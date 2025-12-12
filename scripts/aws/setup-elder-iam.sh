#!/bin/bash
#
# Elder AWS IAM Setup Script
#
# This script creates an IAM user with read-only permissions for Elder
# AWS Discovery. It supports both single-account and organization-level
# discovery configurations.
#
# Usage:
#   ./setup-elder-iam.sh [OPTIONS]
#
# Options:
#   -s, --scope SCOPE     Scope of discovery: 'account' or 'organization' (default: account)
#   -u, --user NAME       IAM user name (default: elder-discovery)
#   -p, --policy NAME     IAM policy name (default: ElderDiscoveryPolicy)
#   -r, --region REGION   AWS region for operations (default: us-east-1)
#   -o, --output FILE     Output credentials to file (default: stdout)
#   -f, --format FORMAT   Output format: 'env', 'json', or 'text' (default: text)
#   -h, --help            Show this help message
#   --cleanup             Remove existing Elder IAM resources before creating
#   --dry-run             Show what would be created without making changes
#
# Examples:
#   # Basic single-account setup
#   ./setup-elder-iam.sh
#
#   # Organization-level setup with custom user name
#   ./setup-elder-iam.sh --scope organization --user elder-org-discovery
#
#   # Output credentials to .env file
#   ./setup-elder-iam.sh --output .env --format env
#
#   # Dry run to preview changes
#   ./setup-elder-iam.sh --dry-run
#
# Requirements:
#   - AWS CLI v2 installed and configured
#   - IAM permissions to create users, policies, and access keys
#
# Created by: Elder Platform (Penguin Tech Inc)
# Documentation: https://github.com/penguintechinc/Elder
#

set -euo pipefail

# Script directory (for finding policy files)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
SCOPE="account"
USER_NAME="elder-discovery"
POLICY_NAME="ElderDiscoveryPolicy"
REGION="us-east-1"
OUTPUT_FILE=""
OUTPUT_FORMAT="text"
CLEANUP=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_header() {
    echo ""
    echo -e "${BOLD}$1${NC}"
    echo "$(printf '=%.0s' {1..60})"
}

