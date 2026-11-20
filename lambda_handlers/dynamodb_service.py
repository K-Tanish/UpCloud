"""DynamoDB service for storing and retrieving cloud findings.

This module demonstrates:
- NoSQL database operations (AWS DynamoDB)
- Data persistence in cloud
- Query and scan operations
- Serverless data storage
"""

import os
import uuid
from typing import Any, Dict, List, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr


class DynamoDBService:
    """Service for interacting with DynamoDB findings table."""
    
    def __init__(self):
        """Initialize DynamoDB client and table."""
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('DYNAMODB_TABLE', 'upcloud-serverless-findings-dev')
        self.table = self.dynamodb.Table(self.table_name)
    
    def store_finding(self, finding: Dict[str, Any]) -> str:
        """
        Store a finding in DynamoDB.
        
        Args:
            finding: Finding data dictionary
            
        Returns:
            The ID of the stored finding
        """
        # Generate unique ID if not present
        if 'id' not in finding:
            finding['id'] = str(uuid.uuid4())
        
        # Ensure required fields
        if 'provider' not in finding:
            finding['provider'] = 'unknown'
        if 'category' not in finding:
            finding['category'] = 'hygiene'
        
        # Store in DynamoDB
        self.table.put_item(Item=finding)
        
        return finding['id']
    
    def batch_store_findings(self, findings: List[Dict[str, Any]]) -> int:
        """
        Store multiple findings in DynamoDB using batch write.
        
        Demonstrates batch operations for efficiency.
        
        Args:
            findings: List of finding dictionaries
            
        Returns:
            Number of findings stored
        """
        with self.table.batch_writer() as batch:
            for finding in findings:
                if 'id' not in finding:
                    finding['id'] = str(uuid.uuid4())
                if 'provider' not in finding:
                    finding['provider'] = 'unknown'
                if 'category' not in finding:
                    finding['category'] = 'hygiene'
                
                batch.put_item(Item=finding)
        
        return len(findings)
    
    def get_finding(self, finding_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single finding by ID.
        
        Args:
            finding_id: The finding ID
            
        Returns:
            Finding dictionary or None if not found
        """
        response = self.table.get_item(Key={'id': finding_id})
        return response.get('Item')
    
    def query_findings_by_provider(
        self, 
        provider: str, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query findings by provider using Global Secondary Index.
        
        Demonstrates:
        - GSI usage for efficient queries
        - Query operations vs Scan operations
        
        Args:
            provider: Cloud provider (aws, azure, gcp)
            category: Optional category filter (hygiene, ai)
            
        Returns:
            List of findings
        """
        if category:
            response = self.table.query(
                IndexName='ProviderCategoryIndex',
                KeyConditionExpression=Key('provider').eq(provider) & Key('category').eq(category)
            )
        else:
            response = self.table.query(
                IndexName='ProviderCategoryIndex',
                KeyConditionExpression=Key('provider').eq(provider)
            )
        
        return response.get('Items', [])
    
    def scan_all_findings(
        self,
        filter_risk: Optional[str] = None,
        filter_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan all findings with optional filters.
        
        Note: Scan is less efficient than Query but allows flexible filtering.
        
        Args:
            filter_risk: Optional risk level filter
            filter_query: Optional text search query
            
        Returns:
            List of findings
        """
        scan_kwargs = {}
        
        # Build filter expression
        filter_expressions = []
        
        if filter_risk:
            filter_expressions.append(Attr('risk').eq(filter_risk))
        
        if filter_query:
            # Search across multiple fields
            query_lower = filter_query.lower()
            filter_expressions.append(
                Attr('title').contains(query_lower) |
                Attr('summary').contains(query_lower) |
                Attr('resource_id').contains(query_lower)
            )
        
        if filter_expressions:
            filter_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        response = self.table.scan(**scan_kwargs)
        items = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = self.table.scan(**scan_kwargs)
            items.extend(response.get('Items', []))
        
        return items
    
    def delete_finding(self, finding_id: str) -> bool:
        """
        Delete a finding by ID.
        
        Args:
            finding_id: The finding ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            self.table.delete_item(Key={'id': finding_id})
            return True
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored findings.
        
        Returns:
            Dictionary with statistics
        """
        # Scan all items (in production, you'd want to use DynamoDB Streams or maintain counters)
        response = self.table.scan(Select='COUNT')
        total_count = response.get('Count', 0)
        
        # Get a sample to calculate statistics
        sample_response = self.table.scan(Limit=1000)
        items = sample_response.get('Items', [])
        
        by_provider = {}
        by_risk = {}
        total_cost = 0.0
        
        for item in items:
            provider = item.get('provider', 'unknown')
            by_provider[provider] = by_provider.get(provider, 0) + 1
            
            risk = item.get('risk', 'unknown')
            by_risk[risk] = by_risk.get(risk, 0) + 1
            
            cost = item.get('estimated_monthly_cost_usd', 0)
            if cost:
                total_cost += float(cost)
        
        return {
            'total_findings': total_count,
            'by_provider': by_provider,
            'by_risk': by_risk,
            'estimated_monthly_waste_usd': round(total_cost, 2)
        }
