#!/usr/bin/env python3
"""
Official evaluation: run model on an eval set (image + reference description) and compute
BLEU-4, ROUGE-L, and optional metrics. Outputs eval_results.json and can update data/metrics.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Eval set: JSON array of {path, damageDescription} or JSONL with image_path, description
EVAL_PROMPT = (
    "Describe any structural damage or defects visible in this building or infrastructure inspection photo. "
    "Mention cracks, spalling, corrosion, boarded windows, foundation issues, or pavement damage. "
    "Keep to one or two short sentences. If no clear damage is visible, say so."
)


def load_eval_set(path: str, base_dir: str) -> list[tuple[str, str]]:
    """Return list of (image_path_abs, reference_description)."""
    base = Path(base_dir or ".").resolve()
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if path.endswith(".jsonl"):
        pairs = []
        for line in raw.splitlines():
            if not line:
                continue
            row = json.loads(line)
            img_path = row.get("image_path") or row.get("path") or ""
            ref = (row.get("description") or row.get("damageDescription") or "").strip()
            if not ref or ref.lower().startswith("no description"):
                continue
            abs_path = (base / img_path).resolve() if not os.path.isabs(img_path) else img_path
            if abs_path.exists():
                pairs.append((str(abs_path), ref))
        return pairs
    data = json.loads(raw)
    if isinstance(data, list):
        pairs = []
        for item in data:
            img_path = item.get("path") or item.get("image_path") or ""
            ref = (item.get("damageDescription") or item.get("description") or "").strip()
            if not ref:
                continue
            abs_path = (base / img_path).resolve() if img_path and not os.path.isabs(img_path) else img_path
            if abs_path and Path(abs_path).exists():
                pairs.append((str(abs_path), ref))
        return pairs
    return []


def tokenize(s: str) -> list[str]:
    return s.lower().split()


def bleu4(reference: list[str], hypothesis: list[str]) -> float:
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    except ImportError:
        return 0.0
    if not hypothesis:
        return 0.0
    # sentence_bleu expects [reference_list] (one ref) and hypothesis_list
    try:
        return sentence_bleu(
            [reference], hypothesis,
            weights=(0.25, 0.25, 0.25, 0.25),
            smoothing_function=SmoothingFunction().method1,
        )
    except Exception:
        return 0.0


def rouge_l(reference: list[str], hypothesis: list[str]) -> float:
    try:
        from rouge_score import rouge_scorer
    except ImportError:
        return 0.0
    if not hypothesis or not reference:
        return 0.0
    ref_str = " ".join(reference)
    hyp_str = " ".join(hypothesis)
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    s = scorer.score(ref_str, hyp_str)
    return s["rougeL"].fmeasure


def run_model_on_image(image_path: str, model, processor, run_fn, device: str) -> str:
    from PIL import Image
    img = Image.open(image_path).convert("RGB")
    return run_fn(img, EVAL_PROMPT, model, processor, device)


def main() -> None:
    ap = argparse.ArgumentParser(description="Official eval: BLEU-4, ROUGE-L on eval set.")
    ap.add_argument("--eval-file", required=True, help="JSON array [{path, damageDescription}] or JSONL with image_path, description")
    ap.add_argument("--base-dir", default="", help="Base dir for relative image paths (default: cwd)")
    ap.add_argument("--model", choices=("blip2", "llava"), default="blip2")
    ap.add_argument("--model-name", default="")
    ap.add_argument("--output", default="structural_damage_model/data/eval_results.json", help="Write results here")
    ap.add_argument("--update-metrics", action="store_true", help="Update data/metrics.json from results for README")
    ap.add_argument("--no-inference", action="store_true", help="Skip model; use existing predictions in eval file (e.g. 'prediction' key)")
    args = ap.parse_args()

    base_dir = args.base_dir or os.getcwd()
    pairs = load_eval_set(args.eval_file, base_dir)
    if not pairs:
        print("No valid (image_path, reference) pairs found. Check --eval-file and --base-dir.", file=sys.stderr)
        sys.exit(1)
    print(f"Eval set: {len(pairs)} samples")

    predictions = []
    if args.no_inference:
        # Load predictions in same order as pairs (from same file)
        with open(args.eval_file, "r", encoding="utf-8") as f:
            data = json.load(f) if args.eval_file.endswith(".json") else [json.loads(l) for l in f if l.strip()]
        if not isinstance(data, list):
            data = []
        # Build (path_abs, ref) to match pairs order, and collect prediction per item
        base = Path(base_dir or ".").resolve()
        for item in data:
            img_path = item.get("path") or item.get("image_path") or ""
            ref = (item.get("damageDescription") or item.get("description") or "").strip()
            if not ref or ref.lower().startswith("no description"):
                continue
            abs_path = (base / img_path).resolve() if img_path and not os.path.isabs(img_path) else img_path
            if not abs_path or not Path(abs_path).exists():
                continue
            pred = (item.get("prediction") or "").strip()
            if not pred:
                print("no-inference: missing 'prediction' in eval file.", file=sys.stderr)
                sys.exit(1)
            predictions.append(pred)
        if len(predictions) != len(pairs):
            print("no-inference: prediction count mismatch.", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            import torch
            from PIL import Image
        except ImportError:
            print("Install: pip install torch pillow nltk rouge-score", file=sys.stderr)
            sys.exit(1)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if args.model == "blip2":
            from transformers import Blip2ForConditionalGeneration, Blip2Processor
            name = args.model_name or "Salesforce/blip2-opt-2.7b"
            processor = Blip2Processor.from_pretrained(name)
            model = Blip2ForConditionalGeneration.from_pretrained(name)
            model.to(device)
            def run_fn(img, prompt, m, p, d):
                inp = p(images=img, text=prompt, return_tensors="pt").to(d)
                out = m.generate(**inp, max_new_tokens=100)
                return p.decode(out[0], skip_special_tokens=True).strip()
        else:
            from transformers import AutoProcessor, LlavaForConditionalGeneration
            name = args.model_name or "llava-hf/llava-1.5-7b-hf"
            processor = AutoProcessor.from_pretrained(name)
            model = LlavaForConditionalGeneration.from_pretrained(name, torch_dtype=torch.float16 if device == "cuda" else torch.float32, device_map="auto" if device == "cpu" else None)
            if getattr(model, "device_map", None) is None:
                model.to(device)
            def run_fn(img, prompt, m, p, d):
                prompt_f = f"USER: <image>\n{prompt} ASSISTANT:"
                inp = p(text=prompt_f, images=img, return_tensors="pt")
                dev = next(m.parameters()).device
                inp = {k: v.to(dev) if hasattr(v, "to") else v for k, v in inp.items()}
                with torch.inference_mode():
                    out = m.generate(**inp, max_new_tokens=150, do_sample=False)
                gen = p.decode(out[0], skip_special_tokens=True)
                if "ASSISTANT:" in gen:
                    gen = gen.split("ASSISTANT:")[-1]
                return gen.strip()
        for i, (img_path, ref) in enumerate(pairs):
            pred = run_model_on_image(img_path, model, processor, run_fn, device)
            predictions.append(pred)
            print(f"  [{i+1}/{len(pairs)}] pred: {pred[:60]}...")

    # Compute metrics (corpus-level)
    refs_tok = [tokenize(ref) for _, ref in pairs]
    hyps_tok = [tokenize(p) for p in predictions]
    bleu_scores = []
    rouge_scores = []
    for ref_t, hyp_t in zip(refs_tok, hyps_tok):
        bleu_scores.append(bleu4(ref_t, hyp_t))  # ref_t, hyp_t are list[str]
        rouge_scores.append(rouge_l(ref_t, hyp_t))
    bleu4_mean = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
    rouge_l_mean = sum(rouge_scores) / len(rouge_scores) if rouge_scores else 0.0

    results = {
        "n_samples": len(pairs),
        "eval_file": args.eval_file,
        "model": args.model,
        "metrics": {
            "BLEU-4": round(bleu4_mean, 4),
            "ROUGE-L": round(rouge_l_mean, 4),
        },
        "per_sample": [
            {"path": pairs[i][0], "reference": pairs[i][1][:200], "prediction": predictions[i][:200], "BLEU-4": round(bleu_scores[i], 4), "ROUGE-L": round(rouge_scores[i], 4)}
            for i in range(len(pairs))
        ],
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"BLEU-4: {results['metrics']['BLEU-4']:.4f}  ROUGE-L: {results['metrics']['ROUGE-L']:.4f}")
    print(f"Results written to {out_path}")

    if args.update_metrics:
        metrics_path = Path(args.output).parent / "metrics.json"
        # Merge into metrics.json for update_readme_metrics
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        else:
            metrics = {}
        metrics["BLEU-4 (caption vs reference)"] = {"value": f"{results['metrics']['BLEU-4']:.2f}", "notes": f"Official eval, n={results['n_samples']}; {args.model}."}
        metrics["ROUGE-L (caption vs reference)"] = {"value": f"{results['metrics']['ROUGE-L']:.2f}", "notes": f"Same eval set."}
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"Updated {metrics_path}")


if __name__ == "__main__":
    main()
