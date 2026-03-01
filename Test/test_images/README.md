# Test images for structural damage description model

Bu klasör, yapı hasarı tanımlama modelini test etmek için kullanılan 3 örnek görseli içerir.

## Görseller

- **building_brick_facade.png** — Tuğla cephe; çatlaklar, temel aşınması, tahta kapalı pencereler.
- **building_complex_street.png** — Bina kompleksi, asfalt çatlakları, yangın merdivenleri, eğik direk.
- **paved_lot_buildings.png** — Kırık beton zemin, yükseltilmiş bina temelleri, dış merdiven.

## Test sonuçları

Referans açıklamalar (görsel içeriklerinden türetilmiş) `test_results.json` içinde. Model çıktısıyla karşılaştırmak için kullanabilirsiniz.

## Bu görsellerle inference çalıştırma

**Proje kökünden:**

```bash
# Görsel dosyaları üzerinde (LLaVA veya BLIP2 ile; GPU önerilir)
python3 -m structural_damage_model.run_inference_on_images Test/test_images/ -o Test/test_images/predictions.json --model blip2
```

Mac’te PyTorch bazen kilitlenebilir; gerçek model testi için Linux + CUDA kullanın.
