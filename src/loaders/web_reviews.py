import csv

from src.db import exec_sp
from src.utils import (
    extraer_id_numerico,
    parsear_fecha,
    nuevo_resultado,
    registrar,
)

SP_INSERTAR_REVIEW = "SP_LOADREVIEWS"

def cargar_web_reviews(cursor, ruta_csv):
    resultado = nuevo_resultado()

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            try:
                _procesar_fila(
                    cursor,
                    fila,
                    fila_num,
                    resultado,
                )

            except Exception as ex:
                registrar(
                    resultado,
                    "ERROR",
                    fila_num,
                    f"EXCEPCIÓN - {ex}",
                )

    return resultado


def _procesar_fila(cursor, fila, fila_num, resultado):
    id_review = extraer_id_numerico(fila.get("IdReview"))
    id_cliente = extraer_id_numerico(fila.get("IdCliente"))  # Puede ser None
    id_producto = extraer_id_numerico(fila.get("IdProducto"))
    fecha = parsear_fecha(fila.get("Fecha"))
    comentario = fila.get("Comentario")

    try:
        rating = int(fila["Rating"]) if fila["Rating"] else None
    except ValueError:
        rating = None

    if id_review is None or id_producto is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdReview/IdProducto obligatorios o con formato inválido",
        )
        return

    res = exec_sp(
        cursor,
        SP_INSERTAR_REVIEW,
        (
            id_review,
            id_cliente,
            id_producto,
            fecha,
            comentario,
            rating,
        ),
    )

    estado = res.get("Resultado", "ERROR: sin respuesta del SP")
    estado_base = "ERROR" if estado.startswith("ERROR") else estado

    registrar(
        resultado,
        estado_base,
        fila_num,
        estado,
    )