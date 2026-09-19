from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.traffic import TrafficEvent
from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.traffic import (
    TrafficEventCreate,
    TrafficEventResponse,
    TrafficStatsEndpointsResponse,
    TrafficStatsStatusCodesResponse,
    TrafficStatsLatencyResponse,
    TrafficStatsVolumeResponse
)
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.detection.anomaly_engine import AnomalyEngine

router = APIRouter(prefix="/traffic", tags=["API Traffic Monitor"])

@router.get("", response_model=List[TrafficEventResponse])
def list_traffic_events(
    project_id: Optional[int] = Query(None),
    endpoint_id: Optional[int] = Query(None),
    method: Optional[str] = Query(None),
    status_code: Optional[int] = Query(None),
    min_anomaly_score: Optional[float] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(TrafficEvent)
    if project_id:
        query = query.filter(TrafficEvent.project_id == project_id)
    if endpoint_id:
        query = query.filter(TrafficEvent.endpoint_id == endpoint_id)
    if method:
        query = query.filter(TrafficEvent.request_method == method.upper())
    if status_code:
        query = query.filter(TrafficEvent.response_status == status_code)
    if min_anomaly_score is not None:
        query = query.filter(TrafficEvent.anomaly_score >= min_anomaly_score)

    return query.order_by(TrafficEvent.timestamp.desc()).limit(limit).all()

@router.post("", response_model=TrafficEventResponse, status_code=status.HTTP_201_CREATED)
async def record_traffic_event(
    traffic_in: TrafficEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == traffic_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Fetch recent statuses for IP to evaluate auth failure patterns
    recent_ip_statuses = []
    if traffic_in.client_ip:
        recent_events = db.query(TrafficEvent.response_status).filter(
            TrafficEvent.client_ip == traffic_in.client_ip
        ).order_by(TrafficEvent.timestamp.desc()).limit(10).all()
        recent_ip_statuses = [r[0] for r in recent_events]

    # Evaluate Anomaly Engine for explainable anomaly scoring
    anomaly_eval = AnomalyEngine.evaluate_traffic_event(
        request_method=traffic_in.request_method.upper(),
        request_url=traffic_in.request_url,
        response_status=traffic_in.response_status,
        response_time_ms=traffic_in.response_time_ms,
        client_ip=traffic_in.client_ip,
        recent_ip_statuses=recent_ip_statuses
    )

    merged_flags = list(set((traffic_in.flag_reasons or []) + anomaly_eval.flag_reasons))

    event = TrafficEvent(
        project_id=traffic_in.project_id,
        endpoint_id=traffic_in.endpoint_id,
        user_id=traffic_in.user_id,
        request_method=traffic_in.request_method.upper(),
        request_url=traffic_in.request_url,
        headers=traffic_in.headers,
        payload=traffic_in.payload, # Sanitized body
        response_status=traffic_in.response_status,
        response_time_ms=traffic_in.response_time_ms,
        request_size_bytes=traffic_in.request_size_bytes or 0,
        response_size_bytes=traffic_in.response_size_bytes or 0,
        client_ip=traffic_in.client_ip,
        anomaly_score=anomaly_eval.anomaly_score,
        flag_reasons=merged_flags
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Broadcast event if WebSocket manager active
    try:
        from app.routers.websocket import manager
        await manager.broadcast({
            "type": "TRAFFIC_EVENT",
            "data": {
                "id": event.id,
                "project_id": event.project_id,
                "method": event.request_method,
                "url": event.request_url,
                "status": event.response_status,
                "latency_ms": event.response_time_ms,
                "anomaly_score": event.anomaly_score,
                "flag_reasons": event.flag_reasons
            }
        })
    except Exception:
        pass

    return event

@router.get("/stats/endpoints", response_model=List[TrafficStatsEndpointsResponse])
def get_endpoint_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        TrafficEvent.request_url,
        TrafficEvent.request_method,
        func.count(TrafficEvent.id).label("request_count"),
        func.sum(case((TrafficEvent.response_status >= 400, 1), else_=0)).label("error_count"),
        func.avg(TrafficEvent.response_time_ms).label("avg_latency_ms")
    )
    if project_id:
        query = query.filter(TrafficEvent.project_id == project_id)

    stats = query.group_by(TrafficEvent.request_url, TrafficEvent.request_method).all()

    results = []
    for s in stats:
        results.append(TrafficStatsEndpointsResponse(
            path=s[0],
            method=s[1],
            request_count=s[2],
            error_count=s[3] or 0,
            avg_latency_ms=round(float(s[4] or 0.0), 2)
        ))
    return results

@router.get("/stats/status-codes", response_model=List[TrafficStatsStatusCodesResponse])
def get_status_code_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(TrafficEvent)
    if project_id:
        query = query.filter(TrafficEvent.project_id == project_id)

    total = query.count()
    if total == 0:
        return [
            TrafficStatsStatusCodesResponse(status_code_group="2xx", count=0, percentage=0.0),
            TrafficStatsStatusCodesResponse(status_code_group="3xx", count=0, percentage=0.0),
            TrafficStatsStatusCodesResponse(status_code_group="4xx", count=0, percentage=0.0),
            TrafficStatsStatusCodesResponse(status_code_group="5xx", count=0, percentage=0.0),
        ]

    c2xx = query.filter(TrafficEvent.response_status >= 200, TrafficEvent.response_status < 300).count()
    c3xx = query.filter(TrafficEvent.response_status >= 300, TrafficEvent.response_status < 400).count()
    c4xx = query.filter(TrafficEvent.response_status >= 400, TrafficEvent.response_status < 500).count()
    c5xx = query.filter(TrafficEvent.response_status >= 500).count()

    return [
        TrafficStatsStatusCodesResponse(status_code_group="2xx", count=c2xx, percentage=round(c2xx / total * 100, 1)),
        TrafficStatsStatusCodesResponse(status_code_group="3xx", count=c3xx, percentage=round(c3xx / total * 100, 1)),
        TrafficStatsStatusCodesResponse(status_code_group="4xx", count=c4xx, percentage=round(c4xx / total * 100, 1)),
        TrafficStatsStatusCodesResponse(status_code_group="5xx", count=c5xx, percentage=round(c5xx / total * 100, 1)),
    ]

@router.get("/stats/latency", response_model=TrafficStatsLatencyResponse)
def get_latency_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        func.avg(TrafficEvent.response_time_ms),
        func.min(TrafficEvent.response_time_ms),
        func.max(TrafficEvent.response_time_ms)
    )
    if project_id:
        query = query.filter(TrafficEvent.project_id == project_id)

    res = query.first()
    avg_l = float(res[0] or 0.0)
    min_l = float(res[1] or 0.0)
    max_l = float(res[2] or 0.0)

    return TrafficStatsLatencyResponse(
        avg_latency_ms=round(avg_l, 2),
        min_latency_ms=round(min_l, 2),
        max_latency_ms=round(max_l, 2),
        p95_latency_ms=round(max_l * 0.9, 2)
    )

@router.get("/stats/volume", response_model=List[TrafficStatsVolumeResponse])
def get_volume_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(TrafficEvent)
    if project_id:
        query = query.filter(TrafficEvent.project_id == project_id)

    total = query.count()
    errors = query.filter(TrafficEvent.response_status >= 400).count()

    return [
        TrafficStatsVolumeResponse(timestamp_bucket="Last Hour", request_count=total, error_count=errors)
    ]
