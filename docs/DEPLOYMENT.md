# Structure Analysis: Eğitim, Servis ve Uygulama Kullanımı

Hedef: Kendi **image detection / structure analysis** modelinizi (drone ve Google Maps görüntüleri için) **eğitip**, **tek bir API** üzerinden **servis edip**, uygulamada bu API’yi kullanmak.

## Genel akış

```
[Drone / Maps görselleri] → [Eğitim verisi] → [Model eğitimi] → [Checkpoint]
                                                                    ↓
[Uygulama] ← HTTP ← [Structure Analysis API] ← [Model yükleme]
```

1. **Veri toplama:** Drone ve/veya Google Maps’ten görseller; mümkünse hasar/yarı-yapı etiketleri.
2. **Eğitim:** Bu repo’daki `structural_damage_model` veri formatı + LLaMA-Factory (veya benzeri) ile VLM fine-tuning.
3. **Servis:** Eğitilmiş modeli `api/` ile aynı sunucuda çalıştırma; tek API (`/v1/analyze`) hem drone hem Maps için.
4. **Uygulama:** Frontend veya mobil uygulama sadece bu API’yi çağırır (file veya base64).

---

## 1. Veri hazırlama

- **Drone:** Uçuşlardan alınan fotoğraflar; isimlendirme veya coğrafi bilgi (opsiyonel) korunabilir.
- **Maps:** Static API / tile indirme ile alınan görüntüler; aynı `image_path` + `description` formatında tutulabilir.

Örnek (mevcut pipeline ile uyumlu):

```bash
# Pipeline JSON’dan eğitim JSONL
python -m structural_damage_model.build_training_data --input path/to/out_merged.json --output structural_damage_model/data/training_captions.jsonl --use-base64
python -m structural_damage_model.export_images_from_pipeline --input path/to/out_merged.json --out-dir structural_damage_model/data/images --jsonl structural_damage_model/data/training_captions.jsonl
```

`training_captions.jsonl` içindeki `description` alanlarını gerçek hasar açıklamalarıyla doldurun (elle veya LLM ile). Drone/Maps için ayrı bir `source` sütunu ekleyebilirsiniz; eğitimde aynı model kullanılır, API’de `source_type` sadece loglama/bağlam için kullanılır.

---

## 2. Model eğitimi

- Veri formatı: `structural_damage_model/data/llamafactory_damage_train.json` (LLaMA-Factory conversation formatı).
- Dönüşüm: `convert_to_llamafactory.py` ile JSONL → LLaMA-Factory JSON.
- Eğitim: LLaMA-Factory ile LLaVA (veya seçtiğiniz VLM) fine-tuning; LoRA önerilir.
- Çıktı: Tek bir checkpoint (ör. `output/checkpoint-final`).

Detay: `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`, `structural_damage_model/data/FINETUNING_DATA.md`.

---

## 3. API servisi

- **Kod:** `api/app.py`, `api/model_loader.py`, `api/schemas.py`.
- **Çalıştırma:**
  - Mock (model yok): `STRUCTURE_API_MOCK=1 python run_api.py`
  - BLIP2: `STRUCTURE_API_MODEL=blip2 python run_api.py`
  - LLaVA: `STRUCTURE_API_MODEL=llava python run_api.py`
  - Kendi checkpoint: `STRUCTURE_API_MODEL=llava STRUCTURE_API_MODEL_NAME=/path/to/checkpoint-final python run_api.py`  
    (model_loader’da LLaVA path’i desteklenmeli; gerekirse `model_name`’i HuggingFace formatında export edin.)

- **Port:** Varsayılan 8000. Değiştirmek için: `uvicorn api.app:app --host 0.0.0.0 --port 8080`.

---

## 4. Uygulamada API kullanımı

- **Endpoint:** `POST /v1/analyze` (tek görsel: `file` veya `image_base64` + `source_type`: `drone` | `google_maps` | `inspection`).
- **Batch:** `POST /v1/analyze/batch` (çoklu `files` + `source_type`).

Örnekler (curl, Python, JS): `docs/API.md`.

Uygulama tarafında:

1. Drone veya Maps’ten görsel al (dosya veya base64).
2. `source_type` ile kaynağı belirt.
3. Yanıttaki `results[].damage_description` (ve ileride `labels`) kullan.

---

## 5. Production notları

- **GPU:** LLaVA ve büyük modeller için CUDA’lı sunucu önerilir.
- **Ortam:** `requirements-api.txt` ile aynı Python ortamında çalıştırın.
- **Reverse proxy:** Nginx/Caddy ile TLS ve rate limit; API’yi `http://127.0.0.1:8000` üzerinden dinletin.
- **Docker (opsiyonel):** `Dockerfile` ile `run_api.py` ve model path’ini kapsayacak bir image tanımlanabilir; model ağır olduğu için volume ile mount edilebilir.

Bu sayfa, model eğitimi + tek API servisi + uygulama entegrasyonu akışını özetler; detaylar `API.md` ve `STRUCTURAL_DAMAGE_MODEL_ROADMAP.md` içindedir.
