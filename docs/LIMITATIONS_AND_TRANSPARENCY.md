# Limitations and transparency

InspAI is developed in the open so that **civil engineers**, **architects**, **inspectors**, and **integrators** can use it with a clear understanding of what it does and does not do. This page states limitations and transparency commitments.

---

## What the model does

- **Input:** A single image (from a drone, camera, or inspection report).
- **Output:** A short **natural-language description** of structural damage or defects (and optionally **structured labels**). The same model and API are used for all image sources.
- **Purpose:** To support **screening**, **prioritization**, and **workflow integration**—not to replace human judgment or professional assessment.

---

## Limitations (transparency)

1. **Not a substitute for professional assessment**  
   The model’s output is a **first-pass, machine-generated description**. It is not a structural engineering report, a code compliance assessment, or a legally binding inspection. Decisions about safety, repair, or criticality should involve qualified professionals (e.g. licensed engineers, certified inspectors).

2. **Accuracy and coverage**  
   - Performance depends on data quality, lighting, resolution, and how representative your images are of the training/eval data.  
   - The model may miss damage, under- or over-state severity, or use terms that need interpretation.  
   - Metrics (e.g. BLEU, ROUGE) are reported in the [structural_damage_model README](../structural_damage_model/README.md); we encourage re-running evaluation on your own data.

3. **Bias and generalizability**  
   - Training data may reflect specific regions, building types, or damage types. Results may be less reliable on very different structures or imaging conditions.  
   - We do not claim absence of bias; we aim to document data sources and evaluation so users can assess fitness for their use case.

4. **Labels and criticality**  
   - **Structured labels** (e.g. class, confidence) are optional and may be extended over time.  
   - **“Critical” building** or severity tagging is something you implement in your application (e.g. from description keywords or label rules). The API provides descriptions (and labels when available), not a built-in legal or regulatory definition of “critical.”

5. **Data and privacy**  
   - If you send images to your own API instance, you control where data is stored and processed.  
   - If you use a third-party deployment, ensure you comply with your organization’s and jurisdiction’s data and privacy rules. We do not collect or store your images in this open-source project.

6. **Availability and changes**  
   - Model weights come from Hugging Face (or your own fine-tuned checkpoint). Availability and licensing follow those sources.  
   - We may extend the API (e.g. new label fields, new endpoints) with backward compatibility where possible; significant changes will be documented in the repo and release notes.

---

## Transparency commitments

- **Open development:** Code, training/eval pipeline, and documentation are public so users can see how the model is used and how to evaluate it.  
- **Documentation:** We document audience, use cases, terminology, labels, and limitations (this file and linked docs).  
- **Evaluation:** We provide an evaluation script and report metrics where applicable; we encourage independent evaluation on your own data.  
- **Contributions:** We welcome issues and pull requests; see [CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute.

If you are an engineer, architect, or inspector using InspAI in a regulatory or safety-related context, we recommend you document that the output is **assistive** and that final decisions are made by qualified personnel.
