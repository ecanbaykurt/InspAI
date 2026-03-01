#!/usr/bin/env python3
"""
Test structural damage description on standalone image files (no pipeline JSON).
Use for quick testing with a folder or list of image paths.
Supports: --model blip2 (lightweight, works on Mac/CPU) or llava (needs GPU for speed).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import torch
    from PIL import Image
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

PROMPT = (
    "Describe any structural damage or defects visible in this building or infrastructure inspection photo. "
    "Mention cracks, spalling, corrosion, boarded windows, foundation issues, or pavement damage. "
    "Keep to one or two short sentences. If no clear damage is visible, say so."
)


def collect_image_paths(paths_or_dirs: list[str]) -> list[str]:
    out = []
    for p in paths_or_dirs:
        if not os.path.exists(p):
            continue
        if os.path.isfile(p):
            low = p.lower()
            if low.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
                out.append(p)
        else:
            for f in sorted(Path(p).iterdir()):
                if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                    out.append(str(f))
    return out


def run_blip2(image: "Image.Image", prompt: str, model, processor, device: str) -> str:
    """Use BLIP2 for image captioning (lightweight, works on CPU/Mac)."""
    # BLIP2 uses a different API: we do image captioning with a prompt as context
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=100)
    return processor.decode(out[0], skip_special_tokens=True).strip()


def run_llava(image: "Image.Image", prompt: str, model, processor, device: str) -> str:
    """LLaVA 1.5 style."""
    import torch as _torch
    prompt_formatted = f"USER: <image>\n{prompt} ASSISTANT:"
    inputs = processor(text=prompt_formatted, images=image, return_tensors="pt")
    model_device = next(model.parameters()).device
    inputs = {k: v.to(model_device) if hasattr(v, "to") else v for k, v in inputs.items()}
    with _torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=150, do_sample=False)
    generated = processor.decode(out[0], skip_special_tokens=True)
    if "ASSISTANT:" in generated:
        generated = generated.split("ASSISTANT:")[-1]
    return generated.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Run structural damage description on image files.")
    ap.add_argument("images", nargs="*", help="Image file paths or directories containing images")
    ap.add_argument("--image-dir", help="Directory of images (alternative to positional args)")
    ap.add_argument("--output", "-o", help="Write results to this JSON file")
    ap.add_argument("--model", choices=("blip2", "llava"), default="blip2",
                    help="blip2 = lightweight (Mac/CPU); llava = better quality, needs GPU")
    ap.add_argument("--model-name", default="",
                    help="HuggingFace model name (default: Salesforce/blip2-opt-2.7b for blip2)")
    args = ap.parse_args()

    paths = list(args.images or [])
    if args.image_dir:
        paths.append(args.image_dir)
    paths = collect_image_paths(paths)
    if not paths:
        print("No image files found. Pass image paths or --image-dir.", file=sys.stderr)
        sys.exit(1)

    if not HAS_DEPS:
        print("Install: pip install torch pillow transformers", file=sys.stderr)
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
    if args.model == "llava" and device == "mps":
        device = "cpu"  # avoid known Mac crash with LLaVA
    print(f"Using device: {device}, model: {args.model}")

    model = None
    processor = None
    if args.model == "blip2":
        from transformers import Blip2ForConditionalGeneration, Blip2Processor
        name = args.model_name or "Salesforce/blip2-opt-2.7b"
        processor = Blip2Processor.from_pretrained(name)
        model = Blip2ForConditionalGeneration.from_pretrained(name)
        model.to(device)
        run_fn = run_blip2
    else:
        from transformers import AutoProcessor, LlavaForConditionalGeneration
        name = args.model_name or "llava-hf/llava-1.5-7b-hf"
        processor = AutoProcessor.from_pretrained(name)
        model = LlavaForConditionalGeneration.from_pretrained(
            name,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device_map="auto" if device == "cpu" else None,
        )
        if getattr(model, "device_map", None) is None:
            model.to(device)
        run_fn = run_llava

    results = []
    for i, path in enumerate(paths):
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            results.append({"path": path, "error": str(e), "damageDescription": None})
            print(f"[{i+1}] {os.path.basename(path)}: ERROR {e}")
            continue
        desc = run_fn(img, PROMPT, model, processor, device)
        results.append({"path": path, "damageDescription": desc, "error": None})
        print(f"[{i+1}] {os.path.basename(path)}:\n   {desc}\n")

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
