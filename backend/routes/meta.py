from fastapi import APIRouter
from ..model import model, get_expected_feature_names

router = APIRouter(prefix="", tags=["meta"])

@router.get("/features")
def features():
    names = get_expected_feature_names(model)
    accepted_inputs = [
        {"name": "period_days", "description": "Orbital period in days"},
        {"name": "duration_hours", "description": "Transit duration in hours"},
        {"name": "rp_rearth", "description": "Planetary Radius (Earth radii)"},
        {"name": "rstar_rsun", "description": "Stellar Radius (Solar radii)"},
        {"name": "mag", "description": "Stellar magnitude (brightness)"},
        {"name": "teff_k", "description": "Stellar effective temperature (K)"},
    ]
    return {"model_feature_count": len(names), "model_feature_names": names, "accepted_inputs": accepted_inputs}

