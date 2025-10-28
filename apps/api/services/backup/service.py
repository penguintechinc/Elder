"""Backup & Data Management Service for Elder v1.2.0 (Phase 10)."""

import os
import json
import gzip
import tempfile
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydal import DAL


class BackupService:
    """Service for backup and data management operations."""

    def __init__(self, db: DAL):
        """
        Initialize BackupService.

        Args:
            db: PyDAL database instance
        """
        self.db = db
        self.backup_dir = os.getenv("BACKUP_DIR", "/var/lib/elder/backups")

        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)

    # ===========================
    # Backup Job Management
    # ===========================

    def list_backup_jobs(
        self,
        enabled: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        List all backup jobs.

        Args:
            enabled: Filter by enabled status

        Returns:
            List of backup jobs
        """
        query = self.db.backup_jobs.id > 0

        if enabled is not None:
            query &= self.db.backup_jobs.enabled == enabled

        jobs = self.db(query).select(orderby=self.db.backup_jobs.created_at)

        return [j.as_dict() for j in jobs]

    def get_backup_job(self, job_id: int) -> Dict[str, Any]:
        """
        Get backup job details.

        Args:
            job_id: Backup job ID

        Returns:
            Backup job dictionary

        Raises:
            Exception: If job not found
        """
        job = self.db.backup_jobs[job_id]

        if not job:
            raise Exception(f"Backup job {job_id} not found")

        return job.as_dict()

    def create_backup_job(
        self,
        name: str,
        schedule: Optional[str] = None,
        retention_days: int = 30,
        enabled: bool = True,
        description: Optional[str] = None,
        include_tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new backup job.

        Args:
            name: Job name
            schedule: Cron schedule (optional for manual jobs)
            retention_days: Number of days to retain backups
            enabled: Enable/disable job
            description: Optional description
            include_tables: Tables to include (None = all)
            exclude_tables: Tables to exclude

        Returns:
            Created backup job dictionary
        """
        config = {}
        if include_tables:
            config['include_tables'] = include_tables
        if exclude_tables:
            config['exclude_tables'] = exclude_tables

        job_id = self.db.backup_jobs.insert(
            name=name,
            schedule=schedule,
            retention_days=retention_days,
            enabled=enabled,
            description=description,
            config_json=json.dumps(config) if config else None,
            created_at=datetime.utcnow()
        )

        self.db.commit()

        job = self.db.backup_jobs[job_id]
        return job.as_dict()

    def update_backup_job(
        self,
        job_id: int,
        name: Optional[str] = None,
        schedule: Optional[str] = None,
        retention_days: Optional[int] = None,
        enabled: Optional[bool] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update backup job configuration.

        Args:
            job_id: Backup job ID
            name: New name
            schedule: New schedule
            retention_days: New retention period
            enabled: New enabled status
            description: New description

        Returns:
            Updated backup job dictionary

        Raises:
            Exception: If job not found
        """
        job = self.db.backup_jobs[job_id]

        if not job:
            raise Exception(f"Backup job {job_id} not found")

        update_data = {'updated_at': datetime.utcnow()}

        if name is not None:
            update_data['name'] = name

        if schedule is not None:
            update_data['schedule'] = schedule

        if retention_days is not None:
            update_data['retention_days'] = retention_days

        if enabled is not None:
            update_data['enabled'] = enabled

        if description is not None:
            update_data['description'] = description

        self.db(self.db.backup_jobs.id == job_id).update(**update_data)
        self.db.commit()

        job = self.db.backup_jobs[job_id]
        return job.as_dict()

    def delete_backup_job(self, job_id: int) -> Dict[str, str]:
        """
        Delete backup job.

        Args:
            job_id: Backup job ID

        Returns:
            Success message

        Raises:
            Exception: If job not found
        """
        job = self.db.backup_jobs[job_id]

        if not job:
            raise Exception(f"Backup job {job_id} not found")

        # Delete associated backups
        self.db(self.db.backups.job_id == job_id).delete()

        # Delete job
        self.db(self.db.backup_jobs.id == job_id).delete()
        self.db.commit()

        return {'message': 'Backup job deleted successfully'}

    def run_backup_job(self, job_id: int) -> Dict[str, Any]:
        """
        Manually trigger a backup job.

        Args:
            job_id: Backup job ID

        Returns:
            Backup execution result

        Raises:
            Exception: If job not found
        """
        job = self.db.backup_jobs[job_id]

        if not job:
            raise Exception(f"Backup job {job_id} not found")

        # Update last run time
        self.db(self.db.backup_jobs.id == job_id).update(
            last_run_at=datetime.utcnow()
        )
        self.db.commit()

        # Execute backup
        return self._execute_backup(job)

    # ===========================
    # Backup Execution Methods
    # ===========================

    def _execute_backup(self, job: Any) -> Dict[str, Any]:
        """
        Execute a backup job.

        Args:
            job: Backup job record

        Returns:
            Backup execution result
        """
        try:
            start_time = datetime.utcnow()

            # Get config
            config = {}
            if job.config_json:
                config = json.loads(job.config_json)

            include_tables = config.get('include_tables')
            exclude_tables = config.get('exclude_tables', [])

            # Get all table names
            tables = list(self.db.tables)

            # Filter tables
            if include_tables:
                tables = [t for t in tables if t in include_tables]

            tables = [t for t in tables if t not in exclude_tables]

            # Create backup data structure
            backup_data = {
                'version': '1.2.0',
                'timestamp': start_time.isoformat(),
                'job_id': job.id,
                'job_name': job.name,
                'tables': {}
            }

            total_records = 0

            # Export each table
            for table_name in tables:
                try:
                    table = self.db[table_name]
                    rows = self.db(table.id > 0).select()

                    # Convert rows to dictionaries
                    table_data = [row.as_dict() for row in rows]
                    backup_data['tables'][table_name] = table_data
                    total_records += len(table_data)

                except Exception as e:
                    backup_data['tables'][table_name] = {
                        'error': str(e)
                    }

            # Generate filename
            filename = f"backup_{job.id}_{start_time.strftime('%Y%m%d_%H%M%S')}.json.gz"
            filepath = os.path.join(self.backup_dir, filename)

            # Write compressed backup
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)

            # Get file size
            file_size = os.path.getsize(filepath)

            end_time = datetime.utcnow()
            duration_seconds = (end_time - start_time).total_seconds()

            # Create backup record
            backup_id = self.db.backups.insert(
                job_id=job.id,
                filename=filename,
                file_path=filepath,
                file_size=file_size,
                record_count=total_records,
                status='completed',
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration_seconds
            )

            self.db.commit()

            # Clean up old backups based on retention policy
            self._cleanup_old_backups(job.id, job.retention_days)

            return {
                'success': True,
                'backup_id': backup_id,
                'filename': filename,
                'file_size': file_size,
                'record_count': total_records,
                'duration_seconds': duration_seconds
            }

        except Exception as e:
            # Record failed backup
            backup_id = self.db.backups.insert(
                job_id=job.id,
                status='failed',
                error_message=str(e),
                started_at=datetime.utcnow()
            )
            self.db.commit()

            return {
                'success': False,
                'backup_id': backup_id,
                'error': str(e)
            }

    def _cleanup_old_backups(self, job_id: int, retention_days: int) -> None:
        """
        Clean up old backups based on retention policy.

        Args:
            job_id: Backup job ID
            retention_days: Retention period in days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        old_backups = self.db(
            (self.db.backups.job_id == job_id) &
            (self.db.backups.completed_at < cutoff_date) &
            (self.db.backups.status == 'completed')
        ).select()

        for backup in old_backups:
            # Delete file
            if backup.file_path and os.path.exists(backup.file_path):
                try:
                    os.remove(backup.file_path)
                except Exception:
                    pass

            # Delete record
            self.db(self.db.backups.id == backup.id).delete()

        self.db.commit()

    # ===========================
    # Backup Management Methods
    # ===========================

    def list_backups(
        self,
        job_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all backups.

        Args:
            job_id: Filter by backup job
            limit: Maximum results

        Returns:
            List of backups
        """
        query = self.db.backups.id > 0

        if job_id is not None:
            query &= self.db.backups.job_id == job_id

        backups = self.db(query).select(
            orderby=~self.db.backups.completed_at,
            limitby=(0, limit)
        )

        return [b.as_dict() for b in backups]

    def get_backup(self, backup_id: int) -> Dict[str, Any]:
        """
        Get backup details.

        Args:
            backup_id: Backup ID

        Returns:
            Backup dictionary

        Raises:
            Exception: If backup not found
        """
        backup = self.db.backups[backup_id]

        if not backup:
            raise Exception(f"Backup {backup_id} not found")

        return backup.as_dict()

    def delete_backup(self, backup_id: int) -> Dict[str, str]:
        """
        Delete backup file.

        Args:
            backup_id: Backup ID

        Returns:
            Success message

        Raises:
            Exception: If backup not found
        """
        backup = self.db.backups[backup_id]

        if not backup:
            raise Exception(f"Backup {backup_id} not found")

        # Delete file
        if backup.file_path and os.path.exists(backup.file_path):
            os.remove(backup.file_path)

        # Delete record
        self.db(self.db.backups.id == backup_id).delete()
        self.db.commit()

        return {'message': 'Backup deleted successfully'}

    def get_backup_file_path(self, backup_id: int) -> str:
        """
        Get backup file path for download.

        Args:
            backup_id: Backup ID

        Returns:
            File path

        Raises:
            Exception: If backup not found or file missing
        """
        backup = self.db.backups[backup_id]

        if not backup:
            raise Exception(f"Backup {backup_id} not found")

        if not backup.file_path or not os.path.exists(backup.file_path):
            raise Exception(f"Backup file not found")

        return backup.file_path

    # ===========================
    # Restore Operations
    # ===========================

    def restore_backup(
        self,
        backup_id: int,
        dry_run: bool = False,
        restore_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Restore from backup.

        Args:
            backup_id: Backup ID
            dry_run: Test restore without committing changes
            restore_options: Optional restore configuration

        Returns:
            Restore result

        Raises:
            Exception: If backup not found or restore fails
        """
        backup = self.db.backups[backup_id]

        if not backup:
            raise Exception(f"Backup {backup_id} not found")

        if not backup.file_path or not os.path.exists(backup.file_path):
            raise Exception(f"Backup file not found")

        # Load backup data
        with gzip.open(backup.file_path, 'rt', encoding='utf-8') as f:
            backup_data = json.load(f)

        # Validate backup format
        if 'version' not in backup_data or 'tables' not in backup_data:
            raise Exception("Invalid backup format")

        restore_options = restore_options or {}
        tables_to_restore = restore_options.get('tables', list(backup_data['tables'].keys()))

        restored_counts = {}
        errors = {}

        for table_name in tables_to_restore:
            if table_name not in backup_data['tables']:
                continue

            if isinstance(backup_data['tables'][table_name], dict) and 'error' in backup_data['tables'][table_name]:
                errors[table_name] = backup_data['tables'][table_name]['error']
                continue

            try:
                table_data = backup_data['tables'][table_name]

                if not dry_run:
                    # Clear existing data if requested
                    if restore_options.get('clear_existing', False):
                        self.db(self.db[table_name].id > 0).delete()

                    # Insert records
                    for record in table_data:
                        # Remove id if exists to let DB auto-generate
                        if 'id' in record and restore_options.get('regenerate_ids', True):
                            del record['id']

                        self.db[table_name].insert(**record)

                    self.db.commit()

                restored_counts[table_name] = len(table_data)

            except Exception as e:
                errors[table_name] = str(e)
                if not dry_run:
                    self.db.rollback()

        return {
            'backup_id': backup_id,
            'dry_run': dry_run,
            'restored_tables': len(restored_counts),
            'total_records': sum(restored_counts.values()),
            'restored_counts': restored_counts,
            'errors': errors
        }

    # ===========================
    # Export Operations
    # ===========================

    def export_data(
        self,
        format: str,
        resource_types: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export data to various formats.

        Args:
            format: Export format (json, csv, xml)
            resource_types: Resource types to export
            filters: Optional filters

        Returns:
            Export result with file path

        Raises:
            Exception: If export fails
        """
        if format not in ['json', 'csv', 'xml']:
            raise Exception(f"Unsupported format: {format}")

        # Collect data
        export_data = {}

        for resource_type in resource_types:
            if resource_type == 'entity':
                entities = self.db(self.db.entities.id > 0).select()
                export_data['entities'] = [e.as_dict() for e in entities]

            elif resource_type == 'organization':
                orgs = self.db(self.db.organizations.id > 0).select()
                export_data['organizations'] = [o.as_dict() for o in orgs]

            elif resource_type == 'issue':
                issues = self.db(self.db.issues.id > 0).select()
                export_data['issues'] = [i.as_dict() for i in issues]

        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{timestamp}.{format}"
        filepath = os.path.join(tempfile.gettempdir(), filename)

        # Write export file
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

        elif format == 'csv':
            # CSV export for each resource type
            for resource_type, records in export_data.items():
                if not records:
                    continue

                csv_filename = f"export_{resource_type}_{timestamp}.csv"
                csv_filepath = os.path.join(tempfile.gettempdir(), csv_filename)

                with open(csv_filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

        elif format == 'xml':
            root = ET.Element('export')
            root.set('timestamp', timestamp)

            for resource_type, records in export_data.items():
                type_elem = ET.SubElement(root, resource_type + 's')

                for record in records:
                    record_elem = ET.SubElement(type_elem, resource_type)
                    for key, value in record.items():
                        field_elem = ET.SubElement(record_elem, key)
                        field_elem.text = str(value) if value is not None else ''

            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)

        file_size = os.path.getsize(filepath)

        return {
            'success': True,
            'format': format,
            'filename': filename,
            'filepath': filepath,
            'file_size': file_size,
            'resource_types': resource_types,
            'record_counts': {k: len(v) for k, v in export_data.items()}
        }

    # ===========================
    # Import Operations
    # ===========================

    def import_data(
        self,
        filepath: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Import data from file.

        Args:
            filepath: Path to import file
            dry_run: Test import without committing

        Returns:
            Import result

        Raises:
            Exception: If import fails
        """
        if not os.path.exists(filepath):
            raise Exception(f"Import file not found: {filepath}")

        # Detect format from extension
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                import_data = json.load(f)

        elif filepath.endswith('.json.gz'):
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                import_data = json.load(f)

        else:
            raise Exception("Unsupported file format. Use .json or .json.gz")

        imported_counts = {}
        errors = {}

        # Import each resource type
        for resource_type, records in import_data.items():
            if resource_type in ['version', 'timestamp', 'job_id', 'job_name']:
                continue

            try:
                if not dry_run:
                    for record in records:
                        if isinstance(record, dict) and 'error' not in record:
                            # Remove id to let DB auto-generate
                            if 'id' in record:
                                del record['id']

                            self.db[resource_type].insert(**record)

                    self.db.commit()

                imported_counts[resource_type] = len(records) if isinstance(records, list) else 0

            except Exception as e:
                errors[resource_type] = str(e)
                if not dry_run:
                    self.db.rollback()

        return {
            'dry_run': dry_run,
            'imported_tables': len(imported_counts),
            'total_records': sum(imported_counts.values()),
            'imported_counts': imported_counts,
            'errors': errors
        }

    # ===========================
    # Storage Statistics
    # ===========================

    def get_backup_stats(self) -> Dict[str, Any]:
        """
        Get backup and storage statistics.

        Returns:
            Storage statistics
        """
        total_backups = self.db(self.db.backups.id > 0).count()
        completed_backups = self.db(self.db.backups.status == 'completed').count()
        failed_backups = self.db(self.db.backups.status == 'failed').count()

        # Calculate total size
        backups = self.db(self.db.backups.status == 'completed').select()
        total_size = sum(b.file_size or 0 for b in backups)

        # Get recent backups
        recent = self.db(self.db.backups.id > 0).select(
            orderby=~self.db.backups.completed_at,
            limitby=(0, 5)
        )

        return {
            'total_backups': total_backups,
            'completed_backups': completed_backups,
            'failed_backups': failed_backups,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'backup_directory': self.backup_dir,
            'recent_backups': [b.as_dict() for b in recent]
        }
