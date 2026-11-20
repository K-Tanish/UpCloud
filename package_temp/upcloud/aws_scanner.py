"""Real AWS resource scanner for UpCloud."""

import boto3
from datetime import datetime, timezone
from typing import List, Dict, Any
from botocore.exceptions import ClientError


def scan_aws_account(region: str = "ap-southeast-2") -> List[Dict[str, Any]]:
    """
    Scan the AWS account for real wasteful resources.
    
    Returns a list of findings in the same format as demo data.
    """
    findings = []
    
    # Initialize AWS clients
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Scan for stopped EC2 instances
        findings.extend(_scan_stopped_instances(ec2, region))
        
        # Scan for unattached EBS volumes
        findings.extend(_scan_unattached_volumes(ec2, region))
        
        # Scan for unused Elastic IPs
        findings.extend(_scan_unused_eips(ec2, region))
        
        # Scan for old snapshots
        findings.extend(_scan_old_snapshots(ec2, region))
        
    except ClientError as e:
        print(f"AWS API Error: {e}")
        # Return empty list if scan fails
        return []
    
    return findings


def _scan_stopped_instances(ec2, region: str) -> List[Dict[str, Any]]:
    """Scan for stopped EC2 instances that are still incurring EBS costs."""
    findings = []
    
    try:
        response = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                instance_type = instance.get('InstanceType', 'unknown')
                
                # Calculate EBS cost (approximate)
                ebs_cost = _calculate_ebs_cost(instance)
                
                # Get instance name from tags
                instance_name = 'Unnamed Instance'
                for tag in instance.get('Tags', []):
                    if tag.get('Key') == 'Name':
                        instance_name = tag.get('Value', instance_name)
                        break
                
                findings.append({
                    'id': f'aws-ec2-stopped-{instance_id}',
                    'provider': 'aws',
                    'category': 'hygiene',
                    'title': f'Stopped EC2 Instance: {instance_name}',
                    'resource_id': instance_id,
                    'resource_type': 'EC2 Instance',
                    'region': region,
                    'description': f'EC2 instance ({instance_type}) has been stopped but still incurring EBS storage costs. Consider terminating if no longer needed.',
                    'risk_level': 'medium',
                    'estimated_monthly_cost_usd': ebs_cost,
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'details': {
                        'instance_type': instance_type,
                        'state': 'stopped',
                        'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None
                    }
                })
    
    except ClientError as e:
        print(f"Error scanning stopped instances: {e}")
    
    return findings


def _scan_unattached_volumes(ec2, region: str) -> List[Dict[str, Any]]:
    """Scan for unattached EBS volumes."""
    findings = []
    
    try:
        response = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        
        for volume in response.get('Volumes', []):
            volume_id = volume.get('VolumeId')
            size_gb = volume.get('Size', 0)
            volume_type = volume.get('VolumeType', 'gp2')
            
            # Calculate monthly cost (approximate)
            monthly_cost = _calculate_volume_cost(size_gb, volume_type)
            
            # Get volume name from tags
            volume_name = 'Unnamed Volume'
            for tag in volume.get('Tags', []):
                if tag.get('Key') == 'Name':
                    volume_name = tag.get('Value', volume_name)
                    break
            
            findings.append({
                'id': f'aws-ebs-unattached-{volume_id}',
                'provider': 'aws',
                'category': 'hygiene',
                'title': f'Unattached EBS Volume: {volume_name}',
                'resource_id': volume_id,
                'resource_type': 'EBS Volume',
                'region': region,
                'description': f'EBS volume ({size_gb}GB {volume_type}) is not attached to any instance. Delete if no longer needed.',
                'risk_level': 'low',
                'estimated_monthly_cost_usd': monthly_cost,
                'detected_at': datetime.now(timezone.utc).isoformat(),
                'details': {
                    'size_gb': size_gb,
                    'volume_type': volume_type,
                    'state': 'available'
                }
            })
    
    except ClientError as e:
        print(f"Error scanning unattached volumes: {e}")
    
    return findings


