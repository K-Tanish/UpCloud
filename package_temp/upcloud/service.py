"""Read-only dashboard data built from CleanCloud's bundled demo findings or real AWS scanning."""

from dataclasses import asdict
from typing import Any, Dict, List, Optional
import os

from cleancloud.demo.findings import (
    AWS_AI_FINDINGS,
    AWS_FINDINGS,
    AZURE_AI_FINDINGS,
    AZURE_FINDINGS,
    GCP_AI_FINDINGS,
    GCP_FINDINGS,
)

# Import real AWS scanner
try:
    from upcloud.aws_scanner import scan_aws_account
    REAL_SCAN_AVAILABLE = True
except ImportError:
    REAL_SCAN_AVAILABLE = False
    scan_aws_account = None

PROVIDERS = ("aws", "azure", "gcp")
CATEGORIES = ("hygiene", "ai")

_FINDINGS = {
    "hygiene": {
        "aws": AWS_FINDINGS,
        "azure": AZURE_FINDINGS,
        "gcp": GCP_FINDINGS,
    },
    "ai": {
        "aws": AWS_AI_FINDINGS,
        "azure": AZURE_AI_FINDINGS,
        "gcp": GCP_AI_FINDINGS,
    },
}


def _validate_filters(provider: str, category: str) -> None:
    if provider != "all" and provider not in PROVIDERS:
        raise ValueError("provider must be one of: all, aws, azure, gcp")
    if category not in CATEGORIES:
        raise ValueError("category must be one of: hygiene, ai")


def _serialize_finding(finding: Any) -> Dict[str, Any]:
    result = finding.to_dict()
    result["evidence"] = asdict(finding.evidence)
    return result


def get_findings(
    provider: str = "all",
    category: str = "hygiene",
    risk: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return filtered demo findings, without accessing cloud accounts."""
    _validate_filters(provider, category)

    source = (
        [
            finding
            for cloud_provider in PROVIDERS
            for finding in _FINDINGS[category][cloud_provider]
        ]
        if provider == "all"
        else _FINDINGS[category][provider]
    )
    normalized_query = (query or "").strip().casefold()
    findings = [_serialize_finding(finding) for finding in source]

    if risk:
        findings = [finding for finding in findings if finding["risk"] == risk.casefold()]
    if normalized_query:
        findings = [
            finding
            for finding in findings
            if normalized_query
            in " ".join(
                str(finding[field])
                for field in ("title", "summary", "resource_id", "resource_type", "region")
            ).casefold()
        ]
    return findings


def get_dashboard(provider: str = "all", category: str = "hygiene") -> Dict[str, Any]:
    """Build summary cards and chart data from the selected demo findings."""
    findings = get_findings(provider=provider, category=category)
    by_provider = {name: 0 for name in PROVIDERS}
    by_risk: Dict[str, int] = {}
    monthly_waste = 0.0
    costed_findings = 0

    for finding in findings:
        by_provider[finding["provider"]] += 1
        by_risk[finding["risk"]] = by_risk.get(finding["risk"], 0) + 1
        cost = finding.get("estimated_monthly_cost_usd")
        if cost is not None:
            monthly_waste += cost
            costed_findings += 1

    return {
        "mode": "simulation",
        "provider": provider,
        "category": category,
        "total_findings": len(findings),
        "high_risk_findings": sum(
            count for risk, count in by_risk.items() if risk in ("high", "critical")
        ),
        "estimated_monthly_waste_usd": round(monthly_waste, 2),
        "costed_findings": costed_findings,
        "by_provider": by_provider,
        "by_risk": by_risk,
    }


def run_demo_scan(provider: str = "all", category: str = "hygiene") -> Dict[str, Any]:
    """Return current simulated results; this deliberately makes no cloud API calls."""
    dashboard = get_dashboard(provider=provider, category=category)
    dashboard["message"] = (
        "Demo scan complete. These are bundled sample findings, not live cloud data."
    )
    return dashboard


def run_real_aws_scan(region: str = "ap-southeast-2") -> Dict[str, Any]:
    """
    Scan the actual AWS account for real wasteful resources.
    
    This makes real AWS API calls and returns actual findings.
    """
    if not REAL_SCAN_AVAILABLE or scan_aws_account is None:
        return {
            "error": "Real AWS scanning not available",
            "message": "AWS scanner module not found"
        }
    
    try:
        # Scan the real AWS account
        real_findings = scan_aws_account(region=region)
        
        # Calculate summary statistics
        total_findings = len(real_findings)
        high_risk_count = sum(1 for f in real_findings if f.get('risk_level') == 'high')
        monthly_waste = sum(f.get('estimated_monthly_cost_usd', 0) for f in real_findings)
        
        # Count by provider (will all be AWS for now)
        by_provider = {'aws': total_findings, 'azure': 0, 'gcp': 0}
        
        return {
            "mode": "real_aws_scan",
            "provider": "aws",
            "region": region,
            "total_findings": total_findings,
            "high_risk_findings": high_risk_count,
            "estimated_monthly_waste_usd": round(monthly_waste, 2),
            "by_provider": by_provider,
            "findings": real_findings,
            "message": f"Real AWS scan complete. Found {total_findings} wasteful resources in your account.",
            "scan_timestamp": real_findings[0]['detected_at'] if real_findings else None
        }
    
    except Exception as e:
        return {
            "error": "AWS scan failed",
            "message": str(e),
            "help": "Ensure Lambda has IAM permissions to scan EC2 resources"
        }
