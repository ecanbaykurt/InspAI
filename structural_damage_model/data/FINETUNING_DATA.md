# Fine-tuning data (structural damage description)

## What’s here

- **`training_captions.jsonl`** — One line per image: `image_path`, `description`, `image_id`, etc.  
  Edit `description` for each line (or generate with an LLM), then use for training.

- **`images/`** — Images exported from your pipeline JSON (so paths in the JSONL point to real files).

- **`llamafactory_damage_train.json`** — Conversation format for [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory): each item has `"image"` (path relative to this `data/` dir) and `"conversations"` (human instruction + gpt response).  
  Use with LLaMA-Factory’s vision-language fine-tuning; set dataset path to this JSON and image root to this `data/` directory (so `images/xxx.png` resolves to `data/images/xxx.png`).

## Workflow

1. **Build/refresh training JSONL from pipeline:**
   ```bash
   python -m structural_damage_model.build_training_data --input Test/out_merged.json --output structural_damage_model/data/training_captions.jsonl --use-base64
   ```

2. **Export images and fix paths in JSONL:**
   ```bash
   python -m structural_damage_model.export_images_from_pipeline --input Test/out_merged.json --out-dir structural_damage_model/data/images --jsonl structural_damage_model/data/training_captions.jsonl
   ```

3. **Add or edit descriptions** in `training_captions.jsonl` (manually or with an LLM). Replace `"No description yet."` with real damage descriptions.

4. **Convert to LLaMA-Factory format:**
   ```bash
   python -m structural_damage_model.convert_to_llamafactory --input structural_damage_model/data/training_captions.jsonl --output structural_damage_model/data/llamafactory_damage_train.json --image-root structural_damage_model/data
   ```

5. Point LLaMA-Factory at `llamafactory_damage_train.json` and use this folder as the image root for fine-tuning LLaVA (or another VLM).
