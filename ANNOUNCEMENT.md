# InspAI / Structure Analysis — GitHub paylaşımı

Repo’yu GitHub’da duyurup paylaşırken aşağıdaki metni (İngilizce veya Türkçe) kısaltıp kullanabilirsiniz.

---

## Kısa duyuru (README / Social)

**InspAI** — Open-source structural damage description model for drone and Google Maps imagery. One VLM (LLaVA/BLIP2), one API, fine-tunable on your labels.

- **Metrics (official eval):** BLEU-4 **0.11**, ROUGE-L **0.59** (eval set: 3 samples; re-run with your model for full benchmark).
- **Use cases:** Inspection reports, drone surveys, Maps-based assessment; single `POST /v1/analyze` API.
- **Repo:** [your-repo-url]

---

## Release notes taslağı (GitHub Release)

**Title:** InspAI v0.1 — Structural damage description model + API

**Description:**

- **Model:** Vision-language (LLaVA/BLIP2) for describing structural damage (cracks, spalling, corrosion, etc.) in one or two sentences.
- **API:** Single endpoint `POST /v1/analyze` for drone, Google Maps, and inspection images; same response format.
- **Evaluation:** Official BLEU-4 and ROUGE-L on eval set; see `structural_damage_model/run_eval.py` and `data/eval_results.json`.
- **Quick start:** `bash structural_damage_model/quick_setup.sh` for data prep; `STRUCTURE_API_MOCK=1 python run_api.py` for API test.

**Assets:** Source only (no pre-trained weights; use HuggingFace LLaVA/BLIP2 or your fine-tuned checkpoint).

---

## Paylaşım öncesi kontrol listesi

- [ ] README’de repo URL’i ve (varsa) canlı demo linki güncel
- [ ] `structural_damage_model/README.md` içindeki metrikler ve “Official evaluation” bölümü güncel
- [ ] `docs/API.md` ve `docs/DEPLOYMENT.md` linkleri çalışıyor
- [ ] Gerekirse `.gitignore` ile büyük model dosyaları / `data/images` hariç tutuldu
- [ ] Lisans dosyası (e.g. MIT) eklendi
- [ ] GitHub repo’da “About” kısmına kısa açıklama ve konular (topics) eklendi

Bu dosyayı ilk release sonrası silebilir veya `docs/` altına taşıyabilirsiniz.
