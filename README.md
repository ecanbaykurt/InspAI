# Structure Analyse

**Image detection model** for structural damage / structure analysis (drone and Google Maps imagery), served through a **single API**; your application calls this API.

## Components

| Component | Description |
|-----------|-------------|
| **Pipeline** | PDF reports → JSON + image extraction (e.g. `run_pipeline.py`, `Sample/`) |
| **Model** | Structural damage description (VLM: LLaVA/BLIP2, fine-tune: `structural_damage_model/`) |
| **API** | Single endpoint: `POST /v1/analyze` — drone / Maps / inspection images → damage description |
| **Application** | Calls the API (file or base64); see `docs/API.md` and `examples/call_structure_api.py` |

## Quick start

### 1. Run the API (mock — no model)

```bash
pip install -r requirements-api.txt
STRUCTURE_API_MOCK=1 python run_api.py
# or: STRUCTURE_API_MOCK=1 uvicorn api.app:app --host 0.0.0.0 --port 8000
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

### 3. Using the API from your application

- **Documentation:** `docs/API.md`  
- **Example client:** `examples/call_structure_api.py`  
- **Training + deploy:** `docs/DEPLOYMENT.md`

## Target flow

1. **Training:** Drone/Maps data → `structural_damage_model` data format → fine-tune with LLaMA-Factory → checkpoint.  
2. **Serving:** Load the checkpoint with this API; the same API is used for drone and Maps.  
3. **Application:** Send image (file or base64) + `source_type` (`drone` | `google_maps` | `inspection`) to `POST /v1/analyze`; use the response `damage_description`.

Details: `docs/API.md`, `docs/DEPLOYMENT.md`, `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`.
