import csv

from src.db import exec_sp
from src.logger import get_logger

logger = get_logger(__name__)

SP_INSERTAR_CLIENTE = "SP_LOADCLIENT"

def cargar_clientes(cursor, ruta_csv: str) -> dict:
    resultado = {
        "procesados": 0,
        "insertados": 0,
        "duplicados": 0,
        "rechazados": 0,
        "errores": [],
    }

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            resultado["procesados"] += 1

            try:
                _procesar_fila(cursor, fila)
                resultado["insertados"] += 1

            except ValueError as ve:
                resultado["duplicados"] += 1
                resultado["errores"].append(
                    f"Fila {fila_num}: {ve}"
                )

            except Exception as ex:
                resultado["rechazados"] += 1
                resultado["errores"].append(
                    f"Fila {fila_num}: error inesperado: {ex}"
                )
                logger.warning(
                    f"Fila {fila_num} rechazada: {ex}"
                )

    return resultado


def _procesar_fila(cursor, fila: dict) -> None:
    try:
        id_cliente = (
            int(fila["IdCliente"])
            if fila["IdCliente"]
            else None
        )
    except ValueError:
        raise ValueError(
            "IdCliente vacío o con formato inválido."
        )

    if id_cliente is None:
        raise ValueError(
            "IdCliente vacío o con formato inválido."
        )

    nombre = fila.get("Nombre")
    email = fila.get("Email")

    exec_sp(
        cursor,
        SP_INSERTAR_CLIENTE,
        (
            id_cliente,
            nombre,
            email,
        ),
    )