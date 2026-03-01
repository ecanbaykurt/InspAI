#!/usr/bin/env python3
"""
Convert training_captions.jsonl to LLaMA-Factory / ShareGPT / conversation format for VLM fine-tuning.
Output: one JSON (or JSONL) with conversations list; each item has "conversations" and "image" path.
See: https://github.com/hiyouga/LLaMA-Factory# data format for vision-language.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

INSTRUCTION = "Describe any structural damage or defects visible in this building or infrastructure inspection photo. Keep the answer to one or two short sentences."


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert training JSONL to LLaMA-Factory conversation format.")
    ap.add_argument("--input", required=True, help="training_captions.jsonl (image_path, description)")
    ap.add_argument("--output", required=True, help="Output JSON path for LLaMA-Factory dataset")
    ap.add_argument("--instruction", default=INSTRUCTION, help="User instruction for the conversation")
    ap.add_argument("--image-root", default="", help="Optional: strip this prefix from image_path so paths are relative")
    args = ap.parse_args()

    samples = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            image_path = row.get("image_path") or ""
            description = (row.get("description") or "").strip()
            if not image_path or image_path.startswith("base64:"):
                continue  # skip base64 refs; run export_images_from_pipeline.py first
            if args.image_root and image_path.startswith(args.image_root):
                image_path = os.path.relpath(image_path, args.image_root)
            conv = [
                {"from": "human", "value": args.instruction},
                {"from": "gpt", "value": description or "No visible damage."},
            ]
            samples.append({"image": image_path, "conversations": conv})

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(samples)} samples to {args.output}. Use as a LLaMA-Factory vision-language dataset.")


if __name__ == "__main__":
    main()
