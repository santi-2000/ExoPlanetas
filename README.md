## Exoplanet API (FastAPI)

### Requisitos
- Python 3.12+
- macOS: `brew install libomp` (LightGBM runtime)

### Instalación
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Variables de entorno (opcional)
```bash
export API_TOKEN=change-me
export ALLOWED_ORIGINS=*
```

### Ejecutar servidor
```bash
uvicorn backend.main:app --reload
```
Abre: `http://127.0.0.1:8000` (docs en `http://127.0.0.1:8000/docs`).

### Endpoints
- GET `/features` → lista de features del modelo y los inputs aceptados por la API.
- POST `/predict` → predicción con 6 inputs; el resto se autocompleta internamente.

### Inputs aceptados (6)
- `period_days` (días)
- `duration_hours` (horas)
- `rp_rearth` (radio planetario en radios Tierra)
- `rstar_rsun` (radio estelar en radios Sol)
- `mag` (magnitud/brillo)
- `teff_k` (temperatura efectiva en Kelvin)

### Ejemplos de prueba
curl:
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me" \
  -d '{
    "period_days": 12,
    "duration_hours": 6,
    "rp_rearth": 1.3,
    "rstar_rsun": 1.1,
    "mag": 11.5,
    "teff_k": 5600
  }'
```



