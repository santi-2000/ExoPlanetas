import os
import joblib
from typing import List
from .config import MODEL_PATH

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Modelo no encontrado. Coloca 'exoplanet_model.pkl' en 'backend/'.")

model = joblib.load(MODEL_PATH)

def get_expected_feature_names(m) -> List[str]:
    for attr in ("feature_names_in_", "feature_name_", "feature_name"):
        names = getattr(m, attr, None)
        if names is not None:
            return list(names)
    n = getattr(m, "n_features_", None)
    if n is None:
        return []
    return [f"f{i}" for i in range(n)]

