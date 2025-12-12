# AWS Discovery Setup Guide

This guide explains how to configure AWS credentials for Elder's cloud discovery feature. Elder can discover and inventory AWS resources including EC2 instances, S3 buckets, RDS databases, Lambda functions, VPCs, and more.

## Authentication Methods

Elder supports three authentication methods for AWS:

| Method | Best For | Security | Rotation |
|--------|----------|----------|----------|
| **OIDC / Web Identity** | CI/CD, Kubernetes, Production | Excellent | Automatic |
| **IAM Roles** | EC2, ECS, Lambda | Excellent | Automatic |
| **Static Credentials** | Development, Testing | Good | Manual (90 days) |

**Recommendation**: Use OIDC for production environments and CI/CD pipelines.

## Quick Start

### Option 1: OIDC / Web Identity (Recommended for Production)

Use OIDC for secure, keyless authentication from GitHub Actions, Kubernetes, or GitLab:

```bash
# GitHub Actions OIDC
./scripts/aws/setup-elder-iam-role.sh --provider github --github-org your-org

# Kubernetes (EKS) OIDC
./scripts/aws/setup-elder-iam-role.sh --provider kubernetes \
  --k8s-namespace elder --k8s-sa elder-discovery \
  --oidc-url oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE
```

### Option 2: Static Credentials (Development/Testing)

Use the provided setup script to create an IAM user with access keys:

```bash
# Basic single-account setup
./scripts/aws/setup-elder-iam.sh

# Organization-level setup (for multi-account environments)
./scripts/aws/setup-elder-iam.sh --scope organization

# Output credentials directly to .env file
./scripts/aws/setup-elder-iam.sh --output .env.aws --format env
```

### Manual Setup

