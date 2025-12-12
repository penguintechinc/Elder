#!/bin/bash
#
# Elder AWS IAM Role Setup Script (OIDC / Web Identity Federation)
#
# This script creates an IAM role with OIDC trust for Elder AWS Discovery.
# Supports multiple OIDC providers for secure, keyless authentication.
#
# Usage:
#   ./setup-elder-iam-role.sh [OPTIONS]
#
# Options:
#   -p, --provider TYPE   OIDC provider type: 'github', 'kubernetes', 'gitlab', 'custom'
#   -r, --role NAME       IAM role name (default: ElderDiscoveryRole)
#   --policy NAME         IAM policy name (default: ElderDiscoveryPolicy)
#   --github-org ORG      GitHub organization name (required for github provider)
#   --github-repo REPO    GitHub repository name (optional, for repo-specific access)
#   --k8s-namespace NS    Kubernetes namespace (required for kubernetes provider)
#   --k8s-sa NAME         Kubernetes service account (required for kubernetes provider)
#   --oidc-url URL        Custom OIDC provider URL (required for custom provider)
#   --oidc-aud AUD        Custom OIDC audience (default: sts.amazonaws.com)
#   --oidc-sub PATTERN    Custom OIDC subject pattern (required for custom provider)
#   --region REGION       AWS region (default: us-east-1)
#   --scope SCOPE         Permission scope: 'account' or 'organization' (default: account)
#   --cleanup             Remove existing role before creating
#   --dry-run             Preview changes without making them
#   -h, --help            Show this help message
#
# Examples:
#   # GitHub Actions OIDC (organization-wide)
#   ./setup-elder-iam-role.sh --provider github --github-org penguintechinc
#
#   # GitHub Actions OIDC (specific repository)
#   ./setup-elder-iam-role.sh --provider github --github-org penguintechinc --github-repo Elder
#
#   # Kubernetes (EKS with IRSA)
#   ./setup-elder-iam-role.sh --provider kubernetes --k8s-namespace elder --k8s-sa elder-discovery
#
#   # Custom OIDC provider
#   ./setup-elder-iam-role.sh --provider custom \
#     --oidc-url token.actions.githubusercontent.com \
#     --oidc-sub "repo:myorg/*"
#
# Requirements:
#   - AWS CLI v2 installed and configured with admin credentials
#   - IAM permissions to create roles, policies, and OIDC providers
#
# OIDC Provider Setup:
#   For GitHub: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments
#   For EKS: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
#
# Created by: Elder Platform (Penguin Tech Inc)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PROVIDER=""
ROLE_NAME="ElderDiscoveryRole"
POLICY_NAME="ElderDiscoveryPolicy"
GITHUB_ORG=""
GITHUB_REPO=""
K8S_NAMESPACE=""
K8S_SA=""
OIDC_URL=""
OIDC_AUD="sts.amazonaws.com"
OIDC_SUB=""
REGION="us-east-1"
SCOPE="account"
CLEANUP=false
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
log_header() { echo ""; echo -e "${BOLD}$1${NC}"; echo "$(printf '=%.0s' {1..60})"; }

show_help() {
    head -60 "$0" | grep -E '^#' | sed 's/^# \?//'
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--provider) PROVIDER="$2"; shift 2 ;;
            -r|--role) ROLE_NAME="$2"; shift 2 ;;
            --policy) POLICY_NAME="$2"; shift 2 ;;
            --github-org) GITHUB_ORG="$2"; shift 2 ;;
            --github-repo) GITHUB_REPO="$2"; shift 2 ;;
            --k8s-namespace) K8S_NAMESPACE="$2"; shift 2 ;;
            --k8s-sa) K8S_SA="$2"; shift 2 ;;
            --oidc-url) OIDC_URL="$2"; shift 2 ;;
            --oidc-aud) OIDC_AUD="$2"; shift 2 ;;
            --oidc-sub) OIDC_SUB="$2"; shift 2 ;;
            --region) REGION="$2"; shift 2 ;;
            --scope) SCOPE="$2"; shift 2 ;;
            --cleanup) CLEANUP=true; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            -h|--help) show_help ;;
            *) log_error "Unknown option: $1"; exit 1 ;;
        esac
    done

    # Validate provider
    if [[ -z "$PROVIDER" ]]; then
        log_error "Provider is required. Use --provider github|kubernetes|gitlab|custom"
        exit 1
    fi

    case "$PROVIDER" in
        github)
            if [[ -z "$GITHUB_ORG" ]]; then
                log_error "GitHub organization is required. Use --github-org"
                exit 1
            fi
            OIDC_URL="token.actions.githubusercontent.com"
            if [[ -n "$GITHUB_REPO" ]]; then
                OIDC_SUB="repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
            else
                OIDC_SUB="repo:${GITHUB_ORG}/*"
            fi
            ;;
        kubernetes)
            if [[ -z "$K8S_NAMESPACE" || -z "$K8S_SA" ]]; then
                log_error "Kubernetes namespace and service account are required"
                log_error "Use --k8s-namespace and --k8s-sa"
                exit 1
            fi
            # OIDC URL must be provided or detected from EKS
            if [[ -z "$OIDC_URL" ]]; then
                log_error "OIDC URL is required for Kubernetes. Use --oidc-url"
                log_info "For EKS, get the OIDC URL from: aws eks describe-cluster --name CLUSTER_NAME --query 'cluster.identity.oidc.issuer' --output text"
                exit 1
            fi
            OIDC_SUB="system:serviceaccount:${K8S_NAMESPACE}:${K8S_SA}"
            ;;
        gitlab)
            if [[ -z "$OIDC_URL" ]]; then
                OIDC_URL="gitlab.com"
            fi
            if [[ -z "$OIDC_SUB" ]]; then
                log_error "OIDC subject pattern is required for GitLab. Use --oidc-sub"
                log_info "Example: project_path:mygroup/myproject:ref_type:branch:ref:main"
                exit 1
            fi
            ;;
        custom)
            if [[ -z "$OIDC_URL" || -z "$OIDC_SUB" ]]; then
                log_error "OIDC URL and subject pattern are required for custom provider"
                exit 1
            fi
            ;;
        *)
            log_error "Invalid provider: $PROVIDER"
            exit 1
            ;;
    esac
}

check_prerequisites() {
    log_header "Checking Prerequisites"

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    log_success "AWS CLI found"

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi

    ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
    log_success "Authenticated to account: $ACCOUNT_ID"
}

check_oidc_provider() {
    log_header "Checking OIDC Provider"

    OIDC_PROVIDER_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${OIDC_URL}"

    if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &> /dev/null; then
        log_success "OIDC provider exists: $OIDC_URL"
    else
        log_warning "OIDC provider not found: $OIDC_URL"

        if [[ "$DRY_RUN" == true ]]; then
            log_info "[DRY-RUN] Would create OIDC provider: $OIDC_URL"
        else
            log_info "Creating OIDC provider..."

            # Get thumbprint for the OIDC provider
            THUMBPRINT=$(echo | openssl s_client -servername "$OIDC_URL" -connect "${OIDC_URL}:443" 2>/dev/null | openssl x509 -fingerprint -sha1 -noout 2>/dev/null | cut -d'=' -f2 | tr -d ':' | tr '[:upper:]' '[:lower:]')

            if [[ -z "$THUMBPRINT" ]]; then
                # Use AWS's known thumbprint for GitHub Actions
                if [[ "$OIDC_URL" == "token.actions.githubusercontent.com" ]]; then
                    THUMBPRINT="6938fd4d98bab03faadb97b34396831e3780aea1"
                else
                    log_error "Could not obtain thumbprint for OIDC provider"
                    exit 1
                fi
            fi

            aws iam create-open-id-connect-provider \
                --url "https://${OIDC_URL}" \
                --client-id-list "sts.amazonaws.com" \
                --thumbprint-list "$THUMBPRINT" \
                --tags Key=Purpose,Value=ElderDiscovery

            log_success "OIDC provider created"
        fi
    fi
}

create_trust_policy() {
    log_header "Creating Trust Policy"

    # Build the trust policy JSON
    TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAssumeRoleWithWebIdentity",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${OIDC_URL}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_URL}:aud": "${OIDC_AUD}"
        },
        "StringLike": {
          "${OIDC_URL}:sub": "${OIDC_SUB}"
        }
      }
    }
  ]
}
EOF
)

    log_info "Trust policy configured for:"
    log_info "  Provider: $OIDC_URL"
    log_info "  Audience: $OIDC_AUD"
    log_info "  Subject:  $OIDC_SUB"
}

create_role() {
    log_header "Creating IAM Role"

    # Check if role exists
    if aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
        if [[ "$CLEANUP" == true ]]; then
            log_warning "Removing existing role: $ROLE_NAME"
            if [[ "$DRY_RUN" != true ]]; then
                # Detach policies
                ATTACHED=$(aws iam list-attached-role-policies --role-name "$ROLE_NAME" --query 'AttachedPolicies[].PolicyArn' --output text 2>/dev/null || true)
                for policy in $ATTACHED; do
                    aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn "$policy"
                done
                aws iam delete-role --role-name "$ROLE_NAME"
            fi
        else
            log_warning "Role already exists: $ROLE_NAME"
            log_info "Use --cleanup to recreate"
            return 0
        fi
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create role: $ROLE_NAME"
        return 0
    fi

    log_info "Creating role: $ROLE_NAME"

    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --description "Elder AWS Discovery role with OIDC trust ($PROVIDER)" \
        --tags Key=Purpose,Value=ElderDiscovery Key=Provider,Value="$PROVIDER" \
        --output json > /dev/null

    log_success "Role created: $ROLE_NAME"
}

attach_policy() {
    log_header "Attaching Policy"

    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

    # Check if policy exists, create if not
    if ! aws iam get-policy --policy-arn "$POLICY_ARN" &> /dev/null; then
        log_info "Creating policy: $POLICY_NAME"

        if [[ "$SCOPE" == "organization" ]]; then
            POLICY_FILE="$SCRIPT_DIR/elder-discovery-policy-org.json"
        else
            POLICY_FILE="$SCRIPT_DIR/elder-discovery-policy.json"
        fi

        if [[ ! -f "$POLICY_FILE" ]]; then
            log_error "Policy file not found: $POLICY_FILE"
            exit 1
        fi

        if [[ "$DRY_RUN" != true ]]; then
            aws iam create-policy \
                --policy-name "$POLICY_NAME" \
                --policy-document "file://$POLICY_FILE" \
                --description "Elder AWS Discovery read-only policy" \
                --output json > /dev/null
        fi
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would attach policy $POLICY_NAME to role $ROLE_NAME"
        return 0
    fi

    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn "$POLICY_ARN"

    log_success "Policy attached to role"
}

output_configuration() {
    log_header "Configuration for Elder"

    ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

    echo ""
    echo "Add these to your Elder configuration:"
    echo "========================================"
    echo ""
    echo "# AWS OIDC Configuration"
    echo "AWS_ROLE_ARN=$ROLE_ARN"
    echo "AWS_DEFAULT_REGION=$REGION"
    echo "AWS_ENABLED=true"
    echo "AWS_USE_WEB_IDENTITY=true"
    echo ""

    case "$PROVIDER" in
        github)
            echo "# GitHub Actions workflow example:"
            echo "# ---------------------------------"
            cat <<'EOF'
# .github/workflows/elder-discovery.yml
permissions:
  id-token: write
  contents: read

jobs:
  discover:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.AWS_ROLE_ARN }}
          aws-region: us-east-2

      - name: Run Elder Discovery
        run: |
          # AWS credentials are now available via OIDC
          python scripts/validate_aws_connection.py -v -d
EOF
            ;;
        kubernetes)
            echo "# Kubernetes deployment example:"
            echo "# -------------------------------"
            cat <<EOF
# elder-deployment.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: $K8S_SA
  namespace: $K8S_NAMESPACE
  annotations:
    eks.amazonaws.com/role-arn: $ROLE_ARN
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      serviceAccountName: $K8S_SA
      containers:
        - name: elder-api
          env:
            - name: AWS_ROLE_ARN
              value: "$ROLE_ARN"
            - name: AWS_WEB_IDENTITY_TOKEN_FILE
              value: /var/run/secrets/eks.amazonaws.com/serviceaccount/token
EOF
            ;;
    esac

    echo ""
    log_info "Role ARN: $ROLE_ARN"
}

main() {
    parse_args "$@"

    echo ""
    echo -e "${BOLD}Elder AWS IAM Role Setup (OIDC)${NC}"
    echo "======================================"
    echo "Provider:    $PROVIDER"
    echo "Role Name:   $ROLE_NAME"
    echo "Policy:      $POLICY_NAME"
    echo "OIDC URL:    $OIDC_URL"
    echo "Subject:     $OIDC_SUB"
    echo "Region:      $REGION"
    echo "Scope:       $SCOPE"
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}Mode:        DRY-RUN${NC}"
    fi
    echo ""

    check_prerequisites
    check_oidc_provider
    create_trust_policy
    create_role
    attach_policy
    output_configuration

    log_success "Setup complete!"
}

main "$@"
