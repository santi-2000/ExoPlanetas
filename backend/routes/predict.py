from fastapi import APIRouter, Depends, HTTPException
from ..security import verify_api_key
from ..schemas import SixInputs
from ..model import model, get_expected_feature_names
import numpy as np
import pandas as pd
from typing import Dict

router = APIRouter(prefix="", tags=["predict"])

@router.post("/predict")
def predict(data: SixInputs, _: bool = Depends(verify_api_key)):
    names = get_expected_feature_names(model)
    if not names:
        raise HTTPException(status_code=500, detail="Modelo sin metadatos de features")

    row: Dict[str, float] = {
        "period_days": float(data.period_days),
        "duration_hours": float(data.duration_hours),
        "rp_rearth": float(data.rp_rearth),
        "rstar_rsun": float(data.rstar_rsun),
        "mag": float(data.mag),
        "teff_k": float(data.teff_k),
    }

    rng = np.random.default_rng()

    if "logg_cgs" in names and "logg_cgs" not in row:
        row["logg_cgs"] = float(rng.uniform(3.5, 4.7))

    if "depth_ppm" in names and "depth_ppm" not in row:
        row["depth_ppm"] = float(max(10.0, rng.normal(200.0, 100.0)))

    for flag in ("flag_nt", "flag_ss", "flag_co", "flag_ec", "flags_nt", "flags_ss", "flags_co", "flags_ec"):
        if flag in names and flag not in row:
            row[flag] = int(rng.integers(0, 2))

    if "period_days" in row and "log_period" in names:
        row["log_period"] = float(np.log10(max(row["period_days"], 1e-6)))
    if "depth_ppm" in row and "log_depth" in names:
        row["log_depth"] = float(np.log10(max(row["depth_ppm"], 1e-6)))
    if "depth_ppm" in row and "rp_rs_est" in names:
        row["rp_rs_est"] = float(np.sqrt(max(row["depth_ppm"], 0.0) / 1e6))
    if {"duration_hours", "period_days"}.issubset(row.keys()) and "dur_frac" in names:
        row["dur_frac"] = float(row["duration_hours"] / (row["period_days"] * 24.0))
    if {"rp_rearth", "rstar_rsun"}.issubset(row.keys()) and "rp_rs_calc" in names:
        rstar_rearth = row["rstar_rsun"] * 109.0
        row["rp_rs_calc"] = float(row["rp_rearth"] / max(rstar_rearth, 1e-9))
    if {"rp_rs_est", "rp_rs_calc"}.issubset(row.keys()) and "rp_rs_error" in names:
        row["rp_rs_error"] = float(abs(row["rp_rs_est"] - row["rp_rs_calc"]))

    for n in names:
        if n not in row:
            row[n] = 0.0

    x_df = pd.DataFrame([row], columns=names)
    pred = model.predict(x_df)
    prob = None
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(x_df).tolist()[0]

    value = pred[0] if isinstance(pred, (list, np.ndarray)) else pred
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = str(value)
    return {"prediction": value, "proba": prob}

