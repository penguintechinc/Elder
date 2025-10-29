# S3-Compatible Backup Configuration

Elder v1.2.0+ supports automatic backup upload to S3-compatible storage endpoints. This enables secure, off-site backup storage with support for AWS S3, MinIO, Wasabi, Backblaze B2, and other S3-compatible services.

## Supported S3-Compatible Services

- **AWS S3** - Amazon Web Services S3
- **MinIO** - Self-hosted S3-compatible object storage
- **Wasabi** - Hot cloud storage
- **Backblaze B2** - Cloud storage with S3-compatible API
- **DigitalOcean Spaces** - S3-compatible object storage
- **Linode Object Storage** - S3-compatible storage
- **Cloudflare R2** - Zero egress S3-compatible storage
- **Any S3-compatible service** supporting the AWS S3 API

## Configuration

### Environment Variables

Add these environment variables to your `.env` file or docker-compose configuration:

```bash
# Enable S3 backup uploads
BACKUP_S3_ENABLED=true

# S3-compatible endpoint URL (required for non-AWS services)
# Leave empty or unset for AWS S3
# Examples:
#   MinIO: https://minio.example.com
#   Wasabi: https://s3.wasabisys.com
#   Backblaze B2: https://s3.us-west-002.backblazeb2.com
#   DigitalOcean: https://nyc3.digitaloceanspaces.com
BACKUP_S3_ENDPOINT=https://minio.example.com

# S3 bucket name (will be created if doesn't exist)
BACKUP_S3_BUCKET=elder-backups

# AWS region (default: us-east-1)
BACKUP_S3_REGION=us-east-1

# S3 access credentials
BACKUP_S3_ACCESS_KEY=your-access-key-id
BACKUP_S3_SECRET_KEY=your-secret-access-key

# Optional: Object key prefix for organization
# Default: elder/backups/
BACKUP_S3_PREFIX=elder/backups/

# Local backup directory (backups are always saved locally first)
BACKUP_DIR=/var/lib/elder/backups
```

### AWS S3 Configuration

For AWS S3, leave `BACKUP_S3_ENDPOINT` unset or empty:

```bash
BACKUP_S3_ENABLED=true
BACKUP_S3_BUCKET=my-company-elder-backups
BACKUP_S3_REGION=us-east-1
BACKUP_S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
BACKUP_S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
BACKUP_S3_PREFIX=production/elder/backups/
```

### MinIO Configuration

For self-hosted MinIO:

```bash
BACKUP_S3_ENABLED=true
BACKUP_S3_ENDPOINT=https://minio.internal.example.com:9000
BACKUP_S3_BUCKET=elder-backups
BACKUP_S3_REGION=us-east-1
BACKUP_S3_ACCESS_KEY=minioadmin
BACKUP_S3_SECRET_KEY=minioadmin
BACKUP_S3_PREFIX=elder/backups/
```

### Wasabi Configuration

For Wasabi Hot Cloud Storage:

```bash
BACKUP_S3_ENABLED=true
BACKUP_S3_ENDPOINT=https://s3.wasabisys.com
BACKUP_S3_BUCKET=my-elder-backups
BACKUP_S3_REGION=us-east-1
BACKUP_S3_ACCESS_KEY=your-wasabi-access-key
BACKUP_S3_SECRET_KEY=your-wasabi-secret-key
```

### Backblaze B2 Configuration

For Backblaze B2 S3-compatible API:

```bash
BACKUP_S3_ENABLED=true
BACKUP_S3_ENDPOINT=https://s3.us-west-002.backblazeb2.com
BACKUP_S3_BUCKET=elder-backups
BACKUP_S3_REGION=us-west-002
BACKUP_S3_ACCESS_KEY=your-b2-application-key-id
BACKUP_S3_SECRET_KEY=your-b2-application-key
```

## How It Works

1. **Local Backup Creation**: Elder creates a compressed JSON backup locally in `BACKUP_DIR`
2. **S3 Upload**: If `BACKUP_S3_ENABLED=true`, the backup is automatically uploaded to S3
3. **Database Record**: Both local path and S3 URL are stored in the database
4. **Download Fallback**: If local file is deleted but S3 copy exists, download automatically happens on restore
5. **Retention Policy**: Old backups are deleted from both local storage and S3 based on retention settings
6. **Graceful Degradation**: If S3 upload fails, backup continues with local copy only

## Database Schema Changes

The S3 integration adds two new fields to the `backups` table:

```sql
ALTER TABLE backups ADD COLUMN s3_url TEXT;
ALTER TABLE backups ADD COLUMN s3_key TEXT;
```

- `s3_url`: Full URL to the backup in S3 (for reference)
- `s3_key`: S3 object key (used for download/delete operations)

## API Response Example

When a backup is created with S3 enabled:

```json
{
  "success": true,
  "backup_id": 42,
  "filename": "backup_1_20251029_150000.json.gz",
  "file_size": 1048576,
  "record_count": 5000,
  "duration_seconds": 12.5,
  "s3_uploaded": true,
  "s3_url": "https://minio.example.com/elder-backups/elder/backups/backup_1_20251029_150000.json.gz"
}
```

## Security Best Practices

### Access Control

