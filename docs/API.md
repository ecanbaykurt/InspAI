# Structure Analysis API

Tek bir API ile **drone** ve **Google Maps** görüntüleri için yapı/hasar analizi (image detection / structure analysis). Modeli kendiniz eğitip servis edersiniz; uygulama yalnızca bu API’yi çağırır.

## Özet

- **Endpoint:** `POST /v1/analyze` (tek görsel: file veya base64) ve `POST /v1/analyze/batch` (çoklu dosya).
- **Kaynak türü:** `source_type`: `drone` | `google_maps` | `inspection` (aynı model, sadece bağlam için).
- **Yanıt:** Her görsel için `damage_description` (metin) ve isteğe bağlı `labels`.

## Servisi çalıştırma

```bash
# Bağımlılıklar (bir kez)
pip install -r requirements-api.txt

# Mock mod (model yok, test için)
STRUCTURE_API_MOCK=1 python run_api.py

# Gerçek model (BLIP2, CPU/Mac uyumlu)
STRUCTURE_API_MODEL=blip2 python run_api.py

# Gerçek model (LLaVA, GPU önerilir)
STRUCTURE_API_MODEL=llava python run_api.py
```

Varsayılan: `http://0.0.0.0:8000`. Health: `GET http://localhost:8000/health`.

## Endpoint’ler

### GET /health

Servis ve model durumu.

**Yanıt:** `{ "status": "ok", "model_backend": "blip2", "mock": false }`

### GET /v1/model

Kullanılan model bilgisi.

**Yanıt:** `{ "backend": "blip2", "model_id": "Salesforce/blip2-opt-2.7b", "mock": false }`

### POST /v1/analyze

Tek (veya iki) görsel analiz. Görseli **file** veya **image_base64** ile gönderin.

**Form / multipart:**

| Alan           | Tip   | Zorunlu | Açıklama                                      |
|----------------|--------|--------|-----------------------------------------------|
| file           | file   | Hayır*  | Görsel dosyası (PNG/JPEG)                     |
| image_base64   | string | Hayır*  | Base64 ile kodlanmış görsel                   |
| source_type    | string | Hayır  | `drone` \| `google_maps` \| `inspection` (varsayılan: inspection) |

\* `file` veya `image_base64`’ten en az biri gerekli.

**Yanıt:** `AnalyzeResponse`

```json
{
  "success": true,
  "results": [
    {
      "damage_description": "Cracks visible along the foundation; two windows boarded up.",
      "source_type": "drone",
      "labels": [],
      "model_id": "Salesforce/blip2-opt-2.7b"
    }
  ],
  "model_id": "Salesforce/blip2-opt-2.7b"
}
```

### POST /v1/analyze/batch

Çoklu görsel (örn. bir drone uçuşu veya birden fazla Maps tile).

**Form / multipart:**

| Alan   | Tip  | Açıklama                          |
|--------|------|------------------------------------|
| files  | files| Birden fazla görsel dosyası        |
| source_type | string | `drone` \| `google_maps` \| `inspection` |

**Yanıt:** Aynı `AnalyzeResponse`; `results` dizisinde her görsel için bir öğe.

## Uygulama tarafında kullanım

### cURL (tek dosya)

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -F "file=@path/to/drone_photo.jpg" \
  -F "source_type=drone"
```

### cURL (base64)

```bash
# Görseli base64 yap (örn. macOS)
BASE64=$(base64 -i path/to/image.png)
curl -X POST http://localhost:8000/v1/analyze \
  -F "image_base64=$BASE64" \
  -F "source_type=google_maps"
```

### JavaScript (fetch)

```javascript
const form = new FormData();
form.append("file", imageFile);  // File from <input type="file"> or drag-drop
form.append("source_type", "drone");

const res = await fetch("http://localhost:8000/v1/analyze", {
  method: "POST",
  body: form,
});
const data = await res.json();
console.log(data.results[0].damage_description);
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/v1/analyze"
with open("drone_photo.jpg", "rb") as f:
    r = requests.post(url, files={"file": f}, data={"source_type": "drone"})
r.raise_for_status()
print(r.json()["results"][0]["damage_description"])
```

### Python (batch, base64 – örn. Google Maps tile’ları)

```python
import base64
import requests

def analyze_image(image_bytes: bytes, source: str = "google_maps") -> str:
    r = requests.post(
        "http://localhost:8000/v1/analyze",
        data={
            "image_base64": base64.b64encode(image_bytes).decode(),
            "source_type": source,
        },
    )
    r.raise_for_status()
    return r.json()["results"][0]["damage_description"]

# Kullanım
with open("tile.png", "rb") as f:
    desc = analyze_image(f.read(), source="google_maps")
```

## Model eğitimi ve servis

1. **Veri:** Drone ve/veya Maps görselleri + etiketler (bkz. `structural_damage_model/data/`, `docs/STRUCTURAL_DAMAGE_MODEL_ROADMAP.md`).
2. **Eğitim:** LLaVA/BLIP2 benzeri VLM’i fine-tune edin (LLaMA-Factory vb.); çıktıyı tek bir checkpoint olarak kaydedin.
3. **Servis:** Eğitilmiş modeli yüklemek için `STRUCTURE_API_MODEL_NAME` ile kendi model yolunuzu verin; API aynı endpoint’leri kullanır.
4. **Deploy:** Sunucuda `run_api.py` veya `uvicorn api.app:app --host 0.0.0.0 --port 8000`; production’da reverse proxy (nginx) ve gerekirse Docker kullanın (bkz. `docs/DEPLOYMENT.md`).

## OpenAPI (Swagger)

Servis ayaktayken: **http://localhost:8000/docs**
