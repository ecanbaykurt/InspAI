# Sample inspection reports

This folder is the **backbone** for SafeStructure: place **structural inspection** or **multi-family / HUD spec** PDFs here. The pipeline will parse them to JSON and extract images for analysis or model training.

## What to put here

- HUD multifamily assessment / foreclosure sale packages  
- Apartment or building inspection reports (e.g. JODAT-style)  
- Bid/RFP packages with exhibits and property photos  
- Any PDF that mixes **text (sections, property info, bid terms)** and **images (photos, exhibits, drawings)**

## Run the pipeline on a sample

From the repo root:

```bash
# Activate venv and install deps if needed
pip install -r requirements-agent.txt

# Example: JODAT-style report
python run_pipeline.py --pdfFilePath "Sample/JODAT-SAMPLE Apartment Building Inspection Report.pdf" \
  --projectId proj-sample --projectNumber SAMPLE-001 \
  --maxImagesToExtract 30 --storageDir Sample/extracted_images \
  --output Sample/out_merged.json
```

Output:

- `Sample/out_merged.json` — Full pipeline output (document structure, images, labels, summaries).
- `Sample/extracted_images/` — Extracted images (if `--storageDir` is set).

## Two-path strategy (PDF → JSON → analyze)

1. **Content path:** Use `docType`, `sectionIndex`, `propertyProfile`, `bidRequirements` from the JSON for scope and context.
2. **Image path:** Use `images[]` (with `imageId`, `pageNumber`, `labels`, `storagePath`) to train or run structural/crack/damage models.

See [../docs/DATASET_FORMAT.md](../docs/DATASET_FORMAT.md) for the full output schema.