If you prefer to create resources manually, follow the steps in the [Manual IAM Setup](#manual-iam-setup) section below.

## Prerequisites

- AWS CLI v2 installed and configured with admin credentials
- Permissions to create IAM users and policies
- For organization scope: access to the AWS Organizations management account

## Scope Options

### Account-Level Discovery

Best for:
- Single AWS account environments
- Isolated testing or development
- Simple deployments

Permissions include:
- EC2 (instances, volumes, VPCs, subnets, security groups)
- S3 (buckets, tags)
- RDS (instances, clusters)
- Lambda (functions)
- ELB (load balancers)
- IAM (users, roles - read only)

### Organization-Level Discovery

Best for:
- Multi-account AWS Organizations
- Enterprise environments
- Centralized asset management

Additional permissions include:
- Organizations API access (list accounts, describe organization)
- Cross-account role assumption (sts:AssumeRole)
- Account listing and metadata

## Setup Script Options

```
./scripts/aws/setup-elder-iam.sh [OPTIONS]

Options:
  -s, --scope SCOPE     Scope: 'account' or 'organization' (default: account)
  -u, --user NAME       IAM user name (default: elder-discovery)
  -p, --policy NAME     IAM policy name (default: ElderDiscoveryPolicy)
  -r, --region REGION   AWS region (default: us-east-1)
  -o, --output FILE     Output credentials to file
  -f, --format FORMAT   Output format: 'env', 'json', or 'text' (default: text)
  --cleanup             Remove existing Elder IAM resources first
  --dry-run             Preview changes without making them
  -h, --help            Show help message
```

## Usage Examples

### Example 1: Basic Setup

```bash
# Create IAM user with account-level permissions
./scripts/aws/setup-elder-iam.sh

# Output:
# AWS Access Key ID:     AKIA...
# AWS Secret Access Key: wJal...
# Region:                us-east-1
```

### Example 2: Organization Setup with Custom Names

```bash
./scripts/aws/setup-elder-iam.sh \
  --scope organization \
  --user elder-org-scanner \
  --policy ElderOrgDiscoveryPolicy \
  --region us-west-2
```

### Example 3: Export to Environment File

```bash
# Create credentials and save to file
./scripts/aws/setup-elder-iam.sh --output ~/.elder-aws.env --format env

# Source the credentials
source ~/.elder-aws.env

# Verify connection
python scripts/validate_aws_connection.py -v
```

### Example 4: Dry Run (Preview Changes)

```bash
# See what would be created without making changes
./scripts/aws/setup-elder-iam.sh --dry-run --scope organization
```

### Example 5: Cleanup and Recreate

```bash
# Remove existing resources and create fresh ones
./scripts/aws/setup-elder-iam.sh --cleanup
```

## Configuration

After running the setup script, add the credentials to your Elder configuration:

### Option 1: Environment Variables (.env file)

```bash
# Add to your Elder .env file
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJal...
AWS_DEFAULT_REGION=us-east-1
AWS_ENABLED=true
```

### Option 2: Elder UI Configuration

1. Navigate to **Settings > Cloud Providers**
2. Click **Add Provider**
3. Select **AWS**
4. Enter credentials and select regions to scan
5. Click **Test Connection** to verify
6. Save configuration

## Validating the Connection

Use the validation script to verify your setup:

```bash
# Basic validation
python scripts/validate_aws_connection.py

# Verbose output with discovery test
python scripts/validate_aws_connection.py -v -d

# Test specific region
python scripts/validate_aws_connection.py -r us-west-2 -d

# Test specific services only
python scripts/validate_aws_connection.py --services ec2,s3,rds -d
```

Expected output for successful setup:

```
============================================================
Elder AWS Connection Validation
============================================================

[Step 1] Checking boto3 installation
✓ boto3 v1.35.90 installed

[Step 2] Checking credentials configuration
✓ AWS credentials configured via environment variables

[Step 3] Testing AWS authentication (STS)
✓ AWS authentication successful
ℹ Account: 123456789012
ℹ ARN: arn:aws:iam::123456789012:user/elder-discovery

[Step 4] Testing Elder AWSDiscoveryClient
✓ Elder AWSDiscoveryClient connected successfully

[Step 5] Testing service discovery
✓ EC2 (Compute): Access OK (5 resources found)
✓ S3 (Storage): Access OK (12 resources found)
✓ RDS (Database): Access OK (2 resources found)
✓ Lambda (Serverless): Access OK (8 resources found)
✓ VPC (Network): Access OK (3 resources found)

============================================================
Validation Summary
============================================================
✓ All validation checks passed!
ℹ Elder AWS Discovery is ready to use.
```

## Manual IAM Setup

If you need to create resources manually (e.g., in restricted environments):

### Step 1: Create the IAM Policy

```bash
# Download the policy file
# For account-level:
curl -O https://raw.githubusercontent.com/penguintechinc/Elder/main/scripts/aws/elder-discovery-policy.json

# For organization-level:
curl -O https://raw.githubusercontent.com/penguintechinc/Elder/main/scripts/aws/elder-discovery-policy-org.json

# Create the policy
aws iam create-policy \
  --policy-name ElderDiscoveryPolicy \
  --policy-document file://elder-discovery-policy.json \
  --description "Elder AWS Discovery read-only policy"
```

### Step 2: Create the IAM User

```bash
aws iam create-user \
  --user-name elder-discovery \
  --tags Key=Purpose,Value=ElderDiscovery
```

### Step 3: Attach the Policy

```bash
aws iam attach-user-policy \
  --user-name elder-discovery \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/ElderDiscoveryPolicy
```

### Step 4: Create Access Keys

```bash
aws iam create-access-key --user-name elder-discovery
```

## IAM Policy Details

### Account-Level Policy Permissions

| Service | Actions | Purpose |
|---------|---------|---------|
| EC2 | DescribeInstances, DescribeVolumes, DescribeVpcs, DescribeSubnets, DescribeTags, DescribeSecurityGroups, DescribeNetworkInterfaces, DescribeAddresses | Discover compute, storage, and network resources |
| S3 | ListAllMyBuckets, GetBucketLocation, GetBucketTagging | Discover storage buckets |
| RDS | DescribeDBInstances, DescribeDBClusters, ListTagsForResource | Discover database instances |
| Lambda | ListFunctions, ListTags, GetFunction | Discover serverless functions |
| ELB | DescribeLoadBalancers, DescribeTags, DescribeTargetGroups | Discover load balancers |
| IAM | ListUsers, ListRoles, ListGroups, GetUser, GetRole, ListAttachedUserPolicies, ListAttachedRolePolicies | Discover identity resources |
| STS | GetCallerIdentity | Verify authentication |

### Organization-Level Additional Permissions

| Service | Actions | Purpose |
|---------|---------|---------|
| Organizations | ListAccounts, DescribeOrganization, DescribeAccount, ListRoots, ListOrganizationalUnitsForParent, ListAccountsForParent | Enumerate organization structure |
| STS | AssumeRole | Cross-account discovery |

## Cross-Account Discovery (Organization Scope)

For organization-level discovery across multiple AWS accounts:

### Step 1: Create Role in Each Member Account

Create `ElderDiscoveryRole` in each member account with a trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::MANAGEMENT_ACCOUNT_ID:user/elder-discovery"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Attach the account-level policy to this role.

### Step 2: Configure Elder

In Elder's configuration, enable organization scanning and specify the role name:

```bash
AWS_ORGANIZATION_ENABLED=true
AWS_CROSS_ACCOUNT_ROLE=ElderDiscoveryRole
```

## Security Best Practices

1. **Use Least Privilege**: The provided policies include only read permissions needed for discovery
2. **Rotate Access Keys**: Regularly rotate the access keys (recommended: every 90 days)
3. **Enable CloudTrail**: Monitor API calls made by Elder for auditing
4. **Use IAM Roles for EC2**: If running Elder on EC2, use instance roles instead of access keys
5. **Restrict IP Access**: Consider adding IP restrictions to the IAM policy for additional security

## Troubleshooting

### "NoCredentialsError: Unable to locate credentials"

- Verify environment variables are set: `echo $AWS_ACCESS_KEY_ID`
- Check credentials file exists: `cat ~/.aws/credentials`
- If in Docker, ensure credentials are mounted or passed as env vars

### "InvalidClientTokenId: The security token included in the request is invalid"

- Access key may be deactivated or deleted
- Regenerate access keys: `./scripts/aws/setup-elder-iam.sh --cleanup`

### "AccessDenied" for specific services

- The IAM policy may be missing permissions
- Verify policy is attached: `aws iam list-attached-user-policies --user-name elder-discovery`
- Check which actions are denied in CloudTrail

### Organization discovery not finding all accounts

- Verify the user has Organizations permissions
- Check if you're using the management account credentials
- Verify cross-account roles exist in member accounts

## Cleanup

To remove Elder IAM resources:

```bash
# Using the setup script
./scripts/aws/setup-elder-iam.sh --cleanup --dry-run  # Preview
./scripts/aws/setup-elder-iam.sh --cleanup            # Execute

# Or manually
aws iam delete-access-key --user-name elder-discovery --access-key-id AKIA...
aws iam detach-user-policy --user-name elder-discovery --policy-arn arn:aws:iam::...:policy/ElderDiscoveryPolicy
aws iam delete-user --user-name elder-discovery
aws iam delete-policy --policy-arn arn:aws:iam::...:policy/ElderDiscoveryPolicy
```

## Related Documentation

- [AWS Connector Configuration](./aws-connector.md)
- [S3 Backup Configuration](../S3_BACKUP_CONFIGURATION.md)
- [Cloud Discovery Overview](./cloud-discovery.md)