# Show help
show_help() {
    head -50 "$0" | grep -E '^#' | sed 's/^# \?//'
    exit 0
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--scope)
                SCOPE="$2"
                shift 2
                ;;
            -u|--user)
                USER_NAME="$2"
                shift 2
                ;;
            -p|--policy)
                POLICY_NAME="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Validate scope
    if [[ "$SCOPE" != "account" && "$SCOPE" != "organization" ]]; then
        log_error "Invalid scope: $SCOPE. Must be 'account' or 'organization'"
        exit 1
    fi

    # Validate output format
    if [[ "$OUTPUT_FORMAT" != "env" && "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "text" ]]; then
        log_error "Invalid format: $OUTPUT_FORMAT. Must be 'env', 'json', or 'text'"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_header "Checking Prerequisites"

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        log_info "Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    log_success "AWS CLI found: $(aws --version | head -1)"

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid."
        log_info "Run 'aws configure' to set up credentials."
        exit 1
    fi

    CALLER_IDENTITY=$(aws sts get-caller-identity --output json)
    ACCOUNT_ID=$(echo "$CALLER_IDENTITY" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
    CALLER_ARN=$(echo "$CALLER_IDENTITY" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
    log_success "Authenticated as: $CALLER_ARN"
    log_info "Account ID: $ACCOUNT_ID"

    # Check policy file exists
    if [[ "$SCOPE" == "organization" ]]; then
        POLICY_FILE="$SCRIPT_DIR/elder-discovery-policy-org.json"
    else
        POLICY_FILE="$SCRIPT_DIR/elder-discovery-policy.json"
    fi

    if [[ ! -f "$POLICY_FILE" ]]; then
        log_error "Policy file not found: $POLICY_FILE"
        exit 1
    fi
    log_success "Policy file found: $POLICY_FILE"
}

# Cleanup existing resources
cleanup_resources() {
    log_header "Cleaning Up Existing Resources"

    # Check if user exists
    if aws iam get-user --user-name "$USER_NAME" &> /dev/null; then
        log_warning "Found existing user: $USER_NAME"

        if [[ "$DRY_RUN" == true ]]; then
            log_info "[DRY-RUN] Would delete user: $USER_NAME"
        else
            # Delete access keys
            ACCESS_KEYS=$(aws iam list-access-keys --user-name "$USER_NAME" --query 'AccessKeyMetadata[].AccessKeyId' --output text 2>/dev/null || true)
            for key in $ACCESS_KEYS; do
                log_info "Deleting access key: $key"
                aws iam delete-access-key --user-name "$USER_NAME" --access-key-id "$key"
            done

            # Detach policies
            ATTACHED_POLICIES=$(aws iam list-attached-user-policies --user-name "$USER_NAME" --query 'AttachedPolicies[].PolicyArn' --output text 2>/dev/null || true)
            for policy_arn in $ATTACHED_POLICIES; do
                log_info "Detaching policy: $policy_arn"
                aws iam detach-user-policy --user-name "$USER_NAME" --policy-arn "$policy_arn"
            done

            # Delete user
            log_info "Deleting user: $USER_NAME"
            aws iam delete-user --user-name "$USER_NAME"
            log_success "User deleted: $USER_NAME"
        fi
    else
        log_info "User does not exist: $USER_NAME"
    fi

    # Check if policy exists
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
    if aws iam get-policy --policy-arn "$POLICY_ARN" &> /dev/null; then
        log_warning "Found existing policy: $POLICY_NAME"

        if [[ "$DRY_RUN" == true ]]; then
            log_info "[DRY-RUN] Would delete policy: $POLICY_NAME"
        else
            # Delete all non-default policy versions
            VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" --query 'Versions[?IsDefaultVersion==`false`].VersionId' --output text 2>/dev/null || true)
            for version in $VERSIONS; do
                log_info "Deleting policy version: $version"
                aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$version"
            done

            # Delete policy
            log_info "Deleting policy: $POLICY_NAME"
            aws iam delete-policy --policy-arn "$POLICY_ARN"
            log_success "Policy deleted: $POLICY_NAME"
        fi
    else
        log_info "Policy does not exist: $POLICY_NAME"
    fi
}

# Create IAM policy
create_policy() {
    log_header "Creating IAM Policy"

    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

    # Check if policy already exists
    if aws iam get-policy --policy-arn "$POLICY_ARN" &> /dev/null; then
        log_warning "Policy already exists: $POLICY_NAME"
        log_info "Use --cleanup to remove existing resources first"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create policy: $POLICY_NAME"
        log_info "[DRY-RUN] Policy file: $POLICY_FILE"
        return 0
    fi

    log_info "Creating policy: $POLICY_NAME"
    log_info "Scope: $SCOPE"

    POLICY_RESULT=$(aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document "file://$POLICY_FILE" \
        --description "Elder AWS Discovery read-only policy ($SCOPE scope)" \
        --output json)

    POLICY_ARN=$(echo "$POLICY_RESULT" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
    log_success "Policy created: $POLICY_ARN"
}

# Create IAM user
create_user() {
    log_header "Creating IAM User"

    # Check if user already exists
    if aws iam get-user --user-name "$USER_NAME" &> /dev/null; then
        log_warning "User already exists: $USER_NAME"
        log_info "Use --cleanup to remove existing resources first"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create user: $USER_NAME"
        return 0
    fi

    log_info "Creating user: $USER_NAME"

    aws iam create-user \
        --user-name "$USER_NAME" \
        --tags "Key=Purpose,Value=ElderDiscovery" "Key=ManagedBy,Value=ElderSetupScript" \
        --output json > /dev/null

    log_success "User created: $USER_NAME"
}

# Attach policy to user
attach_policy() {
    log_header "Attaching Policy to User"

    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would attach policy $POLICY_NAME to user $USER_NAME"
        return 0
    fi

    log_info "Attaching policy to user"

    aws iam attach-user-policy \
        --user-name "$USER_NAME" \
        --policy-arn "$POLICY_ARN"

    log_success "Policy attached to user"
}

# Create access keys
create_access_keys() {
    log_header "Creating Access Keys"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create access keys for user $USER_NAME"
        ACCESS_KEY_ID="AKIAEXAMPLE12345678"
        SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        return 0
    fi

    log_info "Creating access keys for user: $USER_NAME"

    KEY_RESULT=$(aws iam create-access-key \
        --user-name "$USER_NAME" \
        --output json)

    ACCESS_KEY_ID=$(echo "$KEY_RESULT" | grep -o '"AccessKeyId": "[^"]*"' | cut -d'"' -f4)
    SECRET_ACCESS_KEY=$(echo "$KEY_RESULT" | grep -o '"SecretAccessKey": "[^"]*"' | cut -d'"' -f4)

    log_success "Access keys created"
    log_warning "IMPORTANT: Save these credentials securely. The secret key cannot be retrieved again!"
}

# Output credentials
output_credentials() {
    log_header "Elder AWS Discovery Credentials"

    case "$OUTPUT_FORMAT" in
        env)
            CREDENTIALS="# Elder AWS Discovery Configuration
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Scope: $SCOPE

AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY
AWS_DEFAULT_REGION=$REGION
AWS_ENABLED=true"
            ;;
        json)
            CREDENTIALS="{
  \"aws_access_key_id\": \"$ACCESS_KEY_ID\",
  \"aws_secret_access_key\": \"$SECRET_ACCESS_KEY\",
  \"region\": \"$REGION\",
  \"scope\": \"$SCOPE\",
  \"user_name\": \"$USER_NAME\",
  \"generated_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
}"
            ;;
        text)
            CREDENTIALS="
Configuration for Elder AWS Discovery
=====================================

AWS Access Key ID:     $ACCESS_KEY_ID
AWS Secret Access Key: $SECRET_ACCESS_KEY
Region:                $REGION
Scope:                 $SCOPE
IAM User:              $USER_NAME

Add to your Elder .env file:
----------------------------
AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY
AWS_DEFAULT_REGION=$REGION
AWS_ENABLED=true
"
            ;;
    esac

    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$CREDENTIALS" > "$OUTPUT_FILE"
        log_success "Credentials written to: $OUTPUT_FILE"
        if [[ "$OUTPUT_FORMAT" == "env" ]]; then
            chmod 600 "$OUTPUT_FILE"
            log_info "File permissions set to 600 (owner read/write only)"
        fi
    else
        echo ""
        echo "$CREDENTIALS"
    fi
}

