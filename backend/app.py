from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOWED_ORIGINS
from .routes.predict import router as predict_router
from .routes.meta import router as meta_router

app = FastAPI(title="Exoplanet AI API 🔭")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bienvenida a la API de Exoplanet AI"}

app.include_router(meta_router)
app.include_router(predict_router)

