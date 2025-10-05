from pydantic import BaseModel

class SixInputs(BaseModel):
    period_days: float
    duration_hours: float
    rp_rearth: float
    rstar_rsun: float
    mag: float
    teff_k: float

