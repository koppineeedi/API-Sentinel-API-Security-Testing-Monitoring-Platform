import pytest
from app.detection.anomaly_engine import AnomalyEngine

def test_anomaly_latency_spike():
    eval_res = AnomalyEngine.evaluate_traffic_event(
        request_method="GET",
        request_url="/api/v1/users",
        response_status=200,
        response_time_ms=4500.0 # Exceeds 3000ms threshold
    )
    assert eval_res.is_anomalous is True
    assert eval_res.anomaly_score >= 0.35
    assert any("Latency Spike" in reason for reason in eval_res.flag_reasons)

def test_anomaly_repeated_auth_failures():
    eval_res = AnomalyEngine.evaluate_traffic_event(
        request_method="POST",
        request_url="/api/v1/auth/login",
        response_status=401,
        response_time_ms=120.0,
        client_ip="192.168.1.50",
        recent_ip_statuses=[401, 401, 401, 401] # 4 repeated auth rejections
    )
    assert eval_res.is_anomalous is True
    assert eval_res.anomaly_score >= 0.45
    assert any("Repeated Authentication Failures" in reason for reason in eval_res.flag_reasons)

def test_anomaly_normal_traffic():
    eval_res = AnomalyEngine.evaluate_traffic_event(
        request_method="GET",
        request_url="/health",
        response_status=200,
        response_time_ms=50.0
    )
    assert eval_res.is_anomalous is False
    assert eval_res.anomaly_score == 0.0
    assert len(eval_res.flag_reasons) == 0
