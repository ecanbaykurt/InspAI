# InspAI / Structure Analysis — GitHub sharing

When announcing or sharing the repo on GitHub, you can use the text below (shorten as needed).

---

## Short announcement (README / Social)

**InspAI** — Open-source structural damage description model for drone and Google Maps imagery. One VLM (LLaVA/BLIP2), one API, fine-tunable on your labels.

- **Metrics (official eval):** BLEU-4 **0.11**, ROUGE-L **0.59** (eval set: 3 samples; re-run with your model for full benchmark).
- **Use cases:** Inspection reports, drone surveys, Maps-based assessment; single `POST /v1/analyze` API.
- **Repo:** [your-repo-url]

---

## Release notes template (GitHub Release)

**Title:** InspAI v0.1 — Structural damage description model + API

**Description:**

- **Model:** Vision-language (LLaVA/BLIP2) for describing structural damage (cracks, spalling, corrosion, etc.) in one or two sentences.
- **API:** Single endpoint `POST /v1/analyze` for drone, Google Maps, and inspection images; same response format.
- **Evaluation:** Official BLEU-4 and ROUGE-L on eval set; see `structural_damage_model/run_eval.py` and `data/eval_results.json`.
- **Quick start:** `bash structural_damage_model/quick_setup.sh` for data prep; `STRUCTURE_API_MOCK=1 python run_api.py` for API test.

**Assets:** Source only (no pre-trained weights; use HuggingFace LLaVA/BLIP2 or your fine-tuned checkpoint).

---

## Pre-share checklist

- [ ] README repo URL and (if any) live demo link are up to date
- [ ] Metrics and "Official evaluation" section in `structural_damage_model/README.md` are up to date
- [ ] Links in `docs/API.md` and `docs/DEPLOYMENT.md` work
- [ ] If needed, large model files / `data/images` are excluded via `.gitignore`
- [ ] License file (e.g. MIT) is present
- [ ] Short description and topics added in the GitHub repo "About" section

You can delete this file after the first release or move it under `docs/`.
