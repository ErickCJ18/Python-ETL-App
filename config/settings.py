"""
Configuración centralizada del proyecto.
Todo valor sensible o dependiente del entorno vive aquí, nunca en el código de negocio.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Raíz del proyecto (independiente de desde dónde se ejecute el script)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga el .env ubicado en la raíz del proyecto
load_dotenv(BASE_DIR / ".env")


def _required(var_name: str) -> str:
    """Obliga a que ciertas variables existan; falla rápido y con mensaje claro."""
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria '{var_name}'. "
            f"Revisa tu archivo .env (usa .env.example como referencia)."
        )
    return value


# --- Base de datos ---
DB_DRIVER = _required("DB_DRIVER")
DB_SERVER = _required("DB_SERVER")
DB_DATABASE = _required("DB_DATABASE")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Rutas ---
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Seguridad: whitelist de stored procedures ---
# Cualquier SP que no esté en esta lista será rechazado por db.py antes de ejecutarse.
ALLOWED_SPS = set(
    sp.strip() for sp in os.getenv("ALLOWED_SPS", "").split(",") if sp.strip()
)
