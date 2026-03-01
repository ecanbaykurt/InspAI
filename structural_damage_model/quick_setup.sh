#!/usr/bin/env bash
# One-click setup: build training data + export images + convert to LLaMA-Factory.
# Run from repo root: bash structural_damage_model/quick_setup.sh [path/to/out_merged.json]

set -e
INPUT_JSON="${1:-Test/out_merged.json}"
DATA_DIR="structural_damage_model/data"

if [ ! -f "$INPUT_JSON" ]; then
  echo "Usage: bash structural_damage_model/quick_setup.sh [path/to/out_merged.json]"
  echo "File not found: $INPUT_JSON"
  exit 1
fi

echo "Input: $INPUT_JSON"
echo "Step 1/3: build_training_data..."
python3 -m structural_damage_model.build_training_data \
  --input "$INPUT_JSON" \
  --output "$DATA_DIR/training_captions.jsonl" \
  --use-base64

echo "Step 2/3: export_images_from_pipeline..."
python3 -m structural_damage_model.export_images_from_pipeline \
  --input "$INPUT_JSON" \
  --out-dir "$DATA_DIR/images" \
  --jsonl "$DATA_DIR/training_captions.jsonl"

echo "Step 3/3: convert_to_llamafactory..."
python3 -m structural_damage_model.convert_to_llamafactory \
  --input "$DATA_DIR/training_captions.jsonl" \
  --output "$DATA_DIR/llamafactory_damage_train.json" \
  --image-root structural_damage_model/data

echo "Done. Next: edit $DATA_DIR/training_captions.jsonl (add real descriptions), then re-run step 3."