def _scan_unused_eips(ec2, region: str) -> List[Dict[str, Any]]:
    """Scan for unattached Elastic IPs."""
    findings = []
    
    try:
        response = ec2.describe_addresses()
        
        for address in response.get('Addresses', []):
            # Check if EIP is not associated with an instance
            if not address.get('AssociationId'):
                allocation_id = address.get('AllocationId', 'unknown')
                public_ip = address.get('PublicIp', 'unknown')
                
                # Unused EIPs cost $0.005/hour = ~$3.60/month
                monthly_cost = 3.60
                
                findings.append({
                    'id': f'aws-eip-unused-{allocation_id}',
                    'provider': 'aws',
                    'category': 'hygiene',
                    'title': f'Unused Elastic IP: {public_ip}',
                    'resource_id': allocation_id,
                    'resource_type': 'Elastic IP',
                    'region': region,
                    'description': f'Elastic IP ({public_ip}) is allocated but not associated with any instance. Release to avoid charges.',
                    'risk_level': 'low',
                    'estimated_monthly_cost_usd': monthly_cost,
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'details': {
                        'public_ip': public_ip,
                        'state': 'unattached'
                    }
                })
    
    except ClientError as e:
        print(f"Error scanning unused EIPs: {e}")
    
    return findings


def _scan_old_snapshots(ec2, region: str) -> List[Dict[str, Any]]:
    """Scan for old EBS snapshots (>90 days)."""
    findings = []
    
    try:
        response = ec2.describe_snapshots(OwnerIds=['self'])
        
        now = datetime.now(timezone.utc)
        old_threshold_days = 90
        
        for snapshot in response.get('Snapshots', []):
            snapshot_id = snapshot.get('SnapshotId')
            start_time = snapshot.get('StartTime')
            
            if start_time:
                age_days = (now - start_time).days
                
                if age_days > old_threshold_days:
                    size_gb = snapshot.get('VolumeSize', 0)
                    
                    # Snapshot cost: $0.05 per GB-month
                    monthly_cost = size_gb * 0.05
                    
                    # Get snapshot description
                    description = snapshot.get('Description', 'No description')
                    
                    findings.append({
                        'id': f'aws-snapshot-old-{snapshot_id}',
                        'provider': 'aws',
                        'category': 'hygiene',
                        'title': f'Old EBS Snapshot: {description[:50]}',
                        'resource_id': snapshot_id,
                        'resource_type': 'EBS Snapshot',
                        'region': region,
                        'description': f'EBS snapshot ({size_gb}GB) is {age_days} days old. Consider deleting if no longer needed for backup.',
                        'risk_level': 'low',
                        'estimated_monthly_cost_usd': monthly_cost,
                        'detected_at': datetime.now(timezone.utc).isoformat(),
                        'details': {
                            'size_gb': size_gb,
                            'age_days': age_days,
                            'start_time': start_time.isoformat()
                        }
                    })
    
    except ClientError as e:
        print(f"Error scanning old snapshots: {e}")
    
    return findings


def _calculate_ebs_cost(instance: Dict[str, Any]) -> float:
    """Calculate approximate monthly EBS cost for an instance."""
    # Simplified calculation: assume 30GB gp2 volume per instance
    # Real implementation would query actual volumes
    # gp2: $0.10 per GB-month
    return 30 * 0.10  # $3.00/month


def _calculate_volume_cost(size_gb: int, volume_type: str) -> float:
    """Calculate monthly cost for EBS volume."""
    # Pricing per GB-month (approximate)
    pricing = {
        'gp2': 0.10,
        'gp3': 0.08,
        'io1': 0.125,
        'io2': 0.125,
        'st1': 0.045,
        'sc1': 0.015,
        'standard': 0.05
    }
    
    price_per_gb = pricing.get(volume_type, 0.10)
    return size_gb * price_per_gb
