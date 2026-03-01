# Terminology and labels

This document explains the **outputs** of the InspAI model and API (descriptions and labels), the **damage types** commonly referred to, and how to interpret and use them for transparency and consistency.

---

## API output: descriptions and labels

Every analysis result from `POST /v1/analyze` (and batch) includes at least:

| Field | Type | Description |
|-------|------|-------------|
| **damage_description** | string | Short natural-language description of structural damage or defects seen in the image (e.g. *“Cracks along the foundation; two windows boarded up.”*). Always present when the model runs. |
| **labels** | array (optional) | List of structured items, e.g. `{ "class": "<damage_type>", "confidence": <0–1> }`. Used for filtering, dashboards, and labeling critical buildings or elements. Currently optional; may be extended with location or severity. |
| **source_type** | string | As sent: `drone`, `google_maps`, or `inspection`. For context only. |
| **model_id** | string | Model/checkpoint used (e.g. `llava-hf/llava-1.5-7b-hf`). |

- **Today:** The model primarily fills **damage_description**. The **labels** array is in the response schema for future use (and for any downstream detector or post-processor you attach). You can derive your own tags or “critical” flags from the description (e.g. keyword rules) or from labels when present.
- **Interpretation:** Treat **damage_description** as a first-pass, machine-generated summary. It is not a substitute for a qualified human inspection or engineering assessment (see [LIMITATIONS_AND_TRANSPARENCY.md](LIMITATIONS_AND_TRANSPARENCY.md)).

---

## Damage types and terminology

The model is trained to describe **structural and building defects** in plain language. Commonly mentioned concepts include (non-exhaustive):

| Term | Brief definition (for consistency) |
|------|------------------------------------|
| **Crack** | Linear separation or fissure in material (concrete, masonry, etc.); may be hairline or wider. |
| **Spalling** | Flaking or breaking away of surface material (e.g. concrete, render). |
| **Corrosion** | Deterioration of metal (e.g. rebar, railings); rust, staining, or exposure. |
| **Efflorescence** | White salt deposits on surfaces; often indicates moisture. |
| **Boarded / sealed windows** | Windows covered with panels or sealant; can indicate vacancy, damage, or security. |
| **Foundation issues** | Visible problems at or near ground level: cracking, settlement, water damage, exposed footings. |
| **Pavement / surface damage** | Cracking, potholes, or unevenness in paved or ground surfaces. |
| **Fire escape / external stairs** | External egress elements; condition (rust, missing parts) may be noted. |

The **description** may combine several of these (e.g. *“Cracks and spalling on the facade; boarded windows; foundation visible with minor cracking.”*). You can map these terms to your own categories or severity levels when labeling **critical buildings** or assets.

---

## Labels: current and future shape

- **Current:** Each result can include **labels** as a list of objects. Example shape: `{ "class": "crack", "confidence": 0.85 }`. The exact keys and classes may depend on the model or post-processor you use; the API does not enforce a fixed taxonomy yet.
- **Planned / extension:** Labels may be extended with:
  - **Severity** (e.g. low / medium / high / critical),
  - **Location** (e.g. facade, roof, foundation),
  - **Standard taxonomies** (e.g. aligned with inspection codes or public datasets).

We will document any new label fields and recommended values in this file and in the API schema. If you implement your own label schema (e.g. for critical buildings), we encourage documenting it in your fork or in a discussion so others can reuse it.

---

## Using descriptions and labels to tag critical buildings

- **From damage_description:** In your application, parse the text for keywords or phrases (e.g. “foundation”, “crack”, “structural”) and apply your own rule to set a “critical” or “priority” flag for that building or image.
- **From labels:** When present, filter by `class` and `confidence` (e.g. any label with `class` in `["crack", "spalling"]` and `confidence > 0.8`) and mark the asset as critical or high-priority in your DB/UI.
- **Consistency:** Use the same terminology (e.g. the table above) in your UI and reports so civil engineers, architects, and inspectors see consistent terms.

For limitations and professional use, see [LIMITATIONS_AND_TRANSPARENCY.md](LIMITATIONS_AND_TRANSPARENCY.md).
