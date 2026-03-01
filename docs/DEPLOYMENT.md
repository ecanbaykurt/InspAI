# Structure Analysis: Training, Serving, and Application Usage

Goal: **Train** your own **image detection / structure analysis** model (for drone and Google Maps imagery), **serve** it through a **single API**, and use this API in your application.

## Overall flow

```
[Drone / Maps images] → [Training data] → [Model training] → [Checkpoint]
                                                                   ↓
[Application] ← HTTP ← [Structure Analysis API] ← [Model loading]
```

1. **Data collection:** Images from drone and/or Google Maps; damage/structure labels when possible.
2. **Training:** Use this repo’s `structural_damage_model` data format + LLaMA-Factory (or similar) for VLM fine-tuning.
3. **Serving:** Run the trained model on the same server as `api/`; single API (`/v1/analyze`) for both drone and Maps.
4. **Application:** Your frontend or mobile app only calls this API (file or base64).

---

## 1. Data preparation

- **Drone:** Photos from flights; naming or geo metadata can be preserved (optional).
- **Maps:** Images from Static API / tile download; keep the same `image_path` + `description` format.

Example (compatible with the existing pipeline):

```bash
# Training JSONL from pipeline JSON
python -m structural_damage_model.build_training_data --input path/to/out_merged.json --output structural_damage_model/data/training_captions.jsonl --use-base64
python -m structural_damage_model.export_images_from_pipeline --input path/to/out_merged.json --out-dir structural_damage_model/data/images --jsonl structural_damage_model/data/training_captions.jsonl
```

Fill the `description` fields in `training_captions.jsonl` with real damage descriptions (manually or with an LLM). You can add a `source` column for drone/Maps; the same model is used in training, and `source_type` in the API is for logging/context only.

---

## 2. Model training

- Data format: `structural_damage_model/data/llamafactory_damage_train.json` (LLaMA-Factory conversation format).
- Conversion: JSONL → LLaMA-Factory JSON via `convert_to_llamafactory.py`.
- Training: Fine-tune LLaVA (or your chosen VLM) with LLaMA-Factory; LoRA is recommended.
- Output: A single checkpoint (e.g. `output/checkpoint-final`).

Details: `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`, `structural_damage_model/data/FINETUNING_DATA.md`.

---

## 3. API service

- **Code:** `api/app.py`, `api/model_loader.py`, `api/schemas.py`.
- **Running:**
  - Mock (no model): `STRUCTURE_API_MOCK=1 python run_api.py`
  - BLIP2: `STRUCTURE_API_MODEL=blip2 python run_api.py`
  - LLaVA: `STRUCTURE_API_MODEL=llava python run_api.py`
  - Your checkpoint: `STRUCTURE_API_MODEL=llava STRUCTURE_API_MODEL_NAME=/path/to/checkpoint-final python run_api.py`  
    (model_loader must support the LLaVA path; export in HuggingFace format if needed.)

- **Port:** Default 8000. To change: `uvicorn api.app:app --host 0.0.0.0 --port 8080`.

---

## 4. Using the API in your application

- **Endpoint:** `POST /v1/analyze` (single image: `file` or `image_base64` + `source_type`: `drone` | `google_maps` | `inspection`).
- **Batch:** `POST /v1/analyze/batch` (multiple `files` + `source_type`).

Examples (curl, Python, JS): `docs/API.md`.

In your application:

1. Get an image from drone or Maps (file or base64).
2. Set the source with `source_type`.
3. Use `results[].damage_description` (and later `labels`) from the response.

---

## 5. Production notes

- **GPU:** A CUDA server is recommended for LLaVA and larger models.
- **Environment:** Use the same Python environment as `requirements-api.txt`.
- **Reverse proxy:** Use Nginx/Caddy for TLS and rate limiting; expose the API on `http://127.0.0.1:8000`.
- **Docker (optional):** You can define an image that includes `run_api.py` and the model path; mount the model as a volume if it is large.

This page summarizes the flow from model training to single API serving to application integration; details are in `API.md` and `STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`.
