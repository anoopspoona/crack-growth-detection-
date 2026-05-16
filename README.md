# Crack Growth Detection Suite

A practical starter implementation for an industrial crack-growth monitoring system:
- image acquisition session APIs,
- annotation task APIs,
- KPI-driven deployment gates,
- real-time alert state engine (CPU-friendly baseline).

## Industrially Acceptable KPI Targets (Initial Release Gates)
These are pragmatic deployment gates commonly used in industrial vision rollouts (high recall safety posture + controlled nuisance alarms):

1. **Crack Onset Detection Recall**: **>= 97%** on unseen test sessions.
2. **False Critical Alarm Rate**: **<= 1 per 8-hour shift**.
3. **Crack Length Error (MAE)**: **<= 0.25 mm** in validated operating range.
4. **End-to-End Alert Latency**: **<= 300 ms** on target PC profile.
5. **System Availability**: **>= 99%** during monitored test windows.
6. **Data Completeness**: **>= 99.5%** of expected frames/telemetry pairs captured.
7. **Operator Acknowledgment Traceability**: **100%** critical alarms logged with timestamp + user.

> Tune thresholds per specimen/material program after site acceptance trials.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

API docs: `http://localhost:8080/docs`

## Included in this starter build
- Acquisition session creation/start/stop.
- Frame ingest endpoint (metadata-first baseline).
- Annotation task lifecycle.
- KPI status endpoint with pass/fail against configured gates.
- Alert engine endpoint implementing state progression:
  `NORMAL -> SUSPECTED_INITIATION -> CONFIRMED_GROWTH -> CRITICAL`.

## Next build steps
1. Bind live camera ingestion worker (OpenCV/GStreamer).
2. Add real YOLO + segmentation inference service.
3. Replace in-memory store with PostgreSQL and object storage.
4. Add web frontend for operator and reviewer workflows.
