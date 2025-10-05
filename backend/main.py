import os, hmac, joblib, numpy as np
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

# --- Seguridad por API Key en header ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or not hmac.compare_digest(api_key, API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )
    return True

# --- App y CORS ---
app = FastAPI(title="Exoplanet AI API 🔭")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Carga del modelo .pkl (una sola vez al iniciar) ---
# Resolver ruta relativa al directorio de este archivo para evitar problemas de CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "exoplanet_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        "Modelo no encontrado. Coloca 'exoplanet_model.pkl' en el directorio 'backend/'."
    )

model = joblib.load(MODEL_PATH)

# --- Esquema de entrada ---
class SixInputs(BaseModel):
    period_days: float
    duration_hours: float
    rp_rearth: float  # Planetary Radius (R_earth)
    rstar_rsun: float  # Stellar Radius (R_sun)
    mag: float  # Stellar magnitude (Kep/TESS mag)
    teff_k: float  # Stellar effective temperature (K)

@app.get("/")
def read_root():
    return {"message": "Bienvenida a la API de Exoplanet AI"}

def _get_expected_feature_names() -> List[str]:
    for attr in ("feature_names_in_", "feature_name_", "feature_name"):
        names = getattr(model, attr, None)
        if names is not None:
            return list(names)
    n = getattr(model, "n_features_", None)
    if n is None:
        return []
    return [f"f{i}" for i in range(n)]


@app.get("/features")
def list_features() -> Dict[str, Any]:
    names = _get_expected_feature_names()
    accepted_inputs = [
        {"name": "period_days", "description": "Orbital period in days"},
        {"name": "duration_hours", "description": "Transit duration in hours"},
        {"name": "rp_rearth", "description": "Planetary Radius (Earth radii)"},
        {"name": "rstar_rsun", "description": "Stellar Radius (Solar radii)"},
        {"name": "mag", "description": "Stellar magnitude (brightness)"},
        {"name": "teff_k", "description": "Stellar effective temperature (K)"},
    ]
    return {
        "model_feature_count": len(names),
        "model_feature_names": names,
        "accepted_inputs": accepted_inputs,
    }


@app.post("/predict")
def predict(data: SixInputs, _: bool = Depends(verify_api_key)):
    names = _get_expected_feature_names()
    if not names:
        raise HTTPException(status_code=500, detail="Modelo sin metadatos de features")

    # Comenzar con los 6 inputs proporcionados
    row: Dict[str, float] = {
        "period_days": float(data.period_days),
        "duration_hours": float(data.duration_hours),
        "rp_rearth": float(data.rp_rearth),
        "rstar_rsun": float(data.rstar_rsun),
        "mag": float(data.mag),
        "teff_k": float(data.teff_k),
    }

    # Generar/estimar valores para el resto de features cuando falten
    rng = np.random.default_rng()

    # Superficies estelares típicas
    if "logg_cgs" in names and "logg_cgs" not in row:
        row["logg_cgs"] = float(rng.uniform(3.5, 4.7))

    if "depth_ppm" in names and "depth_ppm" not in row:
        # Profundidad de tránsito en ppm (rango razonable)
        row["depth_ppm"] = float(max(10.0, rng.normal(200.0, 100.0)))

    # Flags (0/1)
    for flag in ("flag_nt", "flag_ss", "flag_co", "flag_ec", "flags_nt", "flags_ss", "flags_co", "flags_ec"):
        if flag in names and flag not in row:
            row[flag] = int(rng.integers(0, 2))

    # Derivados
    if "period_days" in row and "log_period" in names:
        row["log_period"] = float(np.log10(max(row["period_days"], 1e-6)))

    if "depth_ppm" in row and "log_depth" in names:
        row["log_depth"] = float(np.log10(max(row["depth_ppm"], 1e-6)))

    if "depth_ppm" in row and "rp_rs_est" in names:
        row["rp_rs_est"] = float(np.sqrt(max(row["depth_ppm"], 0.0) / 1e6))

    if {"duration_hours", "period_days"}.issubset(row.keys()) and "dur_frac" in names:
        row["dur_frac"] = float(row["duration_hours"] / (row["period_days"] * 24.0))

    if {"rp_rearth", "rstar_rsun"}.issubset(row.keys()) and "rp_rs_calc" in names:
        # Aproximación: 1 R_sun ≈ 109 R_earth
        rstar_rearth = row["rstar_rsun"] * 109.0
        row["rp_rs_calc"] = float(row["rp_rearth"] / max(rstar_rearth, 1e-9))

    if {"rp_rs_est", "rp_rs_calc"}.issubset(row.keys()) and "rp_rs_error" in names:
        row["rp_rs_error"] = float(abs(row["rp_rs_est"] - row["rp_rs_calc"]))

    # Completar cualquier feature faltante con 0 para cumplir el orden del modelo
    for n in names:
        if n not in row:
            row[n] = 0.0

    # Construir DataFrame con columnas en el orden esperado
    x_df = pd.DataFrame([row], columns=names)

    pred = model.predict(x_df)

    # Si tu modelo tiene predict_proba:
    prob = None
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(x_df).tolist()[0]

    # Normalizar salida: si es array/serie con string u objeto, devolver como string
    value = pred[0] if isinstance(pred, (list, np.ndarray)) else pred
    try:
        # Convertir a float solo si aplica
        value = float(value)
    except (TypeError, ValueError):
        # Mantener etiqueta como string
        value = str(value)
    return {"prediction": value, "proba": prob}
