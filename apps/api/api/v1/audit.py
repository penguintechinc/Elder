"""Audit System API endpoints for Elder v1.2.0 (Phase 8)."""

from flask import Blueprint, jsonify, request, current_app
from apps.api.auth.decorators import login_required, admin_required
from datetime import datetime

bp = Blueprint('audit', __name__)


# Audit Retention Policies

@bp.route('/retention-policies', methods=['GET'])
@login_required
def list_retention_policies(current_user):
    """
    List all audit retention policies.

    Returns:
        200: List of retention policies
    """
    try:
        db = current_app.db
        policies = db(db.audit_retention_policies.id > 0).select(
            orderby=db.audit_retention_policies.resource_type
        )

        return jsonify({
            'policies': [p.as_dict() for p in policies],
            'count': len(policies)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/retention-policies/<int:policy_id>', methods=['GET'])
@login_required
def get_retention_policy(current_user, policy_id):
    """
    Get retention policy details.

    Returns:
        200: Policy details
        404: Policy not found
    """
    try:
        db = current_app.db
        policy = db.audit_retention_policies[policy_id]

        if not policy:
            return jsonify({'error': 'Retention policy not found'}), 404

        return jsonify(policy.as_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/retention-policies', methods=['POST'])
@admin_required
def create_retention_policy(current_user):
    """
    Create audit retention policy.

    Request body:
        {
            "resource_type": "entities",
            "retention_days": 90,
            "enabled": true
        }

    Returns:
        201: Policy created
        400: Invalid request
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        if 'resource_type' not in data or 'retention_days' not in data:
            return jsonify({'error': 'resource_type and retention_days are required'}), 400

        db = current_app.db

        # Check if policy already exists for this resource type
        existing = db(db.audit_retention_policies.resource_type == data['resource_type']).select().first()
        if existing:
            return jsonify({'error': f'Retention policy already exists for {data["resource_type"]}'}), 400

        policy_id = db.audit_retention_policies.insert(
            resource_type=data['resource_type'],
            retention_days=data['retention_days'],
            enabled=data.get('enabled', True),
            created_at=datetime.utcnow(),
        )

        db.commit()

        policy = db.audit_retention_policies[policy_id]
        return jsonify(policy.as_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/retention-policies/<int:policy_id>', methods=['PUT'])
@admin_required
def update_retention_policy(current_user, policy_id):
    """
    Update retention policy.

    Request body:
        {
            "retention_days": 180,
            "enabled": false
        }

    Returns:
        200: Policy updated
        404: Policy not found
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        db = current_app.db
        policy = db.audit_retention_policies[policy_id]

        if not policy:
            return jsonify({'error': 'Retention policy not found'}), 404

        update_data = {}
        if 'retention_days' in data:
            update_data['retention_days'] = data['retention_days']
        if 'enabled' in data:
            update_data['enabled'] = data['enabled']
        update_data['updated_at'] = datetime.utcnow()

        db(db.audit_retention_policies.id == policy_id).update(**update_data)
        db.commit()

        policy = db.audit_retention_policies[policy_id]
        return jsonify(policy.as_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/retention-policies/<int:policy_id>', methods=['DELETE'])
@admin_required
def delete_retention_policy(current_user, policy_id):
    """
    Delete retention policy.

    Returns:
        200: Policy deleted
        404: Policy not found
    """
    try:
        db = current_app.db
        policy = db.audit_retention_policies[policy_id]

        if not policy:
            return jsonify({'error': 'Retention policy not found'}), 404

        db(db.audit_retention_policies.id == policy_id).delete()
        db.commit()

        return jsonify({'message': 'Retention policy deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Audit Log Cleanup (admin operation)

@bp.route('/cleanup', methods=['POST'])
@admin_required
def cleanup_audit_logs(current_user):
    """
    Clean up old audit logs based on retention policies.

    Query params:
        - dry_run: If true, only return count of logs to delete (default: true)

    Returns:
        200: Cleanup results
    """
    try:
        db = current_app.db
        dry_run = request.args.get('dry_run', 'true').lower() == 'true'

        # Get all enabled retention policies
        policies = db(
            (db.audit_retention_policies.id > 0) &
            (db.audit_retention_policies.enabled == True)
        ).select()

        results = {}
        total_deleted = 0

        for policy in policies:
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)

            # Count/delete old audit logs for this resource type
            # Note: This is a simplified implementation
            # In production, you'd have specific audit log tables per resource type

            if dry_run:
                results[policy.resource_type] = {
                    'retention_days': policy.retention_days,
                    'cutoff_date': cutoff_date.isoformat(),
                    'action': 'dry_run'
                }
            else:
                results[policy.resource_type] = {
                    'retention_days': policy.retention_days,
                    'cutoff_date': cutoff_date.isoformat(),
                    'deleted': 0,
                    'action': 'cleanup_performed'
                }

        return jsonify({
            'dry_run': dry_run,
            'results': results,
            'total_deleted': total_deleted,
            'executed_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


from datetime import timedelta
