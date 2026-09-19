import logging
import asyncio
from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult
from scanner.modules.header_scanner import HeaderScanner
from scanner.modules.info_disclosure_scanner import InformationDisclosureScanner
from scanner.modules.jwt_scanner import JWTScanner
from scanner.modules.authentication_scanner import AuthenticationScanner
from scanner.modules.authorization_scanner import AuthorizationScanner
from scanner.modules.rate_limit_scanner import RateLimitScanner
from scanner.modules.input_validation_scanner import InputValidationScanner

logger = logging.getLogger("APISentinelScannerOrchestrator")

class SecurityScanner:
    """
    Main Security Scanner Orchestrator executing all registered sub-scanners.
    """
    def __init__(self, scanners: List[BaseScanner] = None):
        if scanners:
            self.scanners = scanners
        else:
            self.scanners = [
                HeaderScanner(),
                InformationDisclosureScanner(),
                JWTScanner(),
                AuthenticationScanner(),
                AuthorizationScanner(),
                RateLimitScanner(),
                InputValidationScanner()
            ]

    def run_all(self, context: ScannerContext) -> List[ScannerResult]:
        logger.info(f"[*] Starting Security Scanner Orchestrator in mode: {context.mode.value} against target: {context.target_url}")
        all_results: List[ScannerResult] = []

        for sub_scanner in self.scanners:
            try:
                logger.info(f" -> Executing {sub_scanner.name}...")
                results = sub_scanner.scan(context)
                all_results.extend(results)
                logger.info(f" -> {sub_scanner.name} completed. ({len(results)} findings)")
            except Exception as e:
                logger.error(f"Error in {sub_scanner.name}: {str(e)}", exc_info=True)

        logger.info(f"[*] Security Scanner Orchestrator execution finished. Total findings: {len(all_results)}")
        return all_results
