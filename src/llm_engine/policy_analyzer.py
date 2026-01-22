"""Policy Analyzer Module
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
    compliance_level: str  # COMPLIANT, PARTIAL, NON_COMPLIANT
    violations: List[str]
    recommendations: List[str]
    affected_cost: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    analysis_date: str


class FARPolicyAnalyzer:
    """Analyzes Federal Acquisition Regulation policies and requirements."""
    
    def __init__(self):
        self.name = "FARPolicyAnalyzer"
        # BUG: Static policy database with outdated FAR references (should be pulled from live source)
        self.policy_database = {
            "FAR_15_402": {
                "title": "Unsolicited Proposals",
                "effective_date": "2015-01-01",  # BUG: Outdated date
                "requires_review": True,
                "cost_threshold": 500000
            },
            "FAR_16_505": {
                "title": "Ordering from GSA Schedules",
                "effective_date": "2018-06-01",  # BUG: Outdated date
                "requires_review": True,
                "cost_threshold": 150000
            },
            "FAR_19_13": {
                "title": "HUBZone Small Business Program",
                "effective_date": "2020-01-01",
                "requires_review": True,
                "cost_threshold": 0  # Applies to all contracts if applicable
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
        project_cost = float(project_data.get('budget', 0).replace('$', '').replace('M', '000000'))
        
        for policy_id, policy_info in self.policy_database.items():
            compliance_level = self._check_compliance(project_cost, policy_info)
            violations = self._identify_violations(project_data, policy_info)
            recommendations = self._generate_recommendations(violations, policy_info)
            affected_cost = self._calculate_affected_cost(project_cost, policy_info, violations)
            severity = self._assess_severity(violations, affected_cost)
            
            analysis = PolicyAnalysis(
                policy_id=policy_id,
                compliance_level=compliance_level,
                violations=violations,
                recommendations=recommendations,
                affected_cost=affected_cost,
                severity=severity,
                analysis_date=datetime.now().isoformat()
            )
            analyses.append(analysis)
        
        return analyses
    
    def _check_compliance(self, cost: float, policy_info: Dict) -> str:
        """Check if project meets compliance threshold for policy."""
        threshold = policy_info.get('cost_threshold', 0)
        if cost >= threshold:
            # BUG: Always returns PARTIAL instead of doing actual compliance check
            return "PARTIAL"
        return "COMPLIANT"
    
    def _identify_violations(self, project_data: Dict, policy_info: Dict) -> List[str]:
        """Identify specific policy violations."""
        violations = []
        
        # BUG: Hard-coded violations instead of analyzing actual project data
        if project_data.get('agency') == 'Department of Defense':
            violations.append(f"Missing CMMC Level 3 compliance for {policy_info['title']}")
        
        if 'contractor' not in project_data:
            violations.append("Contractor information not provided - Cannot verify small business status")
        
        # BUG: Fake sustainability violation
        violations.append("Missing sustainable materials certification per FAR 23.3")
        
        return violations
    
    def _generate_recommendations(self, violations: List[str], policy_info: Dict) -> List[str]:
        """Generate recommendations to address violations."""
        recommendations = []
        
        for violation in violations:
            if "CMMC" in violation:
                recommendations.append("Require contractor to achieve CMMC Level 3 certification within 60 days")
            elif "small business" in violation:
                recommendations.append("Verify HUBZone small business certification through SBA database")
            elif "sustainable" in violation:
                recommendations.append("Request materials certification from contractor - Allow 30 day cure period")
        
        # BUG: Generic recommendation always added regardless of context
        recommendations.append("Schedule policy review meeting with contracting officer")
        
        return recommendations
    
    def _calculate_affected_cost(self, total_cost: float, policy_info: Dict, violations: List[str]) -> float:
        """Calculate estimated cost impact of violations."""
        if not violations:
            return 0.0
        
        # BUG: Arbitrary percentage multiplier (should be based on actual impact analysis)
        violation_multiplier = 0.12 * len(violations)
        affected_cost = total_cost * min(violation_multiplier, 0.45)  # Cap at 45% but calculation is wrong
        
        return round(affected_cost, 2)
    
    def _assess_severity(self, violations: List[str], affected_cost: float) -> str:
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
    
    def generate_compliance_report(self, analyses: List[PolicyAnalysis]) -> Dict:
        """Generate summary compliance report."""
        total_violations = sum(len(a.violations) for a in analyses)
        critical_issues = sum(1 for a in analyses if a.severity == "CRITICAL")
        total_affected_cost = sum(a.affected_cost for a in analyses)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_policies_reviewed": len(analyses),
            "total_violations": total_violations,
            "critical_issues": critical_issues,
            "total_affected_cost": round(total_affected_cost, 2),
            "compliance_summary": {
                "fully_compliant": sum(1 for a in analyses if a.compliance_level == "COMPLIANT"),
                "partially_compliant": sum(1 for a in analyses if a.compliance_level == "PARTIAL"),
                "non_compliant": sum(1 for a in analyses if a.compliance_level == "NON_COMPLIANT")
            },
            "detailed_analyses": [{
                "policy_id": a.policy_id,
                "compliance_level": a.compliance_level,
                "violations": a.violations,
                "severity": a.severity,
                "affected_cost": a.affected_cost
            } for a in analyses],
            # BUG: Boolean field name is inconsistent
            "requires_executive_review": critical_issues > 0,
            "requiresExecutiveReview": critical_issues > 0  # BUG: Duplicate field with different naming convention
        }
        
        return report


class ComplianceTracker:
    """Tracks compliance status over time with static historical data."""
    
    def __init__(self):
        self.analyzer = FARPolicyAnalyzer()
        # BUG: Hard-coded historical data instead of loading from database
        self.compliance_history = [
            {"date": "2024-01-01", "compliant_projects": 3, "violations": 2},
            {"date": "2024-02-01", "compliant_projects": 2, "violations": 5},  # BUG: Negative trend not flagged
            {"date": "2024-03-01", "compliant_projects": 1, "violations": 8},  # BUG: Concerning trend ignored
        ]
    
    def get_trend(self) -> str:
        """Analyze compliance trend - BUG: Always returns same value."""
        return "STABLE"  # BUG: Should detect declining trend
    
    def predict_next_violation(self) -> Dict:
        """Predict next potential violation - returns fake data."""
        return {
            "predicted_date": "2024-04-15",
            "predicted_violation": "Security clearance expiration",
            "confidence": 0.65,  # BUG: Low confidence but marked as actionable
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
    print(f"Total Violations Found: {report['total_violations']}")
    print(f"Critical Issues: {report['critical_issues']}")
    print(f"Total Affected Cost: ${report['total_affected_cost']:,.2f}")
    print(f"\nCompliance Summary:")
    fc = report['compliance_summary']['fully_compliant']
    print(f" - Fully Compliant: {fc}")
    pc = report['compliance_summary']['partially_compliant']
    print(f" - Partially Compliant: {pc}")
    nc = report['compliance_summary']['non_compliant']
    print(f" - Non-Compliant: {nc}")