# Show next steps
show_next_steps() {
    log_header "Next Steps"

    echo "1. Add the credentials to your Elder configuration:"
    echo "   - Copy the AWS_* variables to your .env file"
    echo "   - Or use: source $OUTPUT_FILE (if you used --output with --format env)"
    echo ""
    echo "2. Verify the connection:"
    echo "   python scripts/validate_aws_connection.py -v -d"
    echo ""
    echo "3. Start using AWS Discovery in Elder:"
    echo "   - Navigate to Discovery > Cloud Providers"
    echo "   - Add a new AWS provider with these credentials"
    echo ""

    if [[ "$SCOPE" == "organization" ]]; then
        echo "4. For organization-level discovery:"
        echo "   - Create ElderDiscoveryRole in each member account"
        echo "   - See: docs/aws-organization-setup.md"
        echo ""
    fi

    log_info "Documentation: https://github.com/penguintechinc/Elder/docs/aws-discovery.md"
}

# Main execution
main() {
    parse_args "$@"

    echo ""
    echo -e "${BOLD}Elder AWS IAM Setup${NC}"
    echo "======================================"
    echo "Scope:       $SCOPE"
    echo "User Name:   $USER_NAME"
    echo "Policy Name: $POLICY_NAME"
    echo "Region:      $REGION"
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}Mode:        DRY-RUN (no changes will be made)${NC}"
    fi
    echo ""

    check_prerequisites

    if [[ "$CLEANUP" == true ]]; then
        cleanup_resources
    fi

    create_policy
    create_user
    attach_policy
    create_access_keys
    output_credentials

    if [[ "$DRY_RUN" != true ]]; then
        show_next_steps
    fi

    log_success "Setup complete!"
}

main "$@"
