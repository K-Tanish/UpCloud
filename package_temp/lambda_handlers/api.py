"""AWS Lambda handler for API Gateway requests."""

import json
import os
from typing import Any, Dict, Optional
from urllib.parse import parse_qs

# Import the existing service logic
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from upcloud.service import get_dashboard, get_findings, run_demo_scan, run_real_aws_scan


def _get_query_param(event: Dict[str, Any], key: str, default: str = "") -> str:
    """Extract query parameter from API Gateway event."""
    params = event.get('queryStringParameters') or {}
    return params.get(key, default)


def _cors_headers() -> Dict[str, str]:
    """Return CORS headers for API responses."""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': _cors_headers(),
        'body': json.dumps(body)
    }


def _handle_health(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle /api/health endpoint."""
    return _response(200, {
        'status': 'ok',
        'mode': 'serverless',
        'region': os.environ.get('AWS_REGION', 'unknown'),
        'stage': os.environ.get('STAGE', 'dev')
    })


def _handle_dashboard(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle /api/dashboard endpoint."""
    try:
        provider = _get_query_param(event, 'provider', 'all')
        category = _get_query_param(event, 'category', 'hygiene')
        
        dashboard_data = get_dashboard(provider, category)
        return _response(200, dashboard_data)
    except ValueError as e:
        return _response(400, {'error': str(e)})
    except Exception as e:
        return _response(500, {'error': f'Internal error: {str(e)}'})


def _handle_findings(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle /api/findings endpoint."""
    try:
        provider = _get_query_param(event, 'provider', 'all')
        category = _get_query_param(event, 'category', 'hygiene')
        risk = _get_query_param(event, 'risk', '')
        query = _get_query_param(event, 'q', '')
        
        findings = get_findings(provider, category, risk, query)
        return _response(200, {
            'findings': findings,
            'total': len(findings)
        })
    except ValueError as e:
        return _response(400, {'error': str(e)})
    except Exception as e:
        return _response(500, {'error': f'Internal error: {str(e)}'})


def _handle_scan(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle /api/scan endpoint."""
    try:
        # Parse JSON body
        body = json.loads(event.get('body', '{}'))
        provider = body.get('provider', 'all')
        category = body.get('category', 'hygiene')
        scan_type = body.get('scan_type', 'demo')  # 'demo' or 'real'
        
        if not isinstance(provider, str) or not isinstance(category, str):
            return _response(400, {'error': 'provider and category must be strings'})
        
        # Run real AWS scan if requested
        if scan_type == 'real':
            scan_result = run_real_aws_scan()
            return _response(200, scan_result)
        
        # Otherwise run demo scan
        scan_result = run_demo_scan(provider, category)
        return _response(200, scan_result)
    except json.JSONDecodeError:
        return _response(400, {'error': 'Invalid JSON in request body'})
    except ValueError as e:
        return _response(400, {'error': str(e)})
    except Exception as e:
        return _response(500, {'error': f'Internal error: {str(e)}'})


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for all API Gateway requests.
    
    This function demonstrates:
    - Serverless computing (AWS Lambda)
    - API Gateway integration
    - HTTP request routing
    - JSON data serialization
    - Error handling in cloud functions
    """
    try:
        # Lambda Function URLs use 'requestContext' with 'http'
        # API Gateway uses 'httpMethod' and 'path'
        
        # Detect event type and extract method/path
        if 'requestContext' in event and 'http' in event['requestContext']:
            # Lambda Function URL format
            method = event['requestContext']['http']['method']
            path = event.get('rawPath', '/')  # Function URLs use rawPath
            # Also update queryStringParameters format
            if 'rawQueryString' in event and event['rawQueryString']:
                from urllib.parse import parse_qs
                event['queryStringParameters'] = {k: v[0] for k, v in parse_qs(event['rawQueryString']).items()}
        else:
            # API Gateway format
            method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
        
        # Handle OPTIONS for CORS preflight
        if method == 'OPTIONS':
            return _response(200, {'message': 'OK'})
        
        # Serve static files (solves mixed content HTTP/HTTPS issue)
        if path == '/' or path == '/index.html':
            try:
                with open('/var/task/upcloud/static/index.html', 'r', encoding='utf-8') as f:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'text/html; charset=utf-8',
                            'Cache-Control': 'no-cache'
                        },
                        'body': f.read()
                    }
            except Exception as e:
                print(f"Error serving index.html: {e}")
        
        if path.endswith('.css'):
            try:
                with open(f'/var/task/upcloud/static{path}', 'r', encoding='utf-8') as f:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'text/css; charset=utf-8',
                            'Cache-Control': 'public, max-age=3600'
                        },
                        'body': f.read()
                    }
            except Exception as e:
                print(f"Error serving CSS: {e}")
        
        if path.endswith('.js'):
            try:
                with open(f'/var/task/upcloud/static{path}', 'r', encoding='utf-8') as f:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/javascript; charset=utf-8',
                            'Cache-Control': 'public, max-age=3600'
                        },
                        'body': f.read()
                    }
            except Exception as e:
                print(f"Error serving JS: {e}")
        
        print(f"Lambda invoked: {method} {path}")
        
        # Route to appropriate handler
        if path == '/api/health':
            return _handle_health(event)
        elif path == '/api/dashboard':
            return _handle_dashboard(event)
        elif path == '/api/findings':
            return _handle_findings(event)
        elif path == '/api/scan' and method == 'POST':
            return _handle_scan(event)
        else:
            return _response(404, {'error': 'Not found', 'path': path, 'method': method})
            
    except Exception as e:
        print(f"Unhandled error in Lambda: {str(e)}")
        import traceback
        traceback.print_exc()
        return _response(500, {'error': 'Internal server error', 'details': str(e)})
