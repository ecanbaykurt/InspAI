# Structure Analysis API

A **single API** for structure/damage analysis (image detection) on **drone** and **Google Maps** images. You train and serve the model yourself; your application only calls this API.

## Summary

- **Endpoint:** `POST /v1/analyze` (single image: file or base64) and `POST /v1/analyze/batch` (multiple files).
- **Source type:** `source_type`: `drone` | `google_maps` | `inspection` (same model, for context only).
- **Response:** For each image: `damage_description` (text) and optional `labels` (e.g. damage class + confidence). Use these to tag assets or flag critical buildings; see [TERMINOLOGY_AND_LABELS.md](TERMINOLOGY_AND_LABELS.md).

## Running the service

The API serves a **single model**: **LLaVA-1.5-7B** (best description quality). Optionally override with your fine-tuned checkpoint via `STRUCTURE_API_MODEL_NAME`.

```bash
# Dependencies (once)
pip install -r requirements-api.txt

# Mock mode (no model, for testing)
STRUCTURE_API_MOCK=1 python run_api.py

# Real model (LLaVA-1.5-7B; GPU recommended)
python run_api.py

# Your own checkpoint (e.g. fine-tuned LLaVA)
STRUCTURE_API_MODEL_NAME=/path/to/checkpoint python run_api.py
```

Default: `http://0.0.0.0:8000`. Health: `GET http://localhost:8000/health`.

## Endpoints

### GET /health

Service and model status.

**Response:** `{ "status": "ok", "model": "llava-hf/llava-1.5-7b-hf", "mock": false }`

### GET /v1/model

Information about the loaded model (always LLaVA-1.5-7B or your custom checkpoint).

**Response:** `{ "model_id": "llava-hf/llava-1.5-7b-hf", "mock": false }`

### POST /v1/analyze

Analyze one (or two) images. Send the image as **file** or **image_base64**.

**Form / multipart:**

| Field          | Type   | Required | Description                                      |
|----------------|--------|----------|--------------------------------------------------|
| file           | file   | No*      | Image file (PNG/JPEG)                            |
| image_base64   | string | No*      | Base64-encoded image                              |
| source_type    | string | No       | `drone` \| `google_maps` \| `inspection` (default: inspection) |

\* At least one of `file` or `image_base64` is required.

**Response:** `AnalyzeResponse`

```json
{
  "success": true,
  "results": [
    {
      "damage_description": "Cracks visible along the foundation; two windows boarded up.",
      "source_type": "drone",
      "labels": [],
      "model_id": "Salesforce/blip2-opt-2.7b"
    }
  ],
  "model_id": "Salesforce/blip2-opt-2.7b"
}
```

### POST /v1/analyze/batch

Multiple images (e.g. one drone flight or multiple Maps tiles).

**Form / multipart:**

| Field        | Type   | Description                          |
|--------------|--------|--------------------------------------|
| files        | files  | Multiple image files                 |
| source_type  | string | `drone` \| `google_maps` \| `inspection` |

**Response:** Same `AnalyzeResponse`; one entry in `results` per image.

## Using the API from your application

### cURL (single file)

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -F "file=@path/to/drone_photo.jpg" \
  -F "source_type=drone"
```

### cURL (base64)

```bash
# Encode image to base64 (e.g. macOS)
BASE64=$(base64 -i path/to/image.png)
curl -X POST http://localhost:8000/v1/analyze \
  -F "image_base64=$BASE64" \
  -F "source_type=google_maps"
```

### JavaScript (fetch)

```javascript
const form = new FormData();
form.append("file", imageFile);  // File from <input type="file"> or drag-drop
form.append("source_type", "drone");

const res = await fetch("http://localhost:8000/v1/analyze", {
  method: "POST",
  body: form,
});
const data = await res.json();
console.log(data.results[0].damage_description);
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/v1/analyze"
with open("drone_photo.jpg", "rb") as f:
    r = requests.post(url, files={"file": f}, data={"source_type": "drone"})
r.raise_for_status()
print(r.json()["results"][0]["damage_description"])
```

### Python (batch, base64 — e.g. Google Maps tiles)

```python
import base64
import requests

def analyze_image(image_bytes: bytes, source: str = "google_maps") -> str:
    r = requests.post(
        "http://localhost:8000/v1/analyze",
        data={
            "image_base64": base64.b64encode(image_bytes).decode(),
            "source_type": source,
        },
    )
    r.raise_for_status()
    return r.json()["results"][0]["damage_description"]

# Usage
with open("tile.png", "rb") as f:
    desc = analyze_image(f.read(), source="google_maps")
```

## Model training and serving

1. **Data:** Drone and/or Maps images + labels (see `structural_damage_model/data/`, `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`).
2. **Training:** Fine-tune a VLM (LLaVA/BLIP2, etc.) with LLaMA-Factory or similar; save a single checkpoint.
3. **Serving:** To load your trained model, set your model path with `STRUCTURE_API_MODEL_NAME`; the API keeps the same endpoints.
4. **Deploy:** Run `run_api.py` or `uvicorn api.app:app --host 0.0.0.0 --port 8000` on your server; use a reverse proxy (nginx) in production and Docker if needed (see `docs/DEPLOYMENT.md`).

## OpenAPI (Swagger)

With the service running: **http://localhost:8000/docs**
