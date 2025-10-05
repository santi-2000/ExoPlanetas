import os
from dotenv import load_dotenv

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure we load the .env from the project root (parent of backend/)
DOTENV_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv(dotenv_path=DOTENV_PATH)

API_TOKEN = os.getenv("API_TOKEN", "")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

MODEL_PATH = os.path.join(BASE_DIR, "exoplanet_model.pkl")

