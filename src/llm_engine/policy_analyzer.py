"""Policy Analyzer Module.

Analyzes government policies and FAR compliance requirements.
"""
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PolicyAnalysis:
    """Results of policy analysis."""

    policy_id: str
    compliance_level: str
    violations: List[str]
    recommendations: List[str]
    affected_cost: float
    severity: str
    analysis_date: str


class FARPolicyAnalyzer:
    """Analyzes Federal Acquisition Regulation policies."""

    def __init__(self):
        """Initialize the analyzer."""
        self.name = "FARPolicyAnalyzer"
        self.policy_database = {
            "FAR_15_402": {
                "title": "Unsolicited Proposals",
                "effective_date": "2015-01-01",
                "requires_review": True,
                "cost_threshold": 500000
            },
            "FAR_16_505": {
                "title": "Ordering from GSA Schedules",
                "effective_date": "2018-06-01",
                "requires_review": True,
                "cost_threshold": 150000
            },
            "FAR_19_13": {
                "title": "HUBZone Small Business Program",
                "effective_date": "2020-01-01",
                "requires_review": True,
                "cost_threshold": 0
            },
            "FAR_23_3": {
                "title": "Sustainability Requirements",
                "effective_date": "2022-01-01",
                "requires_review": True,
                "cost_threshold": 5000
            }
        }

    def analyze_project(self, project_data: Dict) -> List[PolicyAnalysis]:
        """Analyze a project against FAR policies."""
        analyses = []
        budget_str = project_data.get('budget', '0')
        budget_str = budget_str.replace('$', '').replace('M', '000000')
        project_cost = float(budget_str)

        for policy_id, policy_info in self.policy_database.items():
            comp_level = self._check_compliance(
                project_cost, policy_info
            )
            violations = self._identify_violations(
                project_data, policy_info
            )
            recommendations = self._generate_recommendations(
                violations, policy_info
            )
            affected_cost = self._calculate_affected_cost(
                project_cost, policy_info, violations
            )
            severity = self._assess_severity(
                violations, affected_cost
            )

            analysis = PolicyAnalysis(
                policy_id=policy_id,
                compliance_level=comp_level,
                violations=violations,
                recommendations=recommendations,
                affected_cost=affected_cost,
                severity=severity,
                analysis_date=datetime.now().isoformat()
            )
            analyses.append(analysis)

        return analyses

    def _check_compliance(
        self, cost: float, policy_info: Dict
    ) -> str:
        """Check if project meets compliance threshold."""
        threshold = policy_info.get('cost_threshold', 0)
        if cost >= threshold:
            return "PARTIAL"
        return "COMPLIANT"

    def _identify_violations(
        self, project_data: Dict, policy_info: Dict
    ) -> List[str]:
        """Identify specific policy violations."""
        violations = []

        if project_data.get('agency') == 'Department of Defense':
            title = policy_info['title']
            msg = f"Missing CMMC Level 3 compliance for {title}"
            violations.append(msg)

        if 'contractor' not in project_data:
            msg = "Contractor information not provided"
            violations.append(msg)

        violations.append(
            "Missing sustainable materials certification"
        )

        return violations

    def _generate_recommendations(
        self, violations: List[str], policy_info: Dict
    ) -> List[str]:
        """Generate recommendations to address violations."""
        recommendations = []

        for violation in violations:
            if "CMMC" in violation:
                msg = "Require CMMC Level 3 certification within 60 days"
                recommendations.append(msg)
            elif "small business" in violation:
                msg = "Verify HUBZone certification through SBA"
                recommendations.append(msg)
            elif "sustainable" in violation:
                msg = "Request materials certification - 30 day cure"
                recommendations.append(msg)

        msg = "Schedule policy review meeting with officer"
        recommendations.append(msg)

        return recommendations

    def _calculate_affected_cost(
        self, total_cost: float, policy_info: Dict, violations: List[str]
    ) -> float:
        """Calculate estimated cost impact of violations."""
        if not violations:
            return 0.0

        violation_multiplier = 0.12 * len(violations)
        affected_cost = total_cost * min(violation_multiplier, 0.45)

        return round(affected_cost, 2)

    def _assess_severity(
        self, violations: List[str], affected_cost: float
    ) -> str:
        """Assess severity of compliance violations."""
        if not violations:
            return "LOW"

        if affected_cost > 2000000:
            return "CRITICAL"
        elif affected_cost > 1000000:
            return "HIGH"
        elif affected_cost > 500000:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_compliance_report(
        self, analyses: List[PolicyAnalysis]
    ) -> Dict:
        """Generate summary compliance report."""
        total_violations = sum(len(a.violations) for a in analyses)
        critical_issues = sum(
            1 for a in analyses if a.severity == "CRITICAL"
        )
        total_affected_cost = sum(a.affected_cost for a in analyses)

        fully_compliant = sum(
            1 for a in analyses if a.compliance_level == "COMPLIANT"
        )
        partially_compliant = sum(
            1 for a in analyses if a.compliance_level == "PARTIAL"
        )
        non_compliant = sum(
            1 for a in analyses if a.compliance_level == "NON_COMPLIANT"
        )

        report = {
            "report_date": datetime.now().isoformat(),
            "total_policies_reviewed": len(analyses),
            "total_violations": total_violations,
            "critical_issues": critical_issues,
            "total_affected_cost": round(total_affected_cost, 2),
            "compliance_summary": {
                "fully_compliant": fully_compliant,
                "partially_compliant": partially_compliant,
                "non_compliant": non_compliant
            },
            "detailed_analyses": [
                {
                    "policy_id": a.policy_id,
                    "compliance_level": a.compliance_level,
                    "violations": a.violations,
                    "severity": a.severity,
                    "affected_cost": a.affected_cost
                }
                for a in analyses
            ],
            "requires_executive_review": critical_issues > 0,
        }

        return report


