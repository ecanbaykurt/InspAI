"""
Structure Analysis API — single endpoint for image detection / structure analysis.
Supports drone and Google Maps images; same model and response format.
"""
from __future__ import annotations

import base64
import io
import os
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalysisResult, AnalyzeResponse, ImageSourceType
from api.model_loader import load_model, run_inference

app = FastAPI(
    title="Structure Analysis API",
    description="Image detection / structure analysis for drone and Google Maps imagery. Returns damage descriptions and optional labels.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config from env: single served model (LLaVA-1.5-7B by default)
API_MODEL_NAME = os.environ.get("STRUCTURE_API_MODEL_NAME") or None
API_MOCK = os.environ.get("STRUCTURE_API_MOCK", "0").strip().lower() in ("1", "true", "yes")


@app.on_event("startup")
def startup():
    load_model(model_name=API_MODEL_NAME, use_mock=API_MOCK)


@app.get("/health")
def health():
    from api.model_loader import DEFAULT_MODEL_ID
    return {"status": "ok", "model": DEFAULT_MODEL_ID, "mock": API_MOCK}


@app.get("/v1/model")
def model_info():
    from api.model_loader import _model_state, DEFAULT_MODEL_ID
    return {
        "model_id": _model_state.get("model_id") or DEFAULT_MODEL_ID,
        "mock": API_MOCK,
    }


@app.post("/v1/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: Optional[UploadFile] = File(None, description="Image file (PNG/JPEG)"),
    image_base64: Optional[str] = Form(None, description="Image as base64 string (alternative to file)"),
    source_type: Optional[str] = Form("inspection", description="One of: drone, google_maps, inspection"),
):
    """
    Analyze one or more images for structural damage.
    Send either:
    - **file**: multipart file upload (single image), or
    - **image_base64**: form field with base64-encoded image (single image).

    **source_type**: `drone` | `google_maps` | `inspection` (for logging/context; same model used).
    """
    if file is None and not image_base64:
        raise HTTPException(status_code=400, detail="Provide either 'file' or 'image_base64'")

    images_data: list[tuple[bytes, str]] = []  # (bytes, source_type)

    if file:
        raw = await file.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        images_data.append((raw, source_type or "inspection"))

    if image_base64:
        try:
            raw = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64: {e}")
        if not raw:
            raise HTTPException(status_code=400, detail="Base64 image is empty")
        images_data.append((raw, source_type or "inspection"))

    # Normalize source_type
    try:
        st = ImageSourceType(source_type or "inspection")
    except ValueError:
        st = ImageSourceType.INSPECTION
    source_str = st.value

    results = []
    for img_bytes, st_val in images_data:
        out = run_inference(img_bytes, source_type=st_val)
        results.append(
            AnalysisResult(
                damage_description=out["damage_description"],
                source_type=out.get("source_type"),
                labels=out.get("labels") or [],
                model_id=out.get("model_id"),
            )
        )

    return AnalyzeResponse(
        success=True,
        results=results,
        model_id=results[0].model_id if results else None,
    )


# Batch: multiple files in one request
@app.post("/v1/analyze/batch", response_model=AnalyzeResponse)
async def analyze_batch(
    files: list[UploadFile] = File(..., description="Multiple image files"),
    source_type: Optional[str] = Form("inspection"),
):
    """Analyze multiple images in one request (e.g. drone flight set or Maps tiles)."""
    if not files:
        raise HTTPException(status_code=400, detail="Provide at least one file")
    st = source_type or "inspection"
    results = []
    for f in files:
        raw = await f.read()
        if not raw:
            results.append(
                AnalysisResult(damage_description="[Empty file]", source_type=st, labels=[], model_id=None)
            )
            continue
        out = run_inference(raw, source_type=st)
        results.append(
            AnalysisResult(
                damage_description=out["damage_description"],
                source_type=out.get("source_type"),
                labels=out.get("labels") or [],
                model_id=out.get("model_id"),
            )
        )
    return AnalyzeResponse(success=True, results=results, model_id=results[0].model_id if results else None)
