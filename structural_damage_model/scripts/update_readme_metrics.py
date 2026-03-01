#!/usr/bin/env python3
"""
Update the metrics table in structural_damage_model/README.md from a JSON file.
Run after you have new eval results; keeps the README in sync with real numbers.

Usage:
  python -m structural_damage_model.scripts.update_readme_metrics structural_damage_model/data/metrics.json

metrics.json example:
  {
    "BLEU-4 (caption vs reference)": {"value": "0.31", "notes": "Internal eval set, 50 samples; LLaVA-1.5-7b zero-shot."},
    "ROUGE-L (caption vs reference)": {"value": "0.42", "notes": "Same set."},
    "Inference (LLaVA-1.5-7B, GPU)": {"value": "~1.2 s/image", "notes": "A100; batch=1."}
  }
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Update README metrics table from JSON.")
    ap.add_argument("metrics_json", help="Path to metrics.json")
    ap.add_argument("--readme", default=None, help="Path to README.md (default: structural_damage_model/README.md)")
    args = ap.parse_args()

    readme_path = Path(args.readme) if args.readme else Path(__file__).resolve().parent.parent / "README.md"
    with open(args.metrics_json, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the metrics table: from "| Metric |" to next "---" or "## "
    table_start = "| Metric | Value | Notes |"
    table_end_markers = ("\n---\n", "\n## ")
    start = content.find(table_start)
    if start == -1:
        print("Metrics table not found in README.")
        return
    # Find end of table (next line that doesn't start with "|")
    pos = content.find("\n", start) + 1
    while pos < len(content):
        line = content[pos:content.find("\n", pos) or len(content)]
        if line.strip() and not line.strip().startswith("|"):
            break
        if line.strip().startswith("---") or line.strip().startswith("##"):
            break
        pos = content.find("\n", pos) + 1 or len(content)

    end = pos
    new_rows = [table_start, "|--------|--------|--------|"]
    for metric, data in metrics.items():
        val = data.get("value", "")
        notes = data.get("notes", "")
        if metric.startswith("_section"):
            new_rows.append(f"| {notes} | | |")
        else:
            new_rows.append(f"| {metric} | **{val}** | {notes} |")
    new_table = "\n".join(new_rows) + "\n"
    new_content = content[:start] + new_table + content[end:]
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {len(metrics)} rows in {readme_path}")


if __name__ == "__main__":
    main()
