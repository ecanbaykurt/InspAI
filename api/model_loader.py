"""
Load and run the structure/damage model once; used by the API.
Supports mock mode (no GPU) and blip2/llava backends.
"""
from __future__ import annotations

import io
import os
from typing import Any, Optional

# Lazy imports for torch/transformers to allow server to start in mock mode
PROMPT = (
    "Describe any structural damage or defects visible in this building or infrastructure inspection photo. "
    "Mention cracks, spalling, corrosion, boarded windows, foundation issues, or pavement damage. "
    "Keep to one or two short sentences. If no clear damage is visible, say so."
)

_model_state: dict[str, Any] = {"model": None, "processor": None, "device": "cpu", "backend": None}


def get_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def load_model(backend: str = "blip2", model_name: Optional[str] = None, use_mock: bool = False) -> None:
    """Load model once. backend: blip2 | llava. use_mock: if True, no real model loaded."""
    if use_mock or os.environ.get("STRUCTURE_API_MOCK") == "1":
        _model_state["backend"] = "mock"
        _model_state["model"] = None
        _model_state["processor"] = None
        _model_state["device"] = "cpu"
        return

    if _model_state["model"] is not None and _model_state["backend"] == backend:
        return

    import torch
    device = get_device()
    if backend == "llava" and device == "mps":
        device = "cpu"

    if backend == "blip2":
        from transformers import Blip2ForConditionalGeneration, Blip2Processor
        name = model_name or "Salesforce/blip2-opt-2.7b"
        _model_state["processor"] = Blip2Processor.from_pretrained(name)
        _model_state["model"] = Blip2ForConditionalGeneration.from_pretrained(name)
        _model_state["model"].to(device)
        _model_state["device"] = device
        _model_state["backend"] = "blip2"
        _model_state["model_id"] = name
    else:
        from transformers import AutoProcessor, LlavaForConditionalGeneration
        name = model_name or "llava-hf/llava-1.5-7b-hf"
        _model_state["processor"] = AutoProcessor.from_pretrained(name)
        _model_state["model"] = LlavaForConditionalGeneration.from_pretrained(
            name,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device_map="auto" if device == "cpu" else None,
        )
        if getattr(_model_state["model"], "device_map", None) is None:
            _model_state["model"].to(device)
        _model_state["device"] = device
        _model_state["backend"] = "llava"
        _model_state["model_id"] = name


def run_inference(image_bytes: bytes, source_type: Optional[str] = None) -> dict:
    """
    Run damage description on one image. image_bytes: raw PNG/JPEG bytes.
    Returns dict with damage_description, model_id, optional labels.
    """
    from PIL import Image

    state = _model_state
    if state.get("backend") == "mock" or state.get("model") is None:
        return {
            "damage_description": "[Mock] Run API with real model (set STRUCTURE_API_MOCK=0 and backend blip2/llava).",
            "source_type": source_type,
            "labels": [],
            "model_id": "mock",
        }

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    device = state["device"]
    model = state["model"]
    processor = state["processor"]
    backend = state["backend"]

    if backend == "blip2":
        inputs = processor(images=img, text=PROMPT, return_tensors="pt").to(device)
        out = model.generate(**inputs, max_new_tokens=100)
        desc = processor.decode(out[0], skip_special_tokens=True).strip()
    else:
        import torch
        prompt = f"USER: <image>\n{PROMPT} ASSISTANT:"
        inputs = processor(text=prompt, images=img, return_tensors="pt")
        model_device = next(model.parameters()).device
        inputs = {k: v.to(model_device) if hasattr(v, "to") else v for k, v in inputs.items()}
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=150, do_sample=False)
        generated = processor.decode(out[0], skip_special_tokens=True)
        if "ASSISTANT:" in generated:
            generated = generated.split("ASSISTANT:")[-1]
        desc = generated.strip()

    return {
        "damage_description": desc,
        "source_type": source_type,
        "labels": [],
        "model_id": state.get("model_id"),
    }
