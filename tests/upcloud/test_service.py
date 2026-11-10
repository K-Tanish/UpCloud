import unittest

from upcloud.service import get_dashboard, get_findings, run_demo_scan


class DashboardServiceTests(unittest.TestCase):
    def test_dashboard_totals_match_findings(self):
        findings = get_findings()
        dashboard = get_dashboard()

        self.assertEqual(dashboard["mode"], "simulation")
        self.assertEqual(dashboard["total_findings"], len(findings))
        self.assertEqual(
            dashboard["estimated_monthly_waste_usd"],
            round(
                sum(
                    finding["estimated_monthly_cost_usd"]
                    for finding in findings
                    if finding.get("estimated_monthly_cost_usd") is not None
                ),
                2,
            ),
        )

    def test_filters_findings_by_provider_and_category(self):
        findings = get_findings(provider="aws", category="ai")

        self.assertTrue(findings)
        self.assertTrue(all(finding["provider"] == "aws" for finding in findings))
        self.assertTrue(all("SageMaker" in finding["title"] for finding in findings))

    def test_filters_findings_by_risk_and_search(self):
        findings = get_findings(category="ai", risk="critical", query="SageMaker")

        self.assertTrue(findings)
        self.assertTrue(all(finding["risk"] == "critical" for finding in findings))
        self.assertTrue(
            all(
                "sagemaker" in f"{finding['title']} {finding['summary']}".casefold()
                for finding in findings
            )
        )

    def test_invalid_filters_are_reported(self):
        with self.assertRaises(ValueError):
            get_findings(provider="unknown")
        with self.assertRaises(ValueError):
            get_dashboard(category="unknown")

    def test_scan_is_explicitly_simulated(self):
        result = run_demo_scan(provider="azure")

        self.assertEqual(result["provider"], "azure")
        self.assertIn("sample findings", result["message"])


if __name__ == "__main__":
    unittest.main()
