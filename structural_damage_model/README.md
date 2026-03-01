# InspAI — Structural Damage Description Model

**One model. Drone, Maps, inspection. Open source.**

Describe structural damage in 1–2 sentences from a single image — no API keys, run on your own hardware. Built for the SafeStructure pipeline and the [Structure Analysis API](../api/).

---

| **License** | **Python** | **Backend** |
|-------------|-----------|-------------|
| MIT | 3.9+ | PyTorch · Hugging Face |

**Quick routes**

| [Getting started](#getting-started) | [One-click setup](#one-click-setup) | [Inference](#inference) | [Fine-tune](#fine-tune) | [API](#api--servis) | [Docs](#docs) |
|------------------------------------|-------------------------------------|--------------------------|--------------------------|----------------------|----------------|

---

## What InspAI does

InspAI is the **vision-language component** for structural damage analysis: it takes inspection images (from drone, Google Maps, or report PDFs) and outputs short natural-language descriptions of damage — cracks, spallation, corrosion, boarded windows, foundation issues — so your pipeline or app can use a single, consistent format.

**Design:**

- **VLM-based** — LLaVA or BLIP2; natural sentences, not just class tags.
- **Pipeline-integrated** — Feeds on `out_merged.json` images; writes `damageDescription`.
- **Drone & Maps ready** — Same model and [API](../docs/API.md) for all sources; `source_type` for context only.
- **LoRA fine-tunable** — Train on your own labels and terminology (LLaMA-Factory).

---

## Metrics & benchmarks

Accuracy and performance for the current backends and related benchmarks:

| Metric | Value | Notes |
|--------|--------|--------|
| **Description model** | | |
| BLEU-4 (caption vs reference) | **0.11** | Official eval, n=3 (eval_set_with_predictions); see `run_eval.py` and `data/eval_results.json`. |
| ROUGE-L (caption vs reference) | **0.59** | Same eval set. |
| Inference (LLaVA-1.5-7B, GPU) | **~1.2 s/image** | A100; batch=1. |
| Inference (BLIP2-2.7B, GPU) | **~0.4 s/image** | Lighter, faster. |
| Model size (LLaVA-1.5-7B) | **~14 GB** | FP16. |
| Model size (BLIP2-2.7B) | **~5.5 GB** | FP16. |
| **Related segmentation (dacl10k)** | | |
| mIoU (best baseline, WACV 2024) | **0.42** | 12 damage + 6 component classes; bridge imagery. |
| Dataset size | **9,920 images** | For detection/segmentation baselines. |

*Official numbers from `python -m structural_damage_model.run_eval --eval-file Test/test_images/eval_set_with_predictions.json --no-inference --output data/eval_results.json --update-metrics`. Re-run with your model (omit `--no-inference`) to refresh. To edit the table from JSON: `python -m structural_damage_model.scripts.update_readme_metrics data/metrics.json`.*

---

## Getting started

**1. Install**

```bash
pip install -r structural_damage_model/requirements.txt
```

**2. Run inference (mock — no model)**

```bash
python -m structural_damage_model.inference --input Test/out_merged.json --output Test/out_with_descriptions.json --mock
```

**3. Run inference (real model, GPU recommended)**

```bash
python -m structural_damage_model.inference --input Test/out_merged.json --output Test/out_with_descriptions.json --model-name llava-hf/llava-1.5-7b-hf
```

Use `--max-images N` to limit images. On **macOS** if you see a crash, use `--device cpu` or `--mock`.

---

## One-click setup

From the **repo root**, prepare data and export images in one go (requires a pipeline JSON with images):

```bash
# One command (default: Test/out_merged.json)
bash structural_damage_model/quick_setup.sh

# Or pass your pipeline JSON
bash structural_damage_model/quick_setup.sh path/to/out_merged.json
```

Then edit `structural_damage_model/data/training_captions.jsonl` (replace `"No description yet."` with real descriptions) and re-run the convert step:

```bash
python -m structural_damage_model.convert_to_llamafactory --input structural_damage_model/data/training_captions.jsonl --output structural_damage_model/data/llamafactory_damage_train.json --image-root structural_damage_model/data
```

See [data/FINETUNING_DATA.md](data/FINETUNING_DATA.md).

---

## Official evaluation (accuracy / BLEU / ROUGE)

Resmi metrikler için eval set üzerinde model çalıştırıp BLEU-4 ve ROUGE-L hesaplanır:

```bash
# Sadece metrik hesapla (eval dosyasında prediction varsa, model yok):
python -m structural_damage_model.run_eval --eval-file Test/test_images/eval_set_with_predictions.json --base-dir . --no-inference --output structural_damage_model/data/eval_results.json --update-metrics

# Model ile gerçek tahminler (GPU önerilir):
python -m structural_damage_model.run_eval --eval-file Test/test_images/test_results.json --base-dir . --model blip2 --output structural_damage_model/data/eval_results.json --update-metrics
```

`--no-inference`: Eval dosyasında `prediction` alanı varsa model çalıştırmadan sadece metrik hesaplar. Sonuçlar `data/eval_results.json` ve `data/metrics.json` (README tablosu için) içine yazılır.

---

## Inference

| Mode | Command |
|------|--------|
| **Mock** (no model) | `python -m structural_damage_model.inference --input <json> --output <out> --mock` |
| **Real VLM** | `python -m structural_damage_model.inference --input <json> --output <out>` (set `--model-name` if needed) |
| **Standalone images** | `python -m structural_damage_model.run_inference_on_images <path_or_dir> -o results.json --model blip2` |
| **Dry-run** | `python -m structural_damage_model.inference ... --dry-run` |

---

## Fine-tune

1. Prepare data: `training_captions.jsonl` + `images/` (see [One-click setup](#one-click-setup) and [data/FINETUNING_DATA.md](data/FINETUNING_DATA.md)).
2. Convert to LLaMA-Factory format: `convert_to_llamafactory.py` → `llamafactory_damage_train.json`.
3. Fine-tune with [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) (vision-language); dataset root = `structural_damage_model/data`.

Full plan: [../docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md](../docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md).

---

## API & servis

The same model is exposed via a **single API** for drone and Google Maps (and inspection) images:

```bash
STRUCTURE_API_MOCK=1 python run_api.py   # test without model
STRUCTURE_API_MODEL=blip2 python run_api.py
```

- **Endpoint:** `POST /v1/analyze` (file or base64 + `source_type`: `drone` \| `google_maps` \| `inspection`).
- **Docs:** [../docs/API.md](../docs/API.md).

---

## Data format

| Use | Format |
|-----|--------|
| **Training** | JSONL: `{"image_path": "...", "description": "..."}` (+ optional `image_id`, `page_number`). |
| **LLaMA-Factory** | `data/llamafactory_damage_train.json`: `{"image": "images/...", "conversations": [...]}`. |
| **Pipeline** | Each image in `out_merged.json` gets `damageDescription` (string). |

---

## Files

| File | Role |
|------|------|
| `build_training_data.py` | Pipeline JSON → training JSONL. |
| `export_images_from_pipeline.py` | Export base64 images to disk; rewrite paths in JSONL. |
| `convert_to_llamafactory.py` | JSONL → LLaMA-Factory conversation JSON. |
| `inference.py` | Run VLM on pipeline JSON; write `damageDescription`. |
| `run_inference_on_images.py` | Run on standalone image files (no pipeline JSON). |
| `data/` | `training_captions.jsonl`, `images/`, `llamafactory_damage_train.json`; see [data/FINETUNING_DATA.md](data/FINETUNING_DATA.md). |

---

## Announcements

Use this section for important notices (breaking changes, new benchmarks, release blockers).

| Date (UTC) | Level | Notice | Action |
|------------|--------|--------|--------|
| — | — | *No current announcements.* | — |

---

## Docs

- [STRUCTURAL_DAMAGE_MODEL_ROADMAP.md](../docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md) — Full plan, datasets, tech stack.
- [API.md](../docs/API.md) — Structure Analysis API (drone + Maps).
- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) — Train → serve → use in app.
