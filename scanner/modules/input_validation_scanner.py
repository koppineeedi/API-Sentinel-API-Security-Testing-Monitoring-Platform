from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult

class InputValidationScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "InputValidationScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []

        for ep in context.endpoints:
            # Check for unvalidated path parameters (e.g. {id} without type schema constraints)
            if "{" in ep.path and "}" in ep.path:
                param_names = [p.split("}")[0] for p in ep.path.split("{")[1:]]
                for p_name in param_names:
                    has_schema = False
                    if ep.parameters:
                        for p in ep.parameters:
                            if p.get("name") == p_name and ("schema" in p or "type" in p):
                                has_schema = True
                                break

                    if not has_schema:
                        results.append(ScannerResult(
                            rule_id="SEC-INJ-01",
                            title=f"Unvalidated Path Parameter ({p_name}) in {ep.path}",
                            severity="MEDIUM",
                            confidence="MEDIUM",
                            endpoint=ep.path,
                            http_method=ep.method,
                            description=f"Path parameter '{p_name}' lacks explicit type or regex format constraints in schema.",
                            evidence=f"Path: {ep.path}\nParameter: {p_name}\nSchema Type Constraint: None",
                            impact="Increases vulnerability to SQL injection, path traversal, or type coercion errors.",
                            remediation="Define strict type (integer, UUID) and regex format constraints for all path parameters."
                        ))

        return results
