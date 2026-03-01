#!/usr/bin/env python3
"""
Example: Uygulama tarafında Structure Analysis API nasıl çağrılır.
Tek görsel (dosya veya base64) ve batch örneği.
"""
from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

# API base URL (ortama göre değiştirin)
DEFAULT_BASE = "http://localhost:8000"


def analyze_file(base_url: str, image_path: str, source_type: str = "inspection") -> dict:
    """Tek görsel: dosya yükle."""
    url = f"{base_url.rstrip('/')}/v1/analyze"
    with open(image_path, "rb") as f:
        r = requests.post(url, files={"file": (Path(image_path).name, f)}, data={"source_type": source_type})
    r.raise_for_status()
    return r.json()


def analyze_base64(base_url: str, image_path: str, source_type: str = "google_maps") -> dict:
    """Tek görsel: base64 (örn. Maps tile)."""
    url = f"{base_url.rstrip('/')}/v1/analyze"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = requests.post(url, data={"image_base64": b64, "source_type": source_type})
    r.raise_for_status()
    return r.json()


def analyze_batch(base_url: str, image_paths: list[str], source_type: str = "drone") -> dict:
    """Çoklu görsel (örn. bir drone uçuşu)."""
    url = f"{base_url.rstrip('/')}/v1/analyze/batch"
    files = [("files", (Path(p).name, open(p, "rb"))) for p in image_paths]
    try:
        r = requests.post(url, files=files, data={"source_type": source_type})
        r.raise_for_status()
        return r.json()
    finally:
        for _, (_, f) in files:
            f.close()


def main():
    ap = argparse.ArgumentParser(description="Call Structure Analysis API from app.")
    ap.add_argument("images", nargs="+", help="Image file path(s)")
    ap.add_argument("--base-url", default=DEFAULT_BASE, help="API base URL")
    ap.add_argument("--source", default="inspection", choices=("drone", "google_maps", "inspection"))
    ap.add_argument("--batch", action="store_true", help="Use /v1/analyze/batch for multiple images")
    args = ap.parse_args()

    base = args.base_url
    if args.batch and len(args.images) > 1:
        data = analyze_batch(base, args.images, source_type=args.source)
    elif len(args.images) == 1:
        data = analyze_file(base, args.images[0], source_type=args.source)
    else:
        data = analyze_file(base, args.images[0], source_type=args.source)
        for path in args.images[1:]:
            data["results"].extend(analyze_file(base, path, source_type=args.source)["results"])

    print(data.get("model_id"))
    for i, r in enumerate(data["results"]):
        print(f"[{i+1}] {r['damage_description']}")


if __name__ == "__main__":
    main()
