from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class TrafficEventCreate(BaseModel):
    project_id: int
    endpoint_id: Optional[int] = None
    user_id: Optional[int] = None
    request_method: str
    request_url: str
    headers: Optional[Dict[str, Any]] = None
    payload: Optional[str] = None
    response_status: int
    response_time_ms: float
    request_size_bytes: Optional[int] = 0
    response_size_bytes: Optional[int] = 0
    client_ip: Optional[str] = None
    flag_reasons: Optional[List[str]] = None

class TrafficEventResponse(BaseModel):
    id: int
    project_id: int
    endpoint_id: Optional[int] = None
    user_id: Optional[int] = None
    request_method: str
    request_url: str
    headers: Optional[Dict[str, Any]] = None
    payload: Optional[str] = None
    response_status: int
    response_time_ms: float
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime
    client_ip: Optional[str] = None
    anomaly_score: float
    flag_reasons: Optional[List[str]] = None

    class Config:
        from_attributes = True

class TrafficStatsEndpointsResponse(BaseModel):
    endpoint_id: Optional[int] = None
    path: str
    method: str
    request_count: int
    error_count: int
    avg_latency_ms: float

class TrafficStatsStatusCodesResponse(BaseModel):
    status_code_group: str # 2xx, 3xx, 4xx, 5xx
    count: int
    percentage: float

class TrafficStatsLatencyResponse(BaseModel):
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: float

class TrafficStatsVolumeResponse(BaseModel):
    timestamp_bucket: str
    request_count: int
    error_count: int
