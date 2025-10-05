import pandas as pd
import numpy as np
import argparse
from pathlib import Path

def clean_tabular(df: pd.DataFrame):
    rename_map = {
        "koi_period": "period_days",
        "koi_duration": "duration_hours",
        "koi_depth": "depth_ppm",
        "koi_prad": "rp_rearth",
        "koi_steff": "teff_k",
        "koi_slogg": "logg_cgs",
        "koi_srad": "rstar_rsun",
        "koi_kepmag": "mag",
        "koi_fpflag_nt": "flags_nt",
        "koi_fpflag_ss": "flags_ss",
        "koi_fpflag_co": "flags_co",
        "koi_fpflag_ec": "flags_ec",
        "koi_disposition": "label_raw",
        "koi_pdisposition": "label_prior",
        "koi_score": "score",
        "kepoi_name": "koi_name",
        "kepid": "kepler_id",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    for c in ["koi_period","koi_duration","koi_depth"]:
        if c in df.columns:
            df = df[df[c] > 0]

    # Imputar datos estelares
    for c in ["teff_k","logg_cgs","rstar_rsun","mag"]:
        if c in df.columns:
            med = df[c].median(skipna=True)
            df[c] = df[c].fillna(med)

    # Flags → enteros
    for c in ["flags_nt","flags_ss","flags_co","flags_ec"]:
        if c in df.columns:
            df[c] = df[c].fillna(0).astype(int)
        else:
            df[c] = 0

    # Derivados
    if "period_days" in df.columns:
        df["log_period"] = np.log10(df["period_days"])
    if "depth_ppm" in df.columns:
        df["log_depth"] = np.log10(df["depth_ppm"].clip(lower=1e-6))
        df["rp_rs_est"] = np.sqrt(df["depth_ppm"]/1e6)
    if "duration_hours" in df.columns and "period_days" in df.columns:
        df["dur_frac"] = df["duration_hours"]/(df["period_days"]*24)
    if "rp_rearth" in df.columns and "rstar_rsun" in df.columns:
        df["rp_rs_calc"] = df["rp_rearth"] / df["rstar_rsun"].replace(0, np.nan)
        df["rp_rs_error"] = (df["rp_rs_est"] - df["rp_rs_calc"]).abs()

    # Etiquetas unificadas
    if "label_raw" in df.columns:
        df["label_final"] = df["label_raw"].astype(str).str.upper().map({
            "CONFIRMED": "planet",
            "CANDIDATE": "candidate",
            "FALSE POSITIVE": "false_positive"
        })
    else:
        df["label_final"] = np.nan

    df["mission_Kepler"] = 1
    df["mission_TESS"] = 0
    df["mission_K2"] = 0

    return df

def clean_lightcurve(df: pd.DataFrame):
    if not {"time", "flux"}.issubset(df.columns):
        raise ValueError("Curva de luz debe tener columnas 'time' y 'flux'")
    df = df[["time","flux"]].dropna()
    df = df.sort_values("time").reset_index(drop=True)
    # Normalizar flux (divide entre la mediana)
    med = df["flux"].median()
    df["flux_norm"] = df["flux"] / med
    df["residual"] = df["flux_norm"] - 1.0
    return df

def main():
    parser = argparse.ArgumentParser(description="Limpieza de CSV para exoplanetas o curvas de luz")
    parser.add_argument("--input", required=True, help="Archivo CSV original")
    parser.add_argument("--output", required=True, help="Archivo CSV limpio de salida")
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep=None, engine="python", comment="#")

    # Detectar tipo de CSV
    if {"time","flux"}.issubset(df.columns):
        print("Detectado: Curva de luz 🌟")
        cleaned = clean_lightcurve(df)
    else:
        print("Detectado: Dataset tabular (KOI/TOI/K2) 📊")
        cleaned = clean_tabular(df)

    cleaned.to_csv(args.output, index=False)
    print(f"Archivo limpio guardado en: {args.output}")
    print(f"Filas finales: {len(cleaned)}")

if __name__ == "__main__":
    # Rutas fijas
    input_path = "data_kepler.csv"
    output_path = "Kleper_limpia.csv"

    print("Leyendo archivo:", input_path)
    df = pd.read_csv(input_path, sep=None, engine="python", comment="#")

    # Detectar tipo
    if {"time","flux"}.issubset(df.columns):
        print("Detectado: Curva de luz 🌟")
        cleaned = clean_lightcurve(df)
    else:
        print("Detectado: Dataset tabular (KOI/TOI/K2) 📊")
        cleaned = clean_tabular(df)

    cleaned.to_csv(output_path, index=False)
    print(f"\nArchivo limpio guardado en: {output_path}")
    print(f"Filas finales: {len(cleaned)}")