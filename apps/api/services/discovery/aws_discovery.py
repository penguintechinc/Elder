"""AWS cloud discovery client for Elder."""

from datetime import datetime
from typing import Any, Dict, List

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None

from apps.api.services.discovery.base import BaseDiscoveryProvider


class AWSDiscoveryClient(BaseDiscoveryProvider):
    """AWS cloud resource discovery implementation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AWS discovery client.

        Args:
            config: Configuration with AWS credentials and region
                {
                    "provider_type": "aws",
                    "region": "us-east-1",
                    "access_key_id": "AKIA...",
                    "secret_access_key": "...",
                    "services": ["ec2", "rds", "s3", "lambda"]  # optional filter
                }
        """
        super().__init__(config)

        if boto3 is None:
            raise ImportError(
                "boto3 is required for AWS discovery. Install with: pip install boto3"
            )

        self.region = config.get("region", "us-east-1")
        self.services = config.get("services", [])  # Empty = discover all

        # Initialize boto3 session
        session_config = {"region_name": self.region}
        if config.get("access_key_id") and config.get("secret_access_key"):
            session_config["aws_access_key_id"] = config["access_key_id"]
            session_config["aws_secret_access_key"] = config["secret_access_key"]

        self.session = boto3.Session(**session_config)

    def test_connection(self) -> bool:
        """Test AWS connectivity using STS get_caller_identity."""
        try:
            sts = self.session.client("sts")
            sts.get_caller_identity()
            return True
        except (ClientError, BotoCoreError):
            return False

    def get_supported_services(self) -> List[str]:
        """Get list of AWS services supported for discovery."""
        return [
            "ec2",  # EC2 instances
            "rds",  # RDS databases
            "s3",  # S3 buckets
            "lambda",  # Lambda functions
            "vpc",  # VPCs and subnets
            "elb",  # Load balancers
            "ebs",  # EBS volumes
            "iam",  # IAM users and roles
        ]

    def discover_all(self) -> Dict[str, Any]:
        """Discover all AWS resources."""
        start_time = datetime.utcnow()

        results = {
            "compute": [],
            "storage": [],
            "network": [],
            "database": [],
            "serverless": [],
        }

        # Discover each category
        if not self.services or "ec2" in self.services:
            results["compute"].extend(self.discover_compute())

        if not self.services or any(s in self.services for s in ["s3", "ebs"]):
            results["storage"].extend(self.discover_storage())

        if not self.services or any(s in self.services for s in ["vpc", "elb"]):
            results["network"].extend(self.discover_network())

        if not self.services or "rds" in self.services:
            results["database"].extend(self.discover_databases())

        if not self.services or "lambda" in self.services:
            results["serverless"].extend(self.discover_serverless())

        # Calculate totals
        resources_count = sum(len(resources) for resources in results.values())

        return {
            **results,
            "resources_count": resources_count,
            "discovery_time": datetime.utcnow(),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    def discover_compute(self) -> List[Dict[str, Any]]:
        """Discover EC2 instances."""
        resources = []

        try:
            ec2 = self.session.client("ec2")
            response = ec2.describe_instances()

            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resource = self.format_resource(
                        resource_id=instance["InstanceId"],
                        resource_type="ec2_instance",
                        name=self._get_name_from_tags(instance.get("Tags", [])),
                        metadata={
                            "instance_type": instance.get("InstanceType"),
                            "state": instance.get("State", {}).get("Name"),
                            "private_ip": instance.get("PrivateIpAddress"),
                            "public_ip": instance.get("PublicIpAddress"),
                            "vpc_id": instance.get("VpcId"),
                            "subnet_id": instance.get("SubnetId"),
                            "launch_time": (
                                instance.get("LaunchTime").isoformat()
                                if instance.get("LaunchTime")
                                else None
                            ),
                        },
                        region=self.region,
                        tags=self._normalize_tags(instance.get("Tags", [])),
                    )
                    resources.append(resource)

        except (ClientError, BotoCoreError) as e:
            # Log error but continue discovery
            pass

        return resources

    def discover_storage(self) -> List[Dict[str, Any]]:
        """Discover S3 buckets and EBS volumes."""
        resources = []

        # S3 Buckets
        if not self.services or "s3" in self.services:
            try:
                s3 = self.session.client("s3")
                response = s3.list_buckets()

                for bucket in response.get("Buckets", []):
                    bucket_name = bucket["Name"]

                    # Get bucket location
                    try:
                        location = s3.get_bucket_location(Bucket=bucket_name)
                        bucket_region = (
                            location.get("LocationConstraint") or "us-east-1"
                        )
                    except:
                        bucket_region = "unknown"

                    # Get bucket tags
                    try:
                        tags_response = s3.get_bucket_tagging(Bucket=bucket_name)
                        tags = self._normalize_tags(tags_response.get("TagSet", []))
                    except:
                        tags = {}

                    resource = self.format_resource(
                        resource_id=bucket_name,
                        resource_type="s3_bucket",
                        name=bucket_name,
                        metadata={
                            "creation_date": (
                                bucket.get("CreationDate").isoformat()
                                if bucket.get("CreationDate")
                                else None
                            ),
                        },
                        region=bucket_region,
                        tags=tags,
                    )
                    resources.append(resource)

            except (ClientError, BotoCoreError):
                pass

        # EBS Volumes
        if not self.services or "ebs" in self.services:
            try:
                ec2 = self.session.client("ec2")
                response = ec2.describe_volumes()

                for volume in response.get("Volumes", []):
                    resource = self.format_resource(
                        resource_id=volume["VolumeId"],
                        resource_type="ebs_volume",
                        name=self._get_name_from_tags(volume.get("Tags", [])),
                        metadata={
                            "size_gb": volume.get("Size"),
                            "volume_type": volume.get("VolumeType"),
                            "state": volume.get("State"),
                            "iops": volume.get("Iops"),
                            "encrypted": volume.get("Encrypted"),
                            "availability_zone": volume.get("AvailabilityZone"),
                        },
                        region=self.region,
                        tags=self._normalize_tags(volume.get("Tags", [])),
                    )
                    resources.append(resource)

            except (ClientError, BotoCoreError):
                pass

        return resources

    def discover_network(self) -> List[Dict[str, Any]]:
        """Discover VPCs, subnets, and load balancers."""
        resources = []

        # VPCs
        if not self.services or "vpc" in self.services:
            try:
                ec2 = self.session.client("ec2")
                response = ec2.describe_vpcs()

                for vpc in response.get("Vpcs", []):
                    resource = self.format_resource(
                        resource_id=vpc["VpcId"],
                        resource_type="vpc",
                        name=self._get_name_from_tags(vpc.get("Tags", [])),
                        metadata={
                            "cidr_block": vpc.get("CidrBlock"),
                            "state": vpc.get("State"),
                            "is_default": vpc.get("IsDefault"),
                        },
                        region=self.region,
                        tags=self._normalize_tags(vpc.get("Tags", [])),
                    )
                    resources.append(resource)

                # Subnets
                subnets_response = ec2.describe_subnets()
                for subnet in subnets_response.get("Subnets", []):
                    resource = self.format_resource(
                        resource_id=subnet["SubnetId"],
                        resource_type="subnet",
                        name=self._get_name_from_tags(subnet.get("Tags", [])),
                        metadata={
                            "vpc_id": subnet.get("VpcId"),
                            "cidr_block": subnet.get("CidrBlock"),
                            "availability_zone": subnet.get("AvailabilityZone"),
                            "available_ip_addresses": subnet.get(
                                "AvailableIpAddressCount"
                            ),
                        },
                        region=self.region,
                        tags=self._normalize_tags(subnet.get("Tags", [])),
                    )
                    resources.append(resource)

            except (ClientError, BotoCoreError):
                pass

        # Load Balancers (ELBv2)
        if not self.services or "elb" in self.services:
            try:
                elbv2 = self.session.client("elbv2")
                response = elbv2.describe_load_balancers()

                for lb in response.get("LoadBalancers", []):
                    # Get tags for load balancer
                    try:
                        tags_response = elbv2.describe_tags(
                            ResourceArns=[lb["LoadBalancerArn"]]
                        )
                        tags_list = tags_response.get("TagDescriptions", [{}])[0].get(
                            "Tags", []
                        )
                        tags = self._normalize_tags(tags_list)
                    except:
                        tags = {}

                    resource = self.format_resource(
                        resource_id=lb["LoadBalancerArn"],
                        resource_type="load_balancer",
                        name=lb.get("LoadBalancerName"),
                        metadata={
                            "type": lb.get("Type"),
                            "scheme": lb.get("Scheme"),
                            "vpc_id": lb.get("VpcId"),
                            "state": lb.get("State", {}).get("Code"),
                            "dns_name": lb.get("DNSName"),
                        },
                        region=self.region,
                        tags=tags,
                    )
                    resources.append(resource)

            except (ClientError, BotoCoreError):
                pass

        return resources

    def discover_databases(self) -> List[Dict[str, Any]]:
        """Discover RDS databases."""
        resources = []

        try:
            rds = self.session.client("rds")
            response = rds.describe_db_instances()

            for db_instance in response.get("DBInstances", []):
                # Get tags for DB instance
                try:
                    tags_response = rds.list_tags_for_resource(
                        ResourceName=db_instance["DBInstanceArn"]
                    )
                    tags = self._normalize_tags(tags_response.get("TagList", []))
                except:
                    tags = {}

                resource = self.format_resource(
                    resource_id=db_instance["DBInstanceIdentifier"],
                    resource_type="rds_instance",
                    name=db_instance.get("DBInstanceIdentifier"),
                    metadata={
                        "engine": db_instance.get("Engine"),
                        "engine_version": db_instance.get("EngineVersion"),
                        "instance_class": db_instance.get("DBInstanceClass"),
                        "storage_type": db_instance.get("StorageType"),
                        "allocated_storage": db_instance.get("AllocatedStorage"),
                        "status": db_instance.get("DBInstanceStatus"),
                        "endpoint": db_instance.get("Endpoint", {}).get("Address"),
                        "port": db_instance.get("Endpoint", {}).get("Port"),
                        "multi_az": db_instance.get("MultiAZ"),
                        "availability_zone": db_instance.get("AvailabilityZone"),
                    },
                    region=self.region,
                    tags=tags,
                )
                resources.append(resource)

        except (ClientError, BotoCoreError):
            pass

        return resources

    def discover_serverless(self) -> List[Dict[str, Any]]:
        """Discover Lambda functions."""
        resources = []

        try:
            lambda_client = self.session.client("lambda")
            paginator = lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                for function in page.get("Functions", []):
                    function_arn = function["FunctionArn"]

                    # Get tags
                    try:
                        tags_response = lambda_client.list_tags(Resource=function_arn)
                        tags = tags_response.get("Tags", {})
                    except:
                        tags = {}

                    resource = self.format_resource(
                        resource_id=function_arn,
                        resource_type="lambda_function",
                        name=function.get("FunctionName"),
                        metadata={
                            "runtime": function.get("Runtime"),
                            "handler": function.get("Handler"),
                            "memory_size_mb": function.get("MemorySize"),
                            "timeout_seconds": function.get("Timeout"),
                            "last_modified": function.get("LastModified"),
                            "code_size_bytes": function.get("CodeSize"),
                            "vpc_id": function.get("VpcConfig", {}).get("VpcId"),
                        },
                        region=self.region,
                        tags=tags,
                    )
                    resources.append(resource)

        except (ClientError, BotoCoreError):
            pass

        return resources

    def _get_name_from_tags(self, tags: List[Dict[str, str]]) -> str:
        """
        Extract Name tag from AWS tags list.

        Args:
            tags: List of tag dicts with Key/Value

        Returns:
            Name tag value or "Unnamed"
        """
        if not tags:
            return "Unnamed"

        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "Unnamed")

        return "Unnamed"
