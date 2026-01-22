# API Documentation

## Base URL
```
https://api.llm-government-consulting.com/api/v1
```

## Authentication
All API requests require an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Document Processing Endpoints

### 1. Process Document
**Endpoint:** `POST /process-document`

**Description:** Process and classify government documents

**Request Body:**
```json
{
  "document_type": "rfi|rfp|contract|policy",
  "file_content": "base64_encoded_content",
  "file_name": "document.pdf",
  "agency_id": "agency_001"
}
```

**Response:**
```json
{
  "status": "success",
  "document_id": "doc_12345",
  "classification": "RFP",
  "extracted_data": {
    "title": "...",
    "deadline": "2026-03-15",
    "budget_range": "$100K-$500K",
    "key_requirements": [...]
  },
  "processing_time_ms": 2340,
  "confidence_score": 0.95
}
```

### 2. Analyze Compliance
**Endpoint:** `POST /analyze-compliance`

**Description:** Check document compliance with regulations

**Request Body:**
```json
{
  "document_id": "doc_12345",
  "regulation_framework": "FedRAMP|HIPAA|GDPR|NIST",
  "agency_type": "federal|state|local"
}
```

**Response:**
```json
{
  "status": "success",
  "compliance_score": 0.87,
  "issues": [
    {
      "severity": "high|medium|low",
      "category": "security|privacy|accessibility",
      "description": "...",
      "recommendation": "..."
    }
  ],
  "estimated_fix_time_hours": 12
}
```

## Policy & Legal Analysis

### 3. Analyze Policy
**Endpoint:** `POST /analyze-policy`

**Description:** Review and analyze policy documents

**Request Body:**
```json
{
  "policy_id": "policy_001",
  "content": "policy_text",
  "department": "HR|Finance|IT|Operations",
  "version": "1.0"
}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "clarity_score": 0.82,
    "complexity_level": "high",
    "ambiguities": [...],
    "improvement_suggestions": [...]
  },
  "legal_risk_assessment": {
    "risk_level": "low|medium|high",
    "potential_issues": [...]
  }
}
```

### 4. Legal Compliance Check
**Endpoint:** `POST /legal-check`

**Description:** Perform legal compliance verification

**Request Body:**
```json
{
  "document_content": "legal_document_text",
  "jurisdiction": "federal|state",
  "compliance_areas": ["employment", "contract", "privacy"]
}
```

**Response:**
```json
{
  "status": "success",
  "compliant": true,
  "violations": [],
  "recommendations": [],
  "review_required_by": "legal_team"
}
```

## Cost Analysis & ROI

### 5. Calculate Cost Savings
**Endpoint:** `GET /cost-savings`

**Query Parameters:**
- `agency_id` (required): Government agency identifier
- `timeframe` (optional): "month|quarter|year" (default: "year")
- `services` (optional): Comma-separated list of services

**Response:**
```json
{
  "status": "success",
  "agency_id": "agency_001",
  "timeframe": "year",
  "savings_breakdown": {
    "consulting_reduction": "$2.3M",
    "operational_efficiency": "$1.8M",
    "error_reduction": "$0.9M"
  },
  "total_savings": "$5.0M",
  "roi_percentage": 340
}
```

### 6. ROI Calculation
**Endpoint:** `POST /roi-calculation`

**Request Body:**
```json
{
  "agency_id": "agency_001",
  "current_consulting_spend": 15000000,
  "num_staff": 150,
  "document_volume_monthly": 5000,
  "implementation_cost": 500000,
  "monthly_license_fee": 25000
}
```

**Response:**
```json
{
  "status": "success",
  "payback_period_months": 2.5,
  "year_1_roi": 420,
  "year_3_cumulative_savings": "$25.3M",
  "breakeven_analysis": {
    "breakeven_date": "2026-03-15",
    "cumulative_savings_at_breakeven": "$525K"
  }
}
```

## Error Handling

All endpoints return error responses in this format:

```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "error_message": "Detailed error message",
  "request_id": "req_12345",
  "timestamp": "2026-01-22T14:30:00Z"
}
```

### Common Error Codes
- `INVALID_REQUEST`: Malformed request
- `UNAUTHORIZED`: Missing or invalid API key
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error
- `PROCESSING_ERROR`: Document processing failed

## Rate Limits

- **Standard Plan**: 1,000 requests/hour
- **Professional Plan**: 10,000 requests/hour
- **Enterprise Plan**: Unlimited

## Webhook Events

Subscribe to events for asynchronous processing:

```json
{
  "event_type": "document.processed|compliance.analyzed|roi.calculated",
  "timestamp": "2026-01-22T14:30:00Z",
  "data": {...}
}
```

## Code Examples

### Python
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
payload = {
  "document_type": "rfp",
  "file_content": "base64_content",
  "file_name": "rfp.pdf"
}

response = requests.post(
  "https://api.llm-government-consulting.com/api/v1/process-document",
  json=payload,
  headers=headers
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch(
  'https://api.llm-government-consulting.com/api/v1/process-document',
  {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      document_type: 'rfp',
      file_content: 'base64_content',
      file_name: 'rfp.pdf'
    })
  }
);
const data = await response.json();
console.log(data);
```

## Support

For API support and questions:
- Email: api-support@llm-government-consulting.com
- Documentation: https://docs.llm-government-consulting.com
- Status Page: https://status.llm-government-consulting.com
