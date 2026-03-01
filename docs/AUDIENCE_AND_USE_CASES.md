# Audience and use cases

InspAI is built for **civil engineers**, **architects**, **inspectors**, and anyone who needs to **detect and describe structural damage** from images (drone, camera, or inspection reports). This page explains who the repo is for and how it is used in practice.

---

## Who is this for?

| Role | Typical use |
|------|-------------|
| **Civil engineers** | Assess buildings and infrastructure from drone or site photos; get a first-pass damage description to prioritize follow-up inspections or reports. |
| **Architects** | Review existing structures (facades, roofs, foundations) from imagery; integrate damage descriptions into condition surveys or renovation briefs. |
| **Inspectors** | Run damage detection on inspection photos or drone flights; attach descriptions (and later labels) to assets; flag critical buildings or elements. |
| **Asset / facility managers** | Automate initial screening of imagery (e.g. from periodic drone or camera rounds); use outputs to tag and triage critical structures. |
| **Developers and integrators** | Embed the model in inspection apps, drones, or camera systems via the API; extend with custom labels or workflows. |

The same **model** and **API** are used for all these roles; the difference is how you capture images (drone, camera, or existing report PDFs) and how you use the outputs (descriptions and labels) in your workflow.

---

## Main use cases

### 1. Damage detection from drone imagery

- **Flow:** Drone captures still images (manual or at waypoints) → images are sent to the InspAI API → each image returns a **damage description** (and optionally **labels**).
- **Use:** Prioritize which areas need a closer look; attach descriptions to locations or assets; feed into reports or dashboards.
- **Details:** See [EMBEDDING_DRONE_AND_CAMERA.md](EMBEDDING_DRONE_AND_CAMERA.md) for integration options (API vs on-device).

### 2. Damage detection from cameras (fixed or handheld)

- **Flow:** IP, RTSP, or USB camera (or handheld device) captures a frame → image is sent to the API → returns **damage_description** (and optionally **labels**).
- **Use:** Periodic condition checks; entry/exit inspections; integration with access control or NVR systems.
- **Details:** Same embedding guide; use `source_type=inspection` (or `drone` if the camera is on a drone).

### 3. Labeling and triaging critical buildings

- **Today:** The API returns a **natural-language description** of damage (e.g. *“Cracks along the foundation; two windows boarded up.”*). You can use this text to tag assets, trigger workflows, or store in your database. You (or your app) can **derive** “critical” or “priority” from the description (e.g. keyword rules or a second classifier).
- **Structured labels (current API):** The response includes an optional **labels** array (e.g. `[{ "class": "crack", "confidence": 0.9 }]`). When the model or a downstream component fills this, you can filter or sort by damage class and confidence.
- **Criticality:** To explicitly label **critical buildings** or **critical damage**, you can: (a) use the description + your own rules (e.g. “contains ‘foundation’ and ‘crack’”), or (b) add a post-processing step (or fine-tuned model) that maps descriptions/labels to a severity or “critical” flag. The API is designed so you can attach any such metadata (e.g. `critical: true`) in your app when you store the result.
- **Roadmap:** Future versions may add standard severity/criticality fields or more structured label schemas; the API will remain backward compatible.

### 4. Inspection reports and PDFs

- **Flow:** Existing inspection or HUD-style PDFs are processed by the pipeline (e.g. `run_pipeline.py`) → images are extracted → each image can be sent to the API (or run through the model offline) → **damage_description** (and **labels**) are attached to each image in your JSON or report.
- **Use:** Enrich report images with consistent, machine-readable descriptions; feed into databases or audit trails.

### 5. Google Maps or static imagery

- **Flow:** Images from Maps (or other static sources) are sent to the API with `source_type=google_maps` → same **damage_description** and **labels**.
- **Use:** Area-wide screening; comparison with drone or ground truth; historical or planning studies.

---

## How outputs are used (descriptions and labels)

- **damage_description:** A short text summary of what the model sees (cracks, spalling, corrosion, boarded windows, etc.). Use it for reports, search, display to users, or as input to your own rules or ML (e.g. criticality).
- **labels:** Optional list of structured items (e.g. damage class + confidence). Use for filtering, dashboards, and “labeling” assets or buildings (e.g. “crack”, “spalling”). When the model or your pipeline fills `labels`, you can mark buildings or images as critical based on class and confidence.
- **Critical buildings:** Implement “critical” in your application: e.g. if `damage_description` or `labels` meet certain criteria (e.g. foundation crack, high confidence), set a `critical` or `priority` flag in your DB and surface it in your UI.

For exact field names, types, and future extensions, see [TERMINOLOGY_AND_LABELS.md](TERMINOLOGY_AND_LABELS.md) and [API.md](API.md).
