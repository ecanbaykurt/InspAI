# InspAI — Structural damage description for drones and cameras

**Open-source model** for **detecting and describing structural damage** in images from **drones**, **cameras**, and inspection reports. One API, one model (LLaVA-1.5-7B); outputs natural-language descriptions and optional **labels** so you can screen assets and tag **critical buildings** in your workflows.

---

## Who is this for?

| Audience | Use |
|----------|-----|
| **Civil engineers** | First-pass damage assessment from drone or site photos; prioritize follow-up inspections. |
| **Architects** | Condition surveys and facade/roof review from imagery; integrate descriptions into briefs. |
| **Inspectors** | Damage detection on inspection or drone imagery; attach descriptions and labels to assets; flag critical structures. |
| **Developers / integrators** | Embed the model in apps, drones, or camera systems via a single API. |

See [docs/AUDIENCE_AND_USE_CASES.md](docs/AUDIENCE_AND_USE_CASES.md) for detailed use cases and workflows.

---

## What you get: descriptions and labels

- **damage_description** — Short text summary of damage (cracks, spalling, corrosion, boarded windows, foundation issues, etc.). Always returned.
- **labels** — Optional list of structured items (e.g. damage class + confidence) for filtering, dashboards, and **labeling critical buildings**. Schema and terminology are documented so you can build consistent workflows.

You can use the description (and labels when present) to **tag buildings or assets** as critical or priority in your own app or database. How descriptions and labels work, and how to interpret them, is in [docs/TERMINOLOGY_AND_LABELS.md](docs/TERMINOLOGY_AND_LABELS.md).

---

## Components

| Component | Description |
|-----------|-------------|
| **Model** | LLaVA-1.5-7B for structural damage description; fine-tunable (see `structural_damage_model/`). |
| **API** | Single endpoint: `POST /v1/analyze` — send an image (file or base64), get `damage_description` and optional `labels`. Same for drone, camera, or inspection. |
| **Pipeline** | PDF reports → JSON + image extraction (e.g. `run_pipeline.py`, `Sample/`). |
| **Docs** | API, deployment, **embedding in drones and cameras**, audience/use cases, **terminology/labels**, **limitations/transparency**, contributing. |

---

## Quick start

### 1. Run the API (mock — no model)

```bash
pip install -r requirements-api.txt
STRUCTURE_API_MOCK=1 python run_api.py
```

- Health: http://localhost:8000/health  
- Swagger: http://localhost:8000/docs  
- Analyze: `curl -X POST http://localhost:8000/v1/analyze -F "file=@image.jpg" -F "source_type=drone"`

### 2. With real model (LLaVA-1.5-7B, GPU recommended)

```bash
STRUCTURE_API_MOCK=0 python run_api.py
# Optional: your fine-tuned checkpoint
STRUCTURE_API_MODEL_NAME=/path/to/checkpoint python run_api.py
```

### 3. Use from your application

- **API reference:** [docs/API.md](docs/API.md)  
- **Example client:** [examples/call_structure_api.py](examples/call_structure_api.py)  
- **Drone and camera integration:** [docs/EMBEDDING_DRONE_AND_CAMERA.md](docs/EMBEDDING_DRONE_AND_CAMERA.md)  
- **Training and deploy:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Documentation index

| Doc | Content |
|-----|--------|
| [docs/API.md](docs/API.md) | Endpoints, request/response, examples (curl, Python, JS). |
| [docs/AUDIENCE_AND_USE_CASES.md](docs/AUDIENCE_AND_USE_CASES.md) | Civil engineers, architects, inspectors; damage detection; labeling critical buildings; inspection workflows. |
| [docs/TERMINOLOGY_AND_LABELS.md](docs/TERMINOLOGY_AND_LABELS.md) | Descriptions vs labels; damage types; how to use outputs to tag critical buildings. |
| [docs/EMBEDDING_DRONE_AND_CAMERA.md](docs/EMBEDDING_DRONE_AND_CAMERA.md) | Embedding the model in drones and cameras (API vs on-device; step-by-step and code). |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Training, serving, and using the API in your app. |
| [docs/LIMITATIONS_AND_TRANSPARENCY.md](docs/LIMITATIONS_AND_TRANSPARENCY.md) | What the model does and does not do; transparency; professional use. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute (bugs, docs, code). |
| [structural_damage_model/README.md](structural_damage_model/README.md) | Model training, evaluation, and metrics. |

---

## Transparency

- **Open development:** Code and docs are public so you can see how the model is used and evaluated.  
- **Limitations:** The model is a screening aid, not a substitute for professional structural assessment. See [docs/LIMITATIONS_AND_TRANSPARENCY.md](docs/LIMITATIONS_AND_TRANSPARENCY.md).  
- **Contributions:** We welcome issues and pull requests; see [CONTRIBUTING.md](CONTRIBUTING.md).
