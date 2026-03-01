#!/usr/bin/env python3
"""
Export images from pipeline JSON (base64 in publicUrl) to a directory and optionally
rewrite training_captions.jsonl to use file paths instead of base64:image_id refs.
Use this so fine-tuning tools (LLaMA-Factory, etc.) can read images from disk.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Export pipeline images from JSON to a directory.")
    ap.add_argument("--input", required=True, help="Path to out_merged.json")
    ap.add_argument("--out-dir", required=True, help="Directory to write image files (e.g. data/images)")
    ap.add_argument("--jsonl", default="", help="If set, rewrite this JSONL to use file paths; else only export images")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    images = data.get("images") or []
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    id_to_path = {}

    for img in images:
        url = img.get("publicUrl") or ""
        if not url.startswith("data:image"):
            continue
        image_id = img.get("imageId", "")
        ext = "png"
        if "jpeg" in url or "jpg" in url:
            ext = "jpg"
        payload = url.split(",", 1)[-1]
        raw = base64.b64decode(payload)
        out_path = os.path.join(args.out_dir, f"{image_id}.{ext}")
        with open(out_path, "wb") as f:
            f.write(raw)
        id_to_path[image_id] = out_path

    print(f"Exported {len(id_to_path)} images to {args.out_dir}")

    if not args.jsonl or not os.path.isfile(args.jsonl):
        return

    # Rewrite JSONL: replace base64:image_id with actual path
    rows = []
    with open(args.jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            path = row.get("image_path") or ""
            if path.startswith("base64:") and path.replace("base64:", "") in id_to_path:
                row["image_path"] = id_to_path[path.replace("base64:", "")]
            rows.append(row)

    with open(args.jsonl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Updated {args.jsonl} with file paths.")


if __name__ == "__main__":
    main()
