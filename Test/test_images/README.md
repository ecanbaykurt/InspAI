# Test images for structural damage description model

This folder contains 3 sample images used to test the structural damage description model.

## Images

- **building_brick_facade.png** — Brick facade; cracks, foundation wear, boarded-up windows.
- **building_complex_street.png** — Building complex, pavement cracks, fire escapes, leaning utility pole.
- **paved_lot_buildings.png** — Cracked concrete ground, elevated building foundations, external staircase.

## Test results

Reference descriptions (derived from image content) are in `test_results.json`. Use them to compare with model output.

## Running inference on these images

**From the project root:**

```bash
# On image files (LLaVA or BLIP2; GPU recommended)
python3 -m structural_damage_model.run_inference_on_images Test/test_images/ -o Test/test_images/predictions.json --model blip2
```

PyTorch may hang on macOS; use Linux + CUDA for real model testing.
