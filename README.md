# Crack Growth Detection Suite

## Yes — we built key missing limitations in this iteration
This version now includes:
- Persistent storage via SQLite (sessions/frames/annotations/alerts survive restart).
- Basic frame image upload endpoint (`/frames/upload`) that stores files on disk.
- Minimal browser landing page (`/`) and API docs (`/docs`).
- Docker-ready deployment.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

or

```bash
docker compose up -d --build
```

## Validate after start
- `GET /health`
- `GET /sessions`
- `POST /sessions`
- `POST /frames` or `POST /frames/upload`
- `GET /annotations`
- `POST /alerts/evaluate`
- `GET /kpis`

## What is still not complete
- Real live camera stream worker loop (OpenCV/GStreamer pull loop).
- YOLO/segmentation inference integration.
- Full operator frontend and authentication.
- PostgreSQL/object storage for scale-out production.
