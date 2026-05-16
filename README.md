# Crack Growth Detection Suite (Complete Package)

This repository now defines a **complete, end-to-end application suite** that covers:
1) image/video acquisition from the UTM-mounted camera, 2) built-in labeling/annotation workflow, 3) model training and model registry, and 4) real-time crack detection with alarms in the operator web app.

## 1) Direct Answer to Your Question
**Yes — the app should and will be able to acquire images for labeling and annotation.**
The target system is a single integrated platform with separate modules for:
- Live capture and dataset creation,
- Annotation and review,
- AI training/validation,
- Real-time inference + warning UI.

---

## 2) Product Definition: One Platform, Four Modules

### Module A — Acquisition Console (Data Capture)
Purpose: collect production-quality images/video and generate training datasets.

Core capabilities:
- Connect to RTSP/USB/GigE camera mounted on UTM.
- Start/stop “Test Session” recording with metadata:
  - specimen ID, material, thickness, notch geometry,
  - UTM program ID, load ratio, frequency, operator ID.
- Capture modes:
  - **Continuous video** (full stream archive),
  - **Periodic frame sampling** (e.g., every N cycles / every N seconds),
  - **Event-triggered burst** when changes are detected.
- Auto-sync with UTM cycle/load data over API/CSV/DAQ.
- Save images directly into dataset structure (raw + curated buckets).

Minimum acceptance:
- Operator can run one session and export frame subsets to annotation queue in ≤3 clicks.

### Module B — Annotation Workbench (Integrated)
Purpose: label data without leaving the platform.

Core capabilities:
- Built-in annotation UI (or embedded CVAT/Label Studio in same portal).
- Label types:
  - crack bounding box (for YOLO),
  - crack segmentation/polyline,
  - optional keypoints (notch root, crack tip).
- Workflow states: `new → in_progress → review → approved → training_ready`.
- Reviewer QA:
  - dual-review for sampled frames,
  - disagreement flag + resolution tracking.
- Dataset versioning and export:
  - YOLO format,
  - COCO segmentation,
  - keypoint JSON.

Minimum acceptance:
- Annotator can label and submit a frame in <20 seconds average after training.

### Module C — Training & Model Management
Purpose: train, validate, and publish model versions safely.

Core capabilities:
- One-click training jobs using approved dataset versions.
- Model options:
  - YOLO detector for onset/region detection,
  - segmentation model for crack path length,
  - optional keypoint head for robust tip localization.
- Automatic experiment tracking (hyperparameters, metrics, artifacts).
- Registry states: `candidate → validated → production → retired`.
- Performance gates before promotion:
  - onset recall,
  - crack-length MAE,
  - false alarm rate.

Minimum acceptance:
- No model can deploy unless it passes validation thresholds on held-out sessions.

### Module D — Real-Time Monitoring & Alerts (Operator App)
Purpose: run production inference and warn users in real time.

Core capabilities:
- Live stream with overlay (box/mask/tip + measured crack length in mm).
- Trend panel: crack length vs cycle count/time, growth rate da/dN.
- State machine:
  - Normal → Suspected Initiation → Confirmed Growth → Critical.
- Audible + visual alarms with acknowledgment log.
- Event replay clips for post-test analysis.

Minimum acceptance:
- Critical alarm latency <200 ms end-to-end on target hardware.

---

## 3) Reference Technical Architecture

### 3.1 Edge + Server Split
- **Edge runtime near UTM**
  - camera ingestion,
  - low-latency inference,
  - fail-safe local alarm output.
- **Central server / lab network**
  - web UI,
  - annotation service,
  - training orchestration,
  - model registry,
  - long-term storage/reporting.

### 3.2 Data Flow
1. Session starts in Acquisition Console.
2. Frames/video + UTM telemetry are ingested and timestamp-synced.
3. Curated frames are pushed to annotation queue.
4. Approved labels form dataset version `D_x`.
5. Training job creates model `M_x` with full metrics.
6. After validation gates, `M_x` promoted to production.
7. Real-time app loads `M_x` and generates alerts + logs.


## 3.3 Can a Single PC Connected to the UTM Run This?
**Yes.** A Windows/Linux PC connected to the UTM camera can run the full application stack, with two practical deployment modes:

