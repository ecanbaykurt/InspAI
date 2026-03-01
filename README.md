# Structure Analyse

Yapı hasarı / yapı analizi için **görsel tespit modeli** (drone ve Google Maps görüntüleri), **tek bir API** ile servis edilir; uygulama bu API’yi kullanır.

## Bileşenler

| Bileşen | Açıklama |
|--------|----------|
| **Pipeline** | PDF raporları → JSON + görsel çıkarma (örn. `run_pipeline.py`, `Sample/`) |
| **Model** | Yapı hasarı tanımlama (VLM: LLaVA/BLIP2, fine-tune: `structural_damage_model/`) |
| **API** | Tek endpoint: `POST /v1/analyze` — drone / Maps / inspection görselleri → hasar açıklaması |
| **Uygulama** | API’yi çağırır (dosya veya base64); `docs/API.md` ve `examples/call_structure_api.py` |

## Hızlı başlangıç

### 1. API’yi çalıştır (mock – model yok)

```bash
pip install -r requirements-api.txt
STRUCTURE_API_MOCK=1 python run_api.py
# veya: STRUCTURE_API_MOCK=1 uvicorn api.app:app --host 0.0.0.0 --port 8000
```

- Health: http://localhost:8000/health  
- Swagger: http://localhost:8000/docs  
- Analiz: `curl -X POST http://localhost:8000/v1/analyze -F "file=@resim.jpg" -F "source_type=drone"`

### 2. Gerçek model ile (BLIP2 veya LLaVA)

```bash
STRUCTURE_API_MOCK=0 STRUCTURE_API_MODEL=blip2 python run_api.py
# GPU için: STRUCTURE_API_MODEL=llava
```

### 3. Uygulama tarafında kullanım

- **Dokümantasyon:** `docs/API.md`  
- **Örnek çağrı:** `examples/call_structure_api.py`  
- **Eğitim + deploy:** `docs/DEPLOYMENT.md`

## Hedef akış

1. **Eğitim:** Drone/Maps verisi → `structural_damage_model` veri formatı → LLaMA-Factory ile fine-tune → checkpoint.  
2. **Servis:** Checkpoint’i bu API ile yükle; aynı API drone ve Maps için kullanılır.  
3. **Uygulama:** Görseli (dosya veya base64) + `source_type` (`drone` | `google_maps` | `inspection`) ile `POST /v1/analyze`; yanıttaki `damage_description` kullanılır.

Detaylar: `docs/API.md`, `docs/DEPLOYMENT.md`, `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`.
