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

### Configuración
1. **Crear archivo `.env`** en la raíz del proyecto:
```bash
API_TOKEN=tu_token_seguro_aqui
ALLOWED_ORIGINS=*
```

2. **Generar token seguro** (opcional):
```bash
openssl rand -hex 32
```

### Ejecutar servidor

**Opción 1: Script automático (recomendado)**
```bash
./start_server.sh
```

**Opción 2: Comando manual**
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Parar servidor:**
```bash
# Ctrl+C en la terminal donde corre el servidor
# O desde otra terminal:
lsof -ti tcp:8000 | xargs kill -9
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

**1. Verificar features del modelo:**
```bash
curl http://127.0.0.1:8000/features
```

**2. Hacer predicción:**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_token_del_env" \
  -d '{
    "period_days": 12.34,
    "duration_hours": 5.6,
    "rp_rearth": 1.2,
    "rstar_rsun": 0.9,
    "mag": 10.5,
    "teff_k": 5778
  }'
```

**3. Documentación interactiva:**
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`