- **Mode 1 (Single-PC All-in-One):** acquisition + annotation + training + real-time monitoring on one workstation.
- **Mode 2 (Recommended for labs):** acquisition + real-time monitoring on the UTM PC, while heavy training jobs run on a central GPU server.

### Minimum PC Specification (All-in-One Pilot)
- CPU: modern 4-core Intel/AMD processor (minimum baseline).
- RAM: 8 GB (minimum baseline).
- GPU: NVIDIA RTX class with 8–12 GB VRAM (or better).
- Storage: 250 GB HDD/SSD minimum (higher capacity strongly recommended for video-heavy tests).
- I/O: USB3/GigE for camera and stable LAN for backup/sync.

### Recommended Lab Specification (Production)
- UTM-side PC: 16-core CPU, 64 GB RAM, RTX 4070/4080-class GPU, 2 TB NVMe.
- Central training node (optional): multi-GPU or high-VRAM GPU server for faster retraining.

### Realistic Expectation
- A single PC **can absolutely run the app** for pilot and many production workloads.
- If dataset size and retraining frequency grow, keep real-time inference on the UTM PC and offload model training to a central server.


## 3.4 Can It Run on a Regular PC Without GPU?
**Yes.** The suite can run on a CPU-only regular PC, with some performance trade-offs.

### CPU-Only Mode (Supported)
- Inference runtime: ONNX Runtime CPU execution provider.
- Model profile: smaller YOLO variant (e.g., nano/small) + reduced input resolution.
- Frame strategy: process every Nth frame (frame skipping) while keeping full video recording.
- Alert logic: keep temporal confirmation windows to maintain reliability at lower FPS.

### Expected Trade-Offs on CPU-Only PCs
- Higher inference latency and lower real-time FPS than GPU mode.
- Slower training and retraining jobs.
- Best for pilot use, lower-frequency fatigue tests, or analysis/review workflows.

### Minimum Practical CPU-Only Specification
- CPU: modern 4-core Intel/AMD processor (minimum baseline).
- RAM: 8 GB minimum.
- Storage: 250 GB HDD/SSD minimum.
- Camera I/O: USB3/GigE stable connection.

### Recommended CPU-Only Operating Profile
- Prioritize acquisition + monitoring + annotation on the local PC.
- Schedule model training overnight or offload training to another machine when possible.
- Use tuned model + ROI cropping + quantization to sustain usable alerting latency.

---

## 4) Image Acquisition Plan (Operational SOP)

### 4.1 Camera/Optics Standard
- Industrial global-shutter camera.
- Fixed lens, locked focus, no autofocus.
- Rigid mount with mechanical stops.
- Manual exposure/gain/white-balance lock.
- Diffused flicker-free LED illumination.

### 4.2 Calibration and Measurement Fidelity
- Place known scale/fiducial in view before session.
- Run automatic perspective correction and mm/pixel calibration.
- Save calibration hash with each session for auditability.

### 4.3 Session Capture Policy
- 30 FPS baseline (raise if crack dynamics demand).
- Retain full video + extracted frames.
- “Golden frame” snapshots at key cycle intervals.
- Quality checks each minute:
  - blur score,
  - glare score,
  - ROI drift score.

### 4.4 Dataset Policy
- Split by **session/specimen**, never random frame split.
- Mandatory coverage:
  - no-crack phase,
  - crack initiation,
  - steady growth,
  - near-failure.

---

## 5) Annotation Plan (Built-In and Fool-Proof)

### 5.1 Labeling Rules
- Crack must originate from notch vicinity unless explicitly marked anomaly.
- Distinguish crack from scratches and paint artifacts.
- For branching cracks, annotate primary growth path and mark branch flag.

### 5.2 QA Rules
- 10–15% double-annotated.
- Automatic geometry sanity checks.
- Reviewer sign-off required before `training_ready`.

### 5.3 Throughput Plan
- Start with 20,000–50,000 curated frames from 50–100 tests.
- Weekly annotation batches + continuous data enrichment.

---

## 6) Model Strategy (YOLO + Segmentation)

### 6.1 Recommendation
Use a **hybrid pipeline**:
- YOLO for fast crack presence/ROI detection.
- Segmentation/keypoint stage for precise crack tip and crack length.

### 6.2 Training Pipeline
1. Preprocess (distortion correction, ROI crop, contrast normalization).
2. Augment realistically (brightness, blur, noise, slight affine).
3. Split by session to avoid leakage.
4. Optimize for high early-crack recall.
5. Export optimized runtime model (ONNX/TensorRT).

### 6.3 Validation Gates (Example)
- Onset recall ≥ 98%.
- Crack length MAE ≤ 0.2 mm.
- False critical alarms ≤ 1 per 8-hour shift.
- Median inference latency ≤ 80 ms/frame.

---

## 7) Deployment Blueprint

### 7.1 Environments
- **Dev:** recorded stream replay.
- **Validation:** shadow mode during real tests.
- **Production:** active alarms with SOP escalation.

### 7.2 Reliability Controls
- Service health watchdog and auto-restart.
- Local buffering during network interruption.
- Local critical buzzer if server unavailable.
- Role-based access + audit trails.

### 7.3 MLOps Lifecycle
- Dataset registry + model registry.
- Drift dashboard and alert quality monitoring.
- Scheduled retraining and controlled canary rollout.


## 7.4 Access from Another PC + Offline Operation
You can support **both** remote analysis from another PC and fully offline operation by using a two-profile deployment design.

### Profile A: Lab LAN Deployment (Recommended)
- UTM-side host runs core services (ingestion, inference, API, database, UI).
- Other PCs on the same lab network open browser to: `http://<utm-hostname-or-ip>:<port>`.
- Role-based login controls access for operator/engineer/admin.
- Best for collaborative analysis, report review, and annotation from non-UTM desks.

### Profile B: Fully Offline Standalone Deployment
- All services run on the UTM-side PC with no internet dependency during operation.
- Model files, JS/CSS assets, containers, and Python wheels are pre-bundled.
- Local-only user auth and local database/storage are enabled.
- Reports export to local disk or intranet share when available.

### Hybrid Practical Mode
- Run offline during testing shifts.
- Sync datasets/models/reports to central server when network becomes available.

## 7.5 Deployment Prerequisites

### A) Hardware Prerequisites
- UTM-connected camera (USB3/GigE/RTSP capable).
- UTM-side workstation (GPU recommended, but CPU-only mode is supported).
- Optional NAS or secondary disk for long video retention.
- UPS for safe shutdown and test continuity.

### B) Network Prerequisites
For remote access from another PC:
- Same subnet/VLAN as UTM host **or** routed lab network path.
- Static IP or reserved DHCP lease for UTM host.
- Open inbound ports for web UI/API/WebSocket (example: 8080/8443).
- Local DNS hostname optional but recommended.

For strict offline mode:
- No external internet required at runtime.
- Optional isolated lab LAN still allowed for intra-lab remote access.

### C) Software/Platform Prerequisites
- OS: Ubuntu LTS or Windows 11 Pro (standardized image).
- Container runtime: Docker + Compose (recommended) **or** native Python stack.
- NVIDIA driver + CUDA runtime (only if GPU inference is enabled; not required for CPU-only mode).
- PostgreSQL storage volume and backup schedule.
- Time synchronization source (local NTP or machine clock policy).

### D) Security & Access Prerequisites
- Role-based accounts (operator/engineer/admin).
- TLS for LAN deployment where policy requires encrypted transport.
- Audit logging enabled for login, alarm acknowledgment, and model changes.
- Regular credential rotation and removable-media policy for offline systems.

### E) MLOps/Packaging Prerequisites for Offline Use
- Pre-download model artifacts and dependency packages.
- Maintain offline “release bundle”:
  - application containers/images,
  - model registry snapshot,
  - migration scripts,
  - calibration templates,
  - startup/shutdown SOP.
- Validate bundle in an air-gapped test before production rollout.

## 7.6 Deployment Plan (Step-by-Step)
1. **Provision host PC** with GPU drivers, Docker, storage mounts, and UPS integration.
2. **Install Crack Growth Suite bundle** (containers + configs + model package).
3. **Bind camera + UTM telemetry connectors** and run calibration workflow.
4. **Run site acceptance test (SAT)** using recorded and live specimen sessions.
5. **Enable LAN access** for analysis PCs (firewall rules + RBAC checks).
6. **Enable offline mode controls** (disable internet dependency checks, local auth only).
7. **Go-live in shadow mode** for 1–2 weeks, then active alarms after KPI sign-off.
8. **Operate with periodic sync windows** (if hybrid mode is used).

