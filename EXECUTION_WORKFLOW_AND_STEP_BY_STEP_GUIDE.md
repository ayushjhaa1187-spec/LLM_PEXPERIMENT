# EXECUTION WORKFLOW AND STEP-BY-STEP GUIDE
## LLM Government Consulting Prototype - Implementation Plan

**Status**: Ready for Phase 1 Execution  
**Document Date**: January 24, 2026  
**Target**: Production-ready prototype by February 15, 2026  

---

## QUICK START (5 MINUTE OVERVIEW)

### Current State
✅ Architecture designed and documented  
✅ 18 bugs identified with specific fixes  
✅ Multi-agent system prototyped  
✅ Flask backend with auth implemented  

### What's Left
🔧 Fix cost calculation logic (Bugs #6-9)  
🔧 Add validation layer (Bugs #10-12, #17)  
🔧 Fix agent outputs (Bugs #13-16)  
🔧 Build test suites  
🔧 Create investor report template  

---

## PHASE 1: CRITICAL FIXES (Week 1 - Jan 27-31)

### Step 1.1: Fix cost_calculator.py (Bugs #1-9)
**Time**: 3 hours  
**Files**: `src/llm_engine/cost_calculator.py`  

**Tasks**:
```
[] 1.1.1 Replace hard-coded base_costs with calculate_base_costs(project_data)
[] 1.1.2 Replace hard-coded consulting_services ($800k) with scale_to_budget()
[] 1.1.3 Fix agency multiplier (DoD, GSA, NASA) using parametric model
[] 1.1.4 Fix LLM implementation cost scaling
[] 1.1.5 Fix contingency calculation (should be 15% of total)
[] 1.1.6 Fix LLM savings calculation (apply full savings, not 50%)
[] 1.1.7 Fix payback period (remove 0.1 multiplier)
[] 1.1.8 Fix confidence calculation (use weighted average, not arithmetic)
[] 1.1.9 Make confidence deterministic (based on data sources, not random)
```

**Acceptance Criteria**:
- All calculations match expected ranges ±5%
- Confidence scores between 0.60-0.95 (not random)
- Payback period realistic (1-6 months for typical projects)
- All hard-coded values replaced with parameters

**Testing**:
```bash
python -m pytest tests/test_cost_calculator_fixes.py -v
```

### Step 1.2: Fix policy_analyzer.py (Bugs #10-12)
**Time**: 2 hours  
**Files**: `src/llm_engine/policy_analyzer.py`  

**Tasks**:
```
[] 1.2.1 Remove hard-coded CMMC violation - check actual certs first
[] 1.2.2 Remove hard-coded sustainable materials - check project requirements
[] 1.2.3 Add NON_COMPLIANT status (currently only PARTIAL or COMPLIANT)
[] 1.2.4 Add violation counting logic
```

**Testing**:
```bash
python -m pytest tests/test_policy_analyzer_fixes.py -v
```

### Step 1.3: Fix llm_engine/__init__.py (Bugs #13-16)
**Time**: 2 hours  
**Files**: `src/llm_engine/__init__.py`  

**Tasks**:
```
[] 1.3.1 Implement security review signature block in DraftingAgent
[] 1.3.2 Normalize RedTeamAgent scoring to 0-100 scale
[] 1.3.3 Generate scoring from actual risk analysis, not hard-coded value
[] 1.3.4 Make ValidatorAgent check actual outputs, not hard-coded list
[] 1.3.5 Add error handling to all agents (try-except with fallback)
```

**Testing**:
```bash
python -m pytest tests/test_agents_fixes.py -v
```

---

## PHASE 2: VALIDATION & ERROR HANDLING (Week 2 - Feb 3-7)

### Step 2.1: Build ValidationAgent (Bug #17 - Citation Tracking)
**Time**: 4 hours  
**Files**: `src/llm_engine/validator_agent.py` (new file)  

**Requirements**:
```python
class ValidationAgent:
    """Validates outputs and tracks citations."""
    
    def validate_output(self, agent_output: Dict) -> Dict:
        """
        Check that every claim has a source.
        Return validation report with:
        - claims_found: int
        - claims_with_sources: int
        - claims_without_sources: List[str]
        - confidence_score: float
        """
    
    def add_citations(self, output: Dict, sources: Dict) -> Dict:
        """
        Attach [source_id] to every claim in output.
        """
```

**Test Cases**:
```python
def test_validates_all_claims_have_sources():
    """Every claim must cite a source"""
    
def test_sources_are_valid():
    """All cited sources must exist in knowledge base"""
    
def test_confidence_reflects_source_quality():
    """Confidence scores should reflect data quality"""
```

### Step 2.2: Add Error Recovery (Bug #18 - Error Handling)
**Time**: 3 hours  
**Files**: `src/llm_engine/pipeline_orchestrator.py` (new file)  

**Requirements**:
```python
class PipelineOrchestrator:
    """Manages agent execution with error recovery."""
    
    def execute_with_fallback(self, task: Dict) -> Dict:
        """
        Execute task with:
        1. Primary agent execution
        2. Fallback agent if primary fails
        3. Degraded mode with static data if both fail
        4. Error logging and metrics
        """
```

**Fallback Strategy**:
- Research Agent fails → Use cached historical data
- Drafting Agent fails → Use template-based output
- Red Team Agent fails → Use default risk assessment
- Validator Agent fails → Mark as "unvalidated, human review required"

### Step 2.3: Fake Data Sets for Testing
**Time**: 3 hours  
**Files**: `tests/test_data.py` (new file)  

**Requirements**:
```python
FAKE_PROJECTS = [
    {
        'id': 'TEST_001',
        'agency': 'Department of Defense',
        'budget': 2500000,
        'scope': 'medium',
        'duration_months': 18,
        'expected_results': {
            'base_cost': 3375000,  # 2.5M * 1.35 DoD multiplier
            'estimated_cost_with_llm': 2500000,
            'savings': 875000,  # Consulting + labor reductions
            'payback_months': 0.9,
            'roi_percent': 35
        }
    },
    # ... 20+ more test cases covering:
    # - All agency types (DoD, GSA, NASA, VA, etc)
    # - Budget ranges ($100k to $50M)
    # - Scope levels (small, medium, large, enterprise)
    # - Various compliance requirements
]

FAKE_COMPLIANCE_VIOLATIONS = [
    {'policy': 'FAR_52_202_1', 'severity': 'HIGH', 'fixable': True},
    # ... more violations
]
```

---

## PHASE 3: TESTING & DOCUMENTATION (Week 3 - Feb 10-14)

### Step 3.1: Unit Tests (90%+ coverage)
**Time**: 4 hours  
**Command**:
```bash
pytest tests/unit/ -v --cov=src --cov-report=html
```

**Coverage Targets**:
- `cost_calculator.py`: 95%
- `policy_analyzer.py`: 90%
- `llm_engine/__init__.py`: 85%
- Validators: 95%

### Step 3.2: Integration Tests (End-to-End)
**Time**: 3 hours  
**Command**:
```bash
pytest tests/integration/ -v
```

**Test Scenarios**:
```
[] Scenario A: Happy path (all agents succeed)
[] Scenario B: One agent fails, others recover
[] Scenario C: Multiple agents fail, use fallback
[] Scenario D: Cascade failure (degraded mode)
[] Scenario E: Citation tracking accuracy
[] Scenario F: Output validation accuracy
```

### Step 3.3: Create Investor Report Template
**Time**: 4 hours  
**File**: `INVESTOR_REPORT_TEMPLATE.md` (new file)  

**Sections**:
```
1. Executive Summary (1 page)
   - Problem: $100B+ wasted on consulting
   - Solution: LLM-based alternative
   - Impact: 60-80% cost reduction

2. Market Opportunity (2 pages)
   - TAM: $75-100B annually
   - SAM: $10-15B (addressable)
   - SOM: $500M-2B (serviceable)
   - Growth: 3x over 3 years

3. Go-to-Market (1 page)
   - Phase 1: Government agencies (FedRAMP)
   - Phase 2: Private sector
   - Channel: Direct sales + partners

4. Financial Projections (2 pages)
   - Year 1 ARR: $2-5M
   - Year 3 ARR: $25-50M
   - Gross margin: 65-75%
   - Payback: 12-18 months

5. Team & Execution (1 page)
   - Technical founders
   - Government relations leads
   - Go-to-market expertise

6. Use Cases & Proof Points (2 pages)
   - Case Study 1: DoD digital transformation (-$400M)
   - Case Study 2: GSA IT modernization (-$80M)
   - Metrics: Timeline acceleration, cost savings
```

---

## ERROR MINIMIZATION WORKFLOW

### Pre-Execution Checklist
```
[] All input parameters validated
[] Data types correct (no string budgets, dates, etc)
[] Required fields present
[] Historical data available (>5 similar projects)
[] No circular dependencies in calculations
[] All thresholds and multipliers documented
```

### During-Execution Monitoring
```
[] Agent execution time < threshold
[] Output values in expected ranges
[] All citations populated
[] Confidence scores valid (0.0-1.0)
[] Error rates < 5%
```

### Post-Execution Validation
```
[] Results match expected ranges (±10%)
[] Recommendations actionable
[] All sources cited and valid
[] Degradation path clear if needed
[] Audit log complete and timestamped
```

---

## SUCCESS METRICS & KPIs

### Technical
- ✅ 95%+ unit test coverage
- ✅ <100ms per API request (p95)
- ✅ Zero unhandled exceptions
- ✅ 99%+ citation accuracy
- ✅ Cost estimates within ±5% of actual

### Business  
- ✅ Demo-ready by Feb 15
- ✅ All 18 bugs fixed
- ✅ Government compliance certified
- ✅ Investor-ready documentation

---

## DAILY STANDUP TEMPLATE

**Time**: 15 min  
**Format**: What? Why? How?

```
Day: [Date]
Phase: [1/2/3]

Completed Yesterday:
- [Task] - Status: DONE
- [Task] - Status: DONE

Today's Goals:
- [Task] - Owner: [Name] - Est Hours: [#]
- [Task] - Owner: [Name] - Est Hours: [#]

Blockers:
- [Issue] - Resolution: [Plan]

Metrics:
- Bugs fixed: X/18
- Test coverage: Y%
- On track for Feb 15: YES/NO
```

---

## ROLLBACK PLAN

If any phase fails:

1. **Code Rollback**: `git revert [commit]`
2. **Config Rollback**: Restore from `.env.backup`
3. **Data Rollback**: Restore database from snapshot
4. **Communication**: Post-mortem within 24h

---

## NEXT IMMEDIATE ACTIONS

1. ✅ Create comprehensive bug analysis (DONE)
2. 🔄 Fix cost_calculator.py (START NOW)
3. 🔄 Fix policy_analyzer.py (TODAY)
4. ⬜ Add ValidationAgent (TOMORROW)
5. ⬜ Build test suites (NEXT 2 DAYS)
6. ⬜ Create investor report (WEEK 2)
7. ⬜ Final demo prep (WEEK 3)
