from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Crack Growth Detection Suite API", version="0.1.0")


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"


class AlertState(str, Enum):
    NORMAL = "normal"
    SUSPECTED_INITIATION = "suspected_initiation"
    CONFIRMED_GROWTH = "confirmed_growth"
    CRITICAL = "critical"


class SessionCreate(BaseModel):
    specimen_id: str
    material: str
    operator_id: str
    camera_id: str


class Session(BaseModel):
    id: int
    specimen_id: str
    material: str
    operator_id: str
    camera_id: str
    status: SessionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None


class FrameIngest(BaseModel):
    session_id: int
    frame_index: int
    timestamp: datetime
    cycle_count: Optional[int] = None
    load_kn: Optional[float] = None


class AnnotationTask(BaseModel):
    id: int
    session_id: int
    frame_index: int
    status: str = "new"
    reviewer_id: Optional[str] = None


class AlertInput(BaseModel):
    confidence: float = Field(ge=0.0, le=1.0)
    crack_length_mm: float = Field(ge=0.0)
    growth_rate_mm_per_1k_cycles: float = Field(ge=0.0)


class KPIResult(BaseModel):
    name: str
    target: str
    value: str
    pass_fail: str


sessions: Dict[int, Session] = {}
frames: List[FrameIngest] = []
annotation_tasks: Dict[int, AnnotationTask] = {}

session_counter = 1
task_counter = 1
alert_state = AlertState.NORMAL


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow()}


@app.post("/sessions", response_model=Session)
def create_session(payload: SessionCreate):
    global session_counter
    s = Session(
        id=session_counter,
        specimen_id=payload.specimen_id,
        material=payload.material,
        operator_id=payload.operator_id,
        camera_id=payload.camera_id,
        status=SessionStatus.CREATED,
        created_at=datetime.utcnow(),
    )
    sessions[session_counter] = s
    session_counter += 1
    return s


@app.post("/sessions/{session_id}/start", response_model=Session)
def start_session(session_id: int):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    s.status = SessionStatus.RUNNING
    s.started_at = datetime.utcnow()
    sessions[session_id] = s
    return s


@app.post("/sessions/{session_id}/stop", response_model=Session)
def stop_session(session_id: int):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    s.status = SessionStatus.STOPPED
    s.stopped_at = datetime.utcnow()
    sessions[session_id] = s
    return s


@app.post("/frames")
def ingest_frame(payload: FrameIngest):
    if payload.session_id not in sessions:
        raise HTTPException(404, "Session not found")
    frames.append(payload)
    if payload.frame_index % 50 == 0:
        global task_counter
        annotation_tasks[task_counter] = AnnotationTask(
            id=task_counter,
            session_id=payload.session_id,
            frame_index=payload.frame_index,
        )
        task_counter += 1
    return {"accepted": True, "total_frames": len(frames)}


@app.get("/annotations", response_model=List[AnnotationTask])
def list_annotation_tasks(status: Optional[str] = None):
    tasks = list(annotation_tasks.values())
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


@app.post("/annotations/{task_id}/status", response_model=AnnotationTask)
def set_annotation_status(task_id: int, status: str, reviewer_id: Optional[str] = None):
    t = annotation_tasks.get(task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    t.status = status
    t.reviewer_id = reviewer_id
    annotation_tasks[task_id] = t
    return t


@app.post("/alerts/evaluate")
def evaluate_alert(inp: AlertInput):
    global alert_state
    if inp.confidence < 0.35:
        alert_state = AlertState.NORMAL
    elif inp.confidence < 0.60:
        alert_state = AlertState.SUSPECTED_INITIATION
    elif inp.crack_length_mm >= 0.5 or inp.growth_rate_mm_per_1k_cycles >= 0.08:
        alert_state = AlertState.CONFIRMED_GROWTH
    if inp.crack_length_mm >= 1.5 or inp.growth_rate_mm_per_1k_cycles >= 0.20:
        alert_state = AlertState.CRITICAL
    return {"state": alert_state}


@app.get("/kpis", response_model=List[KPIResult])
def kpis():
    # Placeholder current values for integration testing.
    observed = {
        "recall": 97.4,
        "false_critical_per_shift": 0.8,
        "mae_mm": 0.22,
        "latency_ms": 265,
        "availability_pct": 99.2,
        "data_completeness_pct": 99.7,
        "critical_traceability_pct": 100.0,
    }
    return [
        KPIResult("Crack onset recall", ">= 97%", f"{observed['recall']}%", "pass" if observed["recall"] >= 97 else "fail"),
        KPIResult("False critical alarms", "<= 1 per shift", str(observed["false_critical_per_shift"]), "pass" if observed["false_critical_per_shift"] <= 1 else "fail"),
        KPIResult("Crack length MAE", "<= 0.25 mm", f"{observed['mae_mm']} mm", "pass" if observed["mae_mm"] <= 0.25 else "fail"),
        KPIResult("Alert latency", "<= 300 ms", f"{observed['latency_ms']} ms", "pass" if observed["latency_ms"] <= 300 else "fail"),
        KPIResult("Availability", ">= 99%", f"{observed['availability_pct']}%", "pass" if observed["availability_pct"] >= 99 else "fail"),
        KPIResult("Data completeness", ">= 99.5%", f"{observed['data_completeness_pct']}%", "pass" if observed["data_completeness_pct"] >= 99.5 else "fail"),
        KPIResult("Critical traceability", "= 100%", f"{observed['critical_traceability_pct']}%", "pass" if observed["critical_traceability_pct"] == 100 else "fail"),
    ]
