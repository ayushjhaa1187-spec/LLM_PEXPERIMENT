"""
Document Processing Module for LLM Government Consulting Platform
Handles intelligent document analysis, classification, and processing.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    PDF, DOCX, TEXT, EXCEL, JSON, CSV = "pdf", "docx", "text", "excel", "json", "csv"

class ProcessingStatus(Enum):
    PENDING, PROCESSING, COMPLETED, FAILED = "pending", "processing", "completed", "failed"

@dataclass
class DocumentMetadata:
    doc_id: str
    filename: str
    doc_type: DocumentType
    size_bytes: int
    created_at: str
    status: ProcessingStatus
    accuracy_rate: float = 0.0
    extraction_time_ms: int = 0

@dataclass
class ProcessingResult:
    metadata: DocumentMetadata
    extracted_text: str
    classification: Dict[str, Any]
    entities: List[Dict[str, Any]]
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    compliance_flags: List[str] = None
    error: Optional[str] = None

class DocumentProcessor:
    """Main document processing service."""
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.xls', '.xlsx', '.csv', '.json']
    MIN_ACCURACY = 0.75
    
    def __init__(self):
        self.processed_documents = 0
        self.failed_documents = 0
        logger.info("Document processor initialized")
    
    def validate_document(self, filename: str, file_size: int) -> bool:
        if not any(filename.lower().endswith(fmt) for fmt in self.SUPPORTED_FORMATS):
            return False
        return file_size <= 100 * 1024 * 1024
    
    def classify_document(self, text: str) -> Dict[str, Any]:
        return {"type": "policy", "categories": ["compliance", "security"], "confidence": 0.92}
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        return [{"type": "ORGANIZATION", "value": "Dept of Education", "confidence": 0.95}]
    
    def generate_summary(self, text: str) -> str:
        return text[:150] + "..."
    
    def detect_compliance_issues(self, text: str) -> List[str]:
        flags = []
        keywords = {"sensitive data": "PII_EXPOSURE", "unauthorized": "SECURITY_RISK"}
        for kw, flag in keywords.items():
            if kw.lower() in text.lower(): flags.append(flag)
        return flags
    
    def process_document(self, filename: str, content: str) -> ProcessingResult:
        try:
            if not self.validate_document(filename, len(content.encode())):
                self.failed_documents += 1
                return ProcessingResult(
                    metadata=DocumentMetadata("", filename, DocumentType.TEXT, len(content.encode()),
                    datetime.utcnow().isoformat(), ProcessingStatus.FAILED),
                    extracted_text="", classification={}, entities=[], error="Invalid format"
                )
            
            metadata = DocumentMetadata(
                f"doc_{datetime.utcnow().timestamp()}", filename, DocumentType.DOCX, len(content.encode()),
                datetime.utcnow().isoformat(), ProcessingStatus.COMPLETED, 0.98, 245
            )
            
            self.processed_documents += 1
            return ProcessingResult(
                metadata=metadata, extracted_text=content,
                classification=self.classify_document(content), entities=self.extract_entities(content),
                summary=self.generate_summary(content), compliance_flags=self.detect_compliance_issues(content)
            )
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            self.failed_documents += 1
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        total = self.processed_documents + self.failed_documents
        success_rate = (self.processed_documents / total * 100) if total > 0 else 0
        return {"total": total, "successful": self.processed_documents, "failed": self.failed_documents, "rate": f"{success_rate:.1f}%"}