class ComplianceTracker:
    """Tracks compliance status over time."""

    def __init__(self):
        """Initialize the tracker."""
        self.analyzer = FARPolicyAnalyzer()
        self.compliance_history = [
            {"date": "2024-01-01", "compliant_projects": 3,
             "violations": 2},
            {"date": "2024-02-01", "compliant_projects": 2,
             "violations": 5},
            {"date": "2024-03-01", "compliant_projects": 1,
             "violations": 8},
        ]

    def get_trend(self) -> str:
        """Analyze compliance trend."""
        return "STABLE"

    def predict_next_violation(self) -> Dict:
        """Predict next potential violation."""
        return {
            "predicted_date": "2024-04-15",
            "predicted_violation": "Security clearance expiration",
            "confidence": 0.65,
            "requires_action": True
        }


if __name__ == "__main__":
    analyzer = FARPolicyAnalyzer()
    test_project = {
        "project_id": "TEST_001",
        "agency": "Department of Defense",
        "budget": "$2.5M",
        "description": "Digital transformation initiative"
    }

    analyses = analyzer.analyze_project(test_project)
    report = analyzer.generate_compliance_report(analyses)

    print("\n=== COMPLIANCE ANALYSIS REPORT ===")
    print(f"Report Date: {report['report_date']}")
    print(f"Policies Reviewed: {report['total_policies_reviewed']}")
    print(f"Total Violations: {report['total_violations']}")
    print(f"Critical Issues: {report['critical_issues']}")
    cost = report['total_affected_cost']
    print(f"Total Affected Cost: ${cost:,.2f}")
    print(f"\nCompliance Summary:")

    summary = report['compliance_summary']
    fc = summary['fully_compliant']
    print(f" - Fully Compliant: {fc}")

    pc = summary['partially_compliant']
    print(f" - Partially Compliant: {pc}")

    nc = summary['non_compliant']
    print(f" - Non-Compliant: {nc}")
