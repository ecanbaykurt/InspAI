#!/usr/bin/env python3
"""
Build training data (JSONL) for the structural damage description model from
pipeline output (out_merged.json). Each line: {"image_path": "...", "description": "...", ...}.
If descriptions are missing, outputs a placeholder so you can fill them (manually or via another tool).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path


def load_pipeline_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def image_to_training_row(
    img: dict,
    images_base_dir: str | None,
    use_base64_from_json: bool,
    default_description: str = "No description yet.",
) -> dict | None:
    """Build one training row from a pipeline image entry."""
    image_id = img.get("imageId", "")
    storage_path = img.get("storagePath", "")
    summary = (img.get("summary") or "").strip()
    description = summary if summary and "No explicit condition" not in summary else default_description

    # Resolve image path or base64
    image_path = None
    if images_base_dir and storage_path:
        # storagePath might be "memory/uuid" or "Sample/extracted_images/uuid.png"
        name = os.path.basename(storage_path)
        candidate = os.path.join(images_base_dir, name)
        if os.path.isfile(candidate):
            image_path = candidate
        # try with .png/.jpg if no extension
        for ext in (".png", ".jpg", ".jpeg"):
            if os.path.isfile(candidate + ext):
                image_path = candidate + ext
                break
    if use_base64_from_json and img.get("publicUrl", "").startswith("data:image"):
        # Store as a path placeholder; actual training code can load from JSON
        image_path = f"base64:{image_id}"

    if not image_path and not use_base64_from_json:
        return None

    return {
        "image_id": image_id,
        "image_path": image_path or "",
        "description": description,
        "page_number": img.get("pageNumber"),
        "image_type": img.get("imageType"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build training JSONL from pipeline JSON.")
    ap.add_argument("--input", required=True, help="Path to out_merged.json")
    ap.add_argument("--output", required=True, help="Output JSONL path")
    ap.add_argument("--images-base-dir", default="", help="Base dir for image paths (storagePath basename appended)")
    ap.add_argument("--use-base64", action="store_true", help="If set, allow image from publicUrl base64 in JSON")
    ap.add_argument("--placeholder-description", default="No description yet.", help="Description when none in pipeline")
    args = ap.parse_args()

    data = load_pipeline_json(args.input)
    images = data.get("images") or []
    base_dir = args.images_base_dir or None

    rows = []
    for img in images:
        row = image_to_training_row(
            img,
            images_base_dir=base_dir,
            use_base64_from_json=args.use_base64,
            default_description=args.placeholder_description,
        )
        if row and (row.get("image_path") or row.get("image_id")):
            rows.append(row)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
