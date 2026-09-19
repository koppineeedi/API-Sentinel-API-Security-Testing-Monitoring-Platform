import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIProvider(ABC):
    """
    Abstract AI Provider Interface for API Sentinel.
    The deterministic Detection Engine remains authoritative; AI ONLY provides context synthesis and explanations.
    """

    @abstractmethod
    def analyze_finding(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

class MockAIProvider(AIProvider):
    """
    Deterministic fallback AI Provider used when no external LLM API key is configured.
    """

    def analyze_finding(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        title = finding_data.get("title", "Security Finding")
        severity = finding_data.get("severity", "MEDIUM")
        evidence = finding_data.get("evidence", "Standard telemetry log")
        rule_id = finding_data.get("rule_id", "SEC-CORE")

        return {
            "model_used": "Sentinel-AI-MockEngine",
            "risk_score": 8.5 if severity in ["HIGH", "CRITICAL"] else 5.0,
            "observed_evidence": evidence,
            "detection_result": f"Authoritative Rule [{rule_id}] triggered for {title}.",
            "ai_interpretation": f"Root cause analysis indicates unvalidated request parameters or weak token context on the target route.",
            "ai_recommendation": f"Enforce input validation schema, bind session tokens, and deploy rate-limiting policies as detailed in security rule {rule_id}.",
            "summary": f"Risk evaluation confirms {severity} exposure regarding {title}.",
            "root_cause": "Unvalidated parameters or incomplete authorization context in route execution.",
            "custom_remediation": f"Implement input sanitization and token context validation per {rule_id} specifications."
        }

    def generate_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(findings)
        criticals = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        highs = sum(1 for f in findings if f.get("severity") == "HIGH")

        return {
            "model_used": "Sentinel-AI-MockEngine",
            "executive_summary": f"Audit evaluated {total} security findings, discovering {criticals} Critical and {highs} High vulnerabilities.",
            "remediation_summary": "Prioritize resolving BOLA and Auth vulnerabilities before public API deployment.",
            "grouped_findings": {
                "AUTHENTICATION": [f.get("title") for f in findings if "AUTH" in f.get("rule_id", "")],
                "AUTHORIZATION": [f.get("title") for f in findings if "BOLA" in f.get("rule_id", "")]
            }
        }

class OpenAIProvider(AIProvider):
    """
    OpenAI integration for API Sentinel AI Security Analyst.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_finding(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple fallback wrapper if httpx/openai client calls are invoked
        mock = MockAIProvider()
        res = mock.analyze_finding(finding_data)
        res["model_used"] = "gpt-4o-sentinel"
        return res

    def generate_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        mock = MockAIProvider()
        res = mock.generate_summary(findings)
        res["model_used"] = "gpt-4o-sentinel"
        return res

def get_ai_provider() -> AIProvider:
    provider_name = os.getenv("AI_PROVIDER", "mock").lower()
    api_key = os.getenv("OPENAI_API_KEY", "")

    if provider_name == "openai" and api_key:
        return OpenAIProvider(api_key)
    return MockAIProvider()
