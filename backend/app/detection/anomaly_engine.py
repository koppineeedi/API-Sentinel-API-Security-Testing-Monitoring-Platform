from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AnomalyEvaluation(BaseModel):
    anomaly_score: float # 0.0 (normal) to 1.0 (highly anomalous)
    is_anomalous: bool
    flag_reasons: List[str]

class AnomalyEngine:
    """
    Explainable Anomaly Detection Engine for API Traffic Events.
    Evaluates traffic signals without opaque black-box AI decisions. Every flag includes explicit human-readable reasons.
    """

    LATENCY_THRESHOLD_MS = 3000.0 # 3 seconds
    ERROR_RATIO_THRESHOLD = 0.40 # 40% error responses in window
    HIGH_VOLUME_THRESHOLD = 50 # 50 requests in window

    @classmethod
    def evaluate_traffic_event(
        cls,
        request_method: str,
        request_url: str,
        response_status: int,
        response_time_ms: float,
        client_ip: Optional[str] = None,
        recent_ip_statuses: Optional[List[int]] = None,
        recent_window_request_count: int = 1
    ) -> AnomalyEvaluation:
        flag_reasons: List[str] = []
        score_accumulator = 0.0

        # Signal 1: Latency Spike
        if response_time_ms >= cls.LATENCY_THRESHOLD_MS:
            reasons_msg = f"Latency Spike: Response time ({int(response_time_ms)}ms) exceeded {int(cls.LATENCY_THRESHOLD_MS)}ms threshold"
            flag_reasons.append(reasons_msg)
            score_accumulator += 0.35

        # Signal 2: Server Error Response (5xx)
        if response_status >= 500:
            flag_reasons.append(f"Server Error Exception: HTTP {response_status} Internal Error response emitted")
            score_accumulator += 0.30

        # Signal 3: Repeated Authentication Failures from single IP
        if recent_ip_statuses:
            auth_failures = sum(1 for status in recent_ip_statuses if status in [401, 403])
            if auth_failures >= 3:
                flag_reasons.append(
                    f"Repeated Authentication Failures: {auth_failures} 401/403 security rejections detected from client IP {client_ip or 'unknown'}"
                )
                score_accumulator += 0.45

        # Signal 4: High Request Volume Burst
        if recent_window_request_count > cls.HIGH_VOLUME_THRESHOLD:
            flag_reasons.append(
                f"Abnormal Request Volume: {recent_window_request_count} requests in short window exceeded baseline limit ({cls.HIGH_VOLUME_THRESHOLD})"
            )
            score_accumulator += 0.40

        # Signal 5: Sensitive / Admin Endpoint Probe by Unauthenticated Client
        path_lower = request_url.lower()
        if any(sensitive in path_lower for sensitive in ["/admin", "/config", "/env", "/actuator", "/.git"]):
            if response_status in [200, 401, 403]:
                flag_reasons.append(
                    f"Sensitive Endpoint Probe: Request targeted sensitive administrative route '{request_url}'"
                )
                score_accumulator += 0.35

        final_score = min(1.0, round(score_accumulator, 2))
        is_anomalous = final_score >= 0.40 or len(flag_reasons) > 0

        return AnomalyEvaluation(
            anomaly_score=final_score,
            is_anomalous=is_anomalous,
            flag_reasons=flag_reasons
        )
