# Open-Source Structural Damage Description Model (InspAI) — Roadmap

This doc outlines how to build an **open-source vision model** that takes structural inspection images and outputs **natural language descriptions** of damage (cracks, spallation, corrosion, etc.), pluggable into your existing PDF → JSON pipeline.

---

## 1. What You’re Building

- **Input:** Image from an inspection report (building, bridge, concrete, etc.).
- **Output:** Short, consistent text describing damage type, location, and severity (e.g. *“Hairline crack along joint; minor spallation lower left; no exposed rebar.”*).
- **Integration:** Run on each entry in `out_merged.json` → `images[]`, and add a field such as `damageDescription` (and optionally structured `labels`).

---

## 2. Two Main Approaches

### Option A — Fine-tune a Vision–Language Model (recommended for “describing” damage)

Use an open-source **VLM** (e.g. **LLaVA**, **Qwen2-VL**, **InternVL**) and fine-tune it on (image, damage description) pairs.

- **Pros:** Real sentences, adaptable to your terminology and report style; full control, no API keys.
- **Cons:** Need a few hundred to a few thousand labeled examples; training needs a GPU (LoRA/QLoRA reduces cost).

**Rough steps:**

1. **Collect / create training data**
   - Use images from your pipeline (`Sample/extracted_images`, or paths in `out_merged.json`).
   - Add one short description per image (from existing report text, or manual/GPT-assisted labeling).
   - Store as a simple format, e.g. JSONL: `{"image_path": "...", "description": "..."}`.

2. **Choose a base VLM**
   - **LLaVA-1.5/1.6** or **Qwen2-VL-2B/7B**: good balance of size and quality; lots of tutorials.
   - **InternVL2** or **CogVLM**: stronger but heavier.

3. **Fine-tune with LoRA/QLoRA**
   - Only train a small adapter (and optionally the projector); keep vision encoder and most of the LLM frozen.
   - Use frameworks like **LLaMA-Factory**, **Unsloth**, or the official LLaVA training code.
   - Prompt: e.g. *“Describe the structural damage visible in this inspection photo in one or two sentences.”*

4. **Inference**
   - Load the fine-tuned model; for each image in your JSON, run the model and write the output into `damageDescription`.

### Option B — Detection/Segmentation + template text

Use an existing **detection or segmentation** model (e.g. trained on **dacl10k**, **CODEBRIM**, or crack datasets), then turn bounding boxes/masks into text with templates.

- **Pros:** Less training data for “description” (you only need detection labels); can reuse dacl10k/CODEBRIM.
- **Cons:** Descriptions are more rigid (e.g. “Crack detected at region 1; Spallation at region 2”) unless you add a second step (e.g. LLM to rewrite).

**Rough steps:**

1. Use or train a model for damage classes (crack, spallation, corrosion, efflorescence, exposed rebar, etc.) on public datasets (dacl10k, CODEBRIM, or similar).
2. Run inference on your images → get boxes or masks per class.
3. Map class + location to a template or short phrase; optionally run a small LLM to turn that into a fluent sentence.

---

## 3. Recommended Path for “InspAI” (description-focused)

- **Phase 1 — Quick win:** Use a **pretrained VLM** (no fine-tuning) with a fixed prompt: *“Describe any structural damage or defects in this building inspection photo.”* Run it on your `images[]` and store the result in `damageDescription`. This gives you a baseline and helps you see what kind of descriptions you want.
- **Phase 2 — Data:** From your pipeline, build a dataset: for each image, either take existing text from the report (section captions, notes) or create 1–2 sentence descriptions (manually or with GPT/Claude, then reviewed). Save in a simple JSONL format.
- **Phase 3 — Fine-tune:** Fine-tune a small VLM (e.g. LLaVA-1.5-7B or Qwen2-VL-2B) with LoRA on your (image, description) pairs so the model speaks your language and damage taxonomy.
- **Phase 4 — Optional:** Add a **detection** head or a separate detector for “where” the damage is, and combine with the description model for location-aware text.

---

## 4. Public Datasets You Can Use

- **dacl10k** (WACV 2024): ~10k bridge images, 12 damage classes + 6 component classes; good for segmentation/detection and for bootstrapping descriptions (e.g. from class names + regions).
- **CODEBRIM:** concrete defect detection; useful for cracks, spalling, etc.
- **Your own data:** All images you extract via `run_pipeline.py`; labels/descriptions from report text or from Phase 2 above.

---

## 5. Tech Stack Suggestions

- **Python 3.10+**
- **PyTorch** + **transformers** (Hugging Face)
- **LLaVA** or **Qwen2-VL** for VLM; **LLaMA-Factory** or **Unsloth** for fine-tuning
- Optional: **OpenCV** / **PIL** for image loading; **sentence-transformers** if you want to compare/embed descriptions later

---

## 6. Integration With Your Pipeline

After the model runs on an image:

- Add to each image entry in your JSON, for example:
  - `damageDescription`: string (e.g. one or two sentences).
  - Optionally: `labels`: list of `{ "class": "crack", "confidence": 0.9 }` if you add a detector.

Your existing **Content path** (doc structure, sections) stays unchanged; the **Image path** gains a consistent, automatic damage description for every extracted image.

---

## Next Steps

1. Add a **dataset format** and a script to convert `out_merged.json` + optional captions into training JSONL.
2. Implement **inference** (pretrained VLM first, then swap to fine-tuned model).
3. Wire inference into the pipeline so that `run_pipeline.py` (or a follow-up script) fills `damageDescription` for each image.

See the `structural_damage_model/` package in this repo for a minimal implementation scaffold and data format.
