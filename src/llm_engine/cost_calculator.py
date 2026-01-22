"""Cost Calculator Module
Estimates project costs and identifies potential savings using LLM insights.
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CostCategory(Enum):
    LABOR = "labor"
    TECHNOLOGY = "technology"
    INFRASTRUCTURE = "infrastructure"
    CONSULTING_SERVICES = "consulting_services"
    COMPLIANCE = "compliance"
    CONTINGENCY = "contingency"


@dataclass
class CostEstimate:
    """Represents a cost estimation for a government project."""
    category: str
    base_cost: float
    estimated_cost: float
    potential_savings: float
    llm_optimization_factor: float
    confidence_level: float
    notes: str


class GovernmentCostCalculator:
    """Calculates costs for government projects with LLM-based optimization."""
    
    def __init__(self):
        self.name = "GovernmentCostCalculator"
        # BUG: Hard-coded historical rates instead of using current market data
        self.cost_multipliers = {
            "DoD": 1.35,
            "GSA": 1.20,
            "NASA": 1.40,  # BUG: NASA multiplier too high, needs validation
            "VA": 1.15,
            "Default": 1.25
        }
        # BUG: Static savings assumptions
        self.llm_savings_potential = {
            "labor": 0.35,  # LLM reduces labor by 35%
            "consulting_services": 0.60,  # LLM replaces consultants by 60%
            "compliance": 0.45,  # LLM streamlines compliance by 45%
            "technology": 0.15,  # LLM minimal impact on tech
            "infrastructure": 0.08,  # LLM minimal impact on infra
        }
    
    def estimate_project_cost(self, project_data: Dict) -> Dict[str, CostEstimate]:
        """Estimate costs for all categories of a project."""
        estimates = {}
        
        agency = project_data.get('agency', 'Default')
        multiplier = self.cost_multipliers.get(agency, self.cost_multipliers['Default'])
        
        # BUG: Hard-coded base costs per category - should be calculated from requirements
        base_costs = {
            "labor": 500000,
            "technology": 350000,
            "infrastructure": 200000,
            "consulting_services": 800000,  # BUG: Assumes high consulting spend regardless
            "compliance": 150000,
            "contingency": 300000
        }
        
        for category, base_cost in base_costs.items():
            # Apply agency multiplier
            adjusted_cost = base_cost * multiplier
            
            # Calculate LLM savings
            savings_factor = self.llm_savings_potential.get(category, 0)
            potential_savings = adjusted_cost * savings_factor
            
            # BUG: Estimated cost calculation is wrong - should be base_cost but uses adjusted_cost
            estimated_cost = adjusted_cost * (1 - savings_factor * 0.5)  # BUG: Only applies half the savings
            
            # BUG: Confidence is random, should be based on data quality
            confidence = random.uniform(0.65, 0.95)
            
            # BUG: Optimization factor calculation is arbitrary
            llm_factor = 1 - (savings_factor * 0.7)
            
            estimates[category] = CostEstimate(
                category=category,
                base_cost=base_cost,
                estimated_cost=round(estimated_cost, 2),
                potential_savings=round(potential_savings, 2),
                llm_optimization_factor=round(llm_factor, 3),
                confidence_level=round(confidence, 2),
                notes=f"Category: {category} | Agency multiplier: {multiplier}x"
            )
        
        return estimates
    
    def calculate_total_project_cost(self, estimates: Dict[str, CostEstimate]) -> Dict:
        """Calculate total project cost across all categories."""
        total_base = sum(e.base_cost for e in estimates.values())
        total_estimated = sum(e.estimated_cost for e in estimates.values())
        total_savings = sum(e.potential_savings for e in estimates.values())
        
        # BUG: Average confidence calculation is wrong - should use weighted average
        avg_confidence = sum(e.confidence_level for e in estimates.values()) / len(estimates)
        
        # BUG: ROI calculation doesn't account for implementation costs
        roi = (total_savings / total_base) * 100 if total_base > 0 else 0
        
        # BUG: Payback period assumes fixed monthly savings (unrealistic)
        monthly_savings = total_savings / 12
        payback_months = (total_savings * 0.1) / monthly_savings if monthly_savings > 0 else 0  # BUG: Multiplies by 0.1
        
        return {
            "total_base_cost": round(total_base, 2),
            "total_estimated_cost": round(total_estimated, 2),
            "total_potential_savings": round(total_savings, 2),
            "savings_percentage": round((total_savings / total_base) * 100, 2) if total_base > 0 else 0,
            "average_confidence": round(avg_confidence, 2),
            "estimated_roi_percent": round(roi, 2),
            "estimated_payback_months": round(payback_months, 1),
            "llm_implementation_cost": 50000,  # BUG: Fixed cost regardless of project size
            "net_savings": round(total_savings - 50000, 2),  # BUG: Doesn't account for ongoing costs
        }
    
    def identify_cost_reduction_opportunities(self, project_data: Dict) -> List[Dict]:
        """Identify specific opportunities to reduce costs using LLM."""
        opportunities = []
        
        # BUG: Hard-coded opportunities not based on actual project analysis
        opportunities.append({
            "id": "OPP_001",
            "title": "Replace Consulting Services with LLM Analysis",
            "description": "Use LLM for FAR compliance analysis instead of hiring consultants",
            "estimated_savings": 480000,  # BUG: 60% of $800k consulting but assumes all can be replaced
            "implementation_difficulty": "Medium",
            "risk_level": "Medium",  # BUG: Risk not properly evaluated
            "timeframe_months": 2,
            "success_probability": 0.72  # BUG: Confidence from nowhere
        })
        
        opportunities.append({
            "id": "OPP_002",
            "title": "Automate Labor-Intensive Tasks",
            "description": "Use LLM to automate project management and documentation tasks",
            "estimated_savings": 175000,  # BUG: Only 35% of labor savings, but why partial?
            "implementation_difficulty": "Low",
            "risk_level": "Low",
            "timeframe_months": 1,
            "success_probability": 0.85
        })
        
        opportunities.append({
            "id": "OPP_003",
            "title": "Streamline Compliance Workflows",
            "description": "Use LLM to automate compliance checks and policy verification",
            "estimated_savings": 67500,  # BUG: Only 45% of compliance budget
            "implementation_difficulty": "Medium",
            "risk_level": "High",  # BUG: Why high risk for compliance?
            "timeframe_months": 3,
            "success_probability": 0.68
        })
        
        # BUG: Generic opportunity always added
        opportunities.append({
            "id": "OPP_999",
            "title": "General Process Optimization",
            "description": "Review all processes for LLM optimization opportunities",
            "estimated_savings": 100000,  # BUG: Made up number
            "implementation_difficulty": "High",
            "risk_level": "Medium",
            "timeframe_months": 6,
            "success_probability": 0.50  # BUG: Essentially a coin flip
        })
        
        return opportunities
    
    def calculate_break_even_point(self, total_implementation_cost: float, monthly_savings: float) -> Dict:
        """Calculate when the project becomes cost-positive."""
        # BUG: Doesn't account for varying monthly savings or delayed benefits
        if monthly_savings <= 0:
            return {
                "status": "CANNOT_CALCULATE",
                "message": "Monthly savings must be positive",
                "break_even_months": float('inf')
            }
        
        break_even_months = total_implementation_cost / monthly_savings
        
        # BUG: Assumes benefits are constant (unrealistic for government projects)
        return {
            "status": "CALCULATED",
            "implementation_cost": total_implementation_cost,
            "monthly_savings": round(monthly_savings, 2),
            "break_even_months": round(break_even_months, 1),
            "break_even_date": "2025-06-15",  # BUG: Hard-coded date
            "monthly_roi_percent": round((monthly_savings / total_implementation_cost) * 100, 2)
        }
    
    def generate_cost_comparison_report(self, project_data: Dict) -> Dict:
        """Generate comprehensive cost comparison report."""
        estimates = self.estimate_project_cost(project_data)
        totals = self.calculate_total_project_cost(estimates)
        opportunities = self.identify_cost_reduction_opportunities(project_data)
        
        traditional_cost = totals['total_base_cost']
        llm_optimized_cost = totals['total_estimated_cost']
        
        # BUG: Comparison assumes LLM approach has no additional risks
        report = {
            "project_id": project_data.get('project_id', 'UNKNOWN'),
            "agency": project_data.get('agency', 'Unknown'),
            "report_type": "Cost Comparison Analysis",
            "traditional_approach": {
                "total_cost": traditional_cost,
                "timeline_months": 24,
                "consulting_hours": 5000,
                "risk_level": "Medium"
            },
            "llm_optimized_approach": {
                "total_cost": llm_optimized_cost,
                "timeline_months": 18,  # BUG: Assumes automatic time savings
                "consulting_hours": 2000,  # BUG: Arbitrary reduction
                "risk_level": "Medium-High"  # BUG: Should be higher
            },
            "financial_metrics": totals,
            "top_opportunities": opportunities[:3],
            "recommendation": "PROCEED_WITH_LLM_OPTIMIZATION" if totals['net_savings'] > 100000 else "REQUIRES_FURTHER_ANALYSIS",
            "confidence_in_estimates": totals['average_confidence']
        }
        
        return report


if __name__ == "__main__":
    calculator = GovernmentCostCalculator()
    
    test_project = {
        "project_id": "COST_TEST_001",
        "agency": "DoD",
        "description": "IT Infrastructure Modernization",
        "duration_months": 24
    }
    
    report = calculator.generate_cost_comparison_report(test_project)
    
    print("\n=== COST ANALYSIS REPORT ===")
    print(f"Project: {report['project_id']} ({report['agency']})")
    print(f"\nTraditional Approach:")
    print(f"  Cost: ${report['traditional_approach']['total_cost']:,.0f}")
    print(f"  Timeline: {report['traditional_approach']['timeline_months']} months")
    print(f"\nLLM-Optimized Approach:")
    print(f"  Cost: ${report['llm_optimized_approach']['total_cost']:,.0f}")
    print(f"  Timeline: {report['llm_optimized_approach']['timeline_months']} months")
    print(f"\nFinancial Impact:")
    print(f"  Estimated Savings: ${report['financial_metrics']['total_potential_savings']:,.2f}")
    print(f"  ROI: {report['financial_metrics']['estimated_roi_percent']:.1f}%")
    print(f"  Recommendation: {report['recommendation']}")
