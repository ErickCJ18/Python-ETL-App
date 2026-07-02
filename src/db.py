"""
Capa de acceso a base de datos.
No contiene credenciales ni nombres de servidor: todo viene de config/settings.py
"""
import pyodbc

from config.settings import (
    DB_DRIVER, DB_SERVER, DB_DATABASE, DB_TRUSTED_CONNECTION,
    DB_USER, DB_PASSWORD, ALLOWED_SPS,
)
from src.logger import get_logger

logger = get_logger(__name__)


def _build_conn_str() -> str:
    parts = [f"DRIVER={DB_DRIVER}", f"SERVER={DB_SERVER}", f"DATABASE={DB_DATABASE}"]

    if DB_TRUSTED_CONNECTION.lower() == "yes":
        parts.append("Trusted_Connection=yes")
    else:
        if not DB_USER or not DB_PASSWORD:
            raise RuntimeError(
                "DB_TRUSTED_CONNECTION=no requiere DB_USER y DB_PASSWORD en el .env"
            )
        parts.append(f"UID={DB_USER}")
        parts.append(f"PWD={DB_PASSWORD}")

    return ";".join(parts) + ";"


def get_connection():
    """Abre una conexión nueva. Lanza una excepción clara si falla."""
    try:
        return pyodbc.connect(_build_conn_str())
    except pyodbc.Error as ex:
        logger.error(f"No se pudo conectar a la base de datos: {ex}")
        raise


def exec_sp(cursor, sp_name: str, params: tuple = ()) -> dict:
    """
    Ejecuta un stored procedure de forma segura.

    Seguridad:
    - sp_name se valida contra una whitelist (ALLOWED_SPS) antes de interpolarse
      en el SQL. Esto evita SQL injection por nombre de procedimiento, incluso
      si en el futuro sp_name llegara a depender de un input externo.
    - Los parámetros del SP siempre se pasan vía placeholders (?), nunca concatenados.
    """
    if sp_name not in ALLOWED_SPS:
        raise ValueError(
            f"Stored procedure '{sp_name}' no está en la whitelist ALLOWED_SPS. "
            f"Agrégalo en .env si es intencional."
        )

    placeholders = ", ".join(["?"] * len(params)) if params else ""
    sql = f"EXEC {sp_name} {placeholders}".strip()

    try:
        cursor.execute(sql, params)
    except pyodbc.Error as ex:
        logger.error(f"Error ejecutando {sp_name} con params={params}: {ex}")
        raise

    row = cursor.fetchone()
    if row is None:
        return {}

    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