## 7.7 What You Will Be Able to Do
- Monitor and annotate from UTM PC directly.
- Open the same application from another lab PC for analysis/review.
- Continue full acquisition, detection, and reporting even without internet.
- Optionally synchronize to central infrastructure later.

---

## 8) Web Application Screens (Required)

1. **Session Setup Screen**
   - specimen metadata, camera health, calibration check.
2. **Live Acquisition Screen**
   - stream preview, capture controls, telemetry sync status.
3. **Annotation Screen**
   - frame browser, drawing tools, review workflow.
4. **Training Screen**
   - dataset selection, training launch, metrics view.
5. **Monitoring Screen**
   - live overlays, trend charts, alarms, acknowledgments.
6. **Reports Screen**
   - export PDF/CSV with events and crack-growth curves.

---

## 9) 16-Week Delivery Plan

### Weeks 1–4
- Hardware setup + acquisition service + metadata schema.
- Basic session UI and storage pipeline.

### Weeks 5–8
- Annotation workbench integration and QA workflow.
- Pilot labeling and first dataset release.

### Weeks 9–12
- YOLO detection MVP + segmentation refinement.
- Validation metrics and threshold tuning.

### Weeks 13–16
- Full operator app, alarms, audit, reporting.
- Shadow trials and production hardening.

---

## 10) Tech Stack (Pragmatic)
- AI: PyTorch + Ultralytics YOLO + segmentation model.
- Runtime: ONNX Runtime / TensorRT.
- Backend: FastAPI + PostgreSQL + Redis.
- Frontend: React + WebSocket updates.
- Annotation: embedded CVAT/Label Studio.
- MLOps: MLflow + DVC + Docker.

---

## 11) Final Acceptance Checklist (Go-Live)
- [ ] Acquisition module captures synchronized video + UTM telemetry.
- [ ] Annotation module supports full label/review workflow.
- [ ] Training pipeline is reproducible with model registry.
- [ ] Production model meets all validation gates.
- [ ] Monitoring module provides real-time visual + audio alerts.
- [ ] Audit/reporting package is complete for each test session.

If all boxes are checked, the system is a true **complete package** from acquisition to annotation to final AI crack detection.


## 12) Missing Items Checklist Before Build & Deployment on PC
Before you start implementation on a real PC, confirm these items are closed. If any are open, they are the true blockers.

### A) Requirements Freeze (Must-Have)
- [ ] Finalize measurable acceptance KPIs (onset recall, MAE, false alarms/shift, max latency).
- [ ] Freeze alarm thresholds/escalation policy with lab safety stakeholders.
- [ ] Confirm supported camera models and UTM telemetry interface contract.

### B) Data & Labeling Readiness
- [ ] Pilot dataset collected (minimum representative sessions: no-crack → initiation → growth).
- [ ] Label handbook approved (edge cases: glare, scratches, branching cracks).
- [ ] Annotation QA protocol approved (double-annotation percentage + reviewer signoff).

### C) Deployment Readiness on Target PC
- [ ] OS image and patch level frozen (Windows/Ubuntu standard image).
- [ ] Offline/online deployment profile selected (LAN, standalone offline, or hybrid).
- [ ] Storage sizing validated against expected daily video volume and retention days.
- [ ] Backup/restore dry-run completed.

### D) Runtime & Integration Readiness
- [ ] Camera driver stability test completed for continuous run duration.
- [ ] UTM sync integration test passed (timestamp alignment verified).
- [ ] End-to-end latency smoke test passed on target PC hardware.
- [ ] Audio/visual alarm validation completed with operator acknowledgment workflow.

### E) Security, Audit, and SOP Readiness
- [ ] User roles and account lifecycle defined (operator/engineer/admin).
- [ ] Audit log fields finalized (login, alarm ack, model switch, calibration run).
- [ ] Startup/shutdown/calibration SOP documents approved.
- [ ] Incident response SOP approved (what to do when system flags critical crack growth).

### F) Go-Live Control
- [ ] Shadow-mode trial completed (recommended 1–2 weeks).
- [ ] KPI signoff from engineering + lab operations.
- [ ] Rollback plan tested (previous model/config restore under 15 minutes).

### Practical Answer
If all boxes above are checked, you are ready to build and deploy on PC with controlled risk.
If not, those unchecked boxes are the missing items to close first.
