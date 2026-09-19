import enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class ScannerMode(str, enum.Enum):
    PASSIVE = "PASSIVE"
    ACTIVE_AUTHORIZED = "ACTIVE_AUTHORIZED"

@dataclass
class TargetEndpoint:
    path: str
    method: str
    parameters: Optional[List[Dict[str, Any]]] = None
    headers: Optional[Dict[str, Any]] = None

@dataclass
class ScannerContext:
    target_url: str
    mode: ScannerMode
    endpoints: List[TargetEndpoint] = field(default_factory=list)
    auth_token_a: Optional[str] = None
    auth_token_b: Optional[str] = None
    bola_target_id: Optional[str] = None
    max_burst_requests: int = 5
    timeout_seconds: float = 5.0
    headers_to_test: Optional[Dict[str, str]] = None

@dataclass
class ScannerResult:
    rule_id: str
    title: str
    severity: str # INFO, LOW, MEDIUM, HIGH, CRITICAL
    confidence: str # LOW, MEDIUM, HIGH
    endpoint: str
    http_method: str
    description: str
    evidence: str
    impact: str
    remediation: str

class BaseScanner(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        pass
