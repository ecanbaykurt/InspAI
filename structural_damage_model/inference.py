#!/usr/bin/env python3
"""
Run a vision-language model on pipeline images and add damageDescription to each image entry.
Uses Hugging Face transformers; supports LLaVA-style VLMs. Requires GPU for reasonable speed.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
from pathlib import Path

# Optional: only needed when actually running the model
try:
    import torch
    from PIL import Image
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

DEFAULT_PROMPT = (
    "Describe any structural damage or defects visible in this building or infrastructure inspection photo. "
    "Keep the answer to one or two short sentences. If no clear damage is visible, say so."
)


def load_pipeline_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_pipeline_json(path: str, data: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_image_from_entry(img: dict, images_base_dir: str | None) -> Image.Image | None:
    """Load PIL Image from pipeline image entry (publicUrl base64 or storagePath file)."""
    try:
        from PIL import Image
    except ImportError:
        return None

    url = img.get("publicUrl") or ""
    if url.startswith("data:image"):
        # data:image/png;base64,...
        payload = url.split(",", 1)[-1]
        raw = base64.b64decode(payload)
        return Image.open(io.BytesIO(raw)).convert("RGB")

    path = img.get("storagePath") or ""
    if images_base_dir and path:
        name = os.path.basename(path)
        for p in (os.path.join(images_base_dir, name), os.path.join(images_base_dir, name + ".png"), path):
            if os.path.isfile(p):
                return Image.open(p).convert("RGB")
    if path and os.path.isfile(path):
        return Image.open(path).convert("RGB")
    return None


def run_llava_inference(image: "Image.Image", user_prompt: str, model, processor, device: str) -> str:
    """Single image caption with LLaVA 1.5: USER: <<image>>\\n{user_prompt} ASSISTANT:"""
    if processor is None or model is None:
        return "[Model not loaded; install transformers and pass --model-name]"
    # LLaVA 1.5 expects "USER: <<image>>\n<question> ASSISTANT:"
    prompt = f"USER: <image>\n{user_prompt} ASSISTANT:"
    inputs = processor(text=prompt, images=image, return_tensors="pt")
    # Move inputs to same device as model (handle device_map="auto")
    model_device = next(model.parameters()).device
    inputs = {k: v.to(model_device) if hasattr(v, "to") else v for k, v in inputs.items()}
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=150, do_sample=False)
    # Decode only the generated part (after ASSISTANT:)
    generated = processor.decode(out[0], skip_special_tokens=True)
    if "ASSISTANT:" in generated:
        generated = generated.split("ASSISTANT:")[-1]
    return generated.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Add damage descriptions to pipeline JSON using a VLM.")
    ap.add_argument("--input", required=True, help="Path to out_merged.json")
    ap.add_argument("--output", required=True, help="Output JSON path (with damageDescription added)")
    ap.add_argument("--images-base-dir", default="", help="Base dir for image files if not using base64 in JSON")
    ap.add_argument("--model-name", default="llava-hf/llava-1.5-7b-hf", help="HuggingFace model (LLaVA or similar)")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt for the VLM")
    ap.add_argument("--max-images", type=int, default=0, help="Max images to process (0 = all)")
    ap.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto", help="Device (auto = cuda > mps > cpu)")
    ap.add_argument("--dry-run", action="store_true", help="Only load JSON and list images, do not run model")
    ap.add_argument("--mock", action="store_true", help="Skip model: set damageDescription from existing summary (for testing pipeline)")
    args = ap.parse_args()

    if not HAS_TORCH:
        print("Install PyTorch and Pillow to run inference. Example: pip install torch pillow transformers")
        return

    data = load_pipeline_json(args.input)
    images = data.get("images") or []
    base_dir = args.images_base_dir or None

    if args.dry_run:
        print(f"Would process {len(images)} images. First image keys: {list(images[0].keys()) if images else []}")
        return

    if args.mock:
        for img in data.get("images") or []:
            s = (img.get("summary") or "").strip()
            img["damageDescription"] = s if s else "[No summary; run without --mock to use VLM.]"
        save_pipeline_json(args.output, data)
        print(f"Mock: wrote damageDescription from summary for {len(data.get('images') or [])} images to {args.output}")
        return

    if args.device != "auto":
        device = args.device
    elif torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"  # Apple Silicon (if you see mutex errors, use --device cpu)
    else:
        device = "cpu"
    print(f"Using device: {device}")

    model = None
    processor = None
    try:
        from transformers import AutoProcessor, LlavaForConditionalGeneration

        # Use device_map="auto" so large models can use CPU offload on Mac/low-memory machines
        model = LlavaForConditionalGeneration.from_pretrained(
            args.model_name,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device_map="auto" if device == "cpu" else None,
        )
        processor = AutoProcessor.from_pretrained(args.model_name)
        if model.device_map is None:
            model.to(device)
    except Exception as e:
        print(f"Could not load model: {e}. Use --model-name for a compatible VLM or implement a different loader.")
        return

    to_process = images[: args.max_images] if args.max_images else images
    for i, img in enumerate(to_process):
        pil_image = load_image_from_entry(img, base_dir)
        if pil_image is None:
            img["damageDescription"] = "[Could not load image]"
            continue
        desc = run_llava_inference(pil_image, args.prompt, model, processor, device)
        img["damageDescription"] = desc
        print(f"  [{i+1}/{len(to_process)}] {img.get('imageId', '')[:8]}... -> {desc[:60]}...")

    save_pipeline_json(args.output, data)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