1. **Dedicated IAM User/Policy** (AWS S3):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::elder-backups",
           "arn:aws:s3:::elder-backups/*"
         ]
       }
     ]
   }
   ```

2. **Bucket Versioning**: Enable versioning to protect against accidental deletion
3. **Lifecycle Policies**: Configure automatic deletion of old versions
4. **Encryption**: Enable server-side encryption (SSE-S3 or SSE-KMS)
5. **Access Logging**: Enable S3 access logging for audit trails

### Credentials Management

- **Never commit credentials** to version control
- Use environment variables or secrets management
- Rotate credentials regularly
- Use least-privilege access policies
- Consider using AWS IAM roles (EC2, ECS) instead of access keys when possible

## Troubleshooting

### S3 Upload Failures

Check the API logs for detailed error messages:

```bash
docker-compose logs -f api | grep -i s3
```

Common issues:

1. **Invalid Credentials**:
   - Error: `SignatureDoesNotMatch` or `InvalidAccessKeyId`
   - Solution: Verify `BACKUP_S3_ACCESS_KEY` and `BACKUP_S3_SECRET_KEY`

2. **Bucket Doesn't Exist**:
   - Elder will attempt to create the bucket automatically
   - Ensure credentials have `s3:CreateBucket` permission

3. **Endpoint URL Issues**:
   - Error: `Could not connect to the endpoint URL`
   - Solution: Verify `BACKUP_S3_ENDPOINT` is correct and reachable

4. **Region Mismatch**:
   - Some S3-compatible services require specific region values
   - Check provider documentation for correct region

### Testing S3 Configuration

Test S3 connectivity before running backups:

```bash
# Install AWS CLI
pip install awscli

# Test S3 access
AWS_ACCESS_KEY_ID="your-key" \
AWS_SECRET_ACCESS_KEY="your-secret" \
aws s3 ls s3://elder-backups/ --endpoint-url https://minio.example.com

# Upload test file
echo "test" > test.txt
AWS_ACCESS_KEY_ID="your-key" \
AWS_SECRET_ACCESS_KEY="your-secret" \
aws s3 cp test.txt s3://elder-backups/test.txt --endpoint-url https://minio.example.com
```

## Cost Optimization

### Storage Costs

- **AWS S3**: ~$0.023/GB/month (Standard), ~$0.0125/GB/month (Glacier Instant Retrieval)
- **Wasabi**: $5.99/TB/month (no egress fees)
- **Backblaze B2**: $5/TB/month + $0.01/GB egress
- **MinIO**: Self-hosted, free (infrastructure costs only)

### Best Practices

1. **Compression**: Elder automatically uses gzip compression
2. **Retention Policies**: Configure `retention_days` to automatically delete old backups
3. **Lifecycle Policies**: Use S3 lifecycle rules to transition to cheaper storage classes
4. **Monitoring**: Track backup sizes over time to estimate costs

## Performance Considerations

- **Backup Size**: Large databases (100GB+) may take significant time to upload
- **Network Bandwidth**: Ensure sufficient bandwidth for uploads
- **Compression**: Gzip compression reduces upload size by ~80-90%
- **Parallel Uploads**: Future enhancement for multi-part uploads of large backups

## Monitoring and Alerts

### Success Tracking

Monitor backup status via API:

```bash
# Get backup statistics
curl -X GET http://localhost:5000/api/v1/backup/stats \
  -H "Authorization: Bearer $TOKEN"

# List recent backups with S3 status
curl -X GET http://localhost:5000/api/v1/backup?limit=10 \
  -H "Authorization: Bearer $TOKEN" | jq '.backups[] | {id, filename, s3_url}'
```

### Alerting

Set up monitoring for:

- Failed S3 uploads (backup succeeds locally but S3 upload fails)
- Growing backup sizes
- Missing backups (retention policy too aggressive)
- S3 storage costs

## Migration Guide

### Enabling S3 for Existing Backups

Existing backups will continue to work without S3. New backups will automatically upload to S3 once enabled.

To retroactively upload existing backups to S3:

```python
# Python script example (future enhancement)
from apps.api.services.backup.service import BackupService

service = BackupService(db)

# Get all backups without S3 URL
backups = db(db.backups.s3_url == None).select()

for backup in backups:
    if os.path.exists(backup.file_path):
        result = service._upload_to_s3(backup.file_path, backup.filename)
        if result['success']:
            db(db.backups.id == backup.id).update(
                s3_url=result['s3_url'],
                s3_key=result['s3_key']
            )
db.commit()
```

### Disabling S3

To disable S3 backups:

```bash
BACKUP_S3_ENABLED=false
```

Existing backups in S3 remain accessible. Elder will no longer upload new backups to S3 but will still download from S3 if local files are missing.

## Future Enhancements

- Multi-part uploads for large backups (>5GB)
- S3 bucket encryption configuration
- Backup verification after upload
- Automated backup restore testing
- Support for S3 storage classes (Standard, IA, Glacier)
- Direct S3-to-S3 copy for cross-region replication

---

**Elder v1.2.0+** - Enterprise-Grade Backup Management with S3 Integration

© 2024 Penguin Tech Inc. All rights reserved.
