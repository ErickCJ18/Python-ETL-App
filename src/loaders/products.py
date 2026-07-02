import csv

from src.db import exec_sp
from src.utils import nuevo_resultado, registrar

SP_INSERTAR_PRODUCTO = "SP_LOADPRODUCT"

def cargar_products(cursor, ruta_csv):
    resultado = nuevo_resultado()

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            try:
                _procesar_fila(cursor, fila, fila_num, resultado)

            except Exception as ex:
                registrar(
                    resultado,
                    "ERROR",
                    fila_num,
                    f"EXCEPCIÓN - {ex}"
                )

    return resultado


def _procesar_fila(cursor, fila, fila_num, resultado):
    try:
        id_producto = int(fila["IdProducto"]) if fila["IdProducto"] else None
    except ValueError:
        id_producto = None

    nombre = fila.get("Nombre")
    categoria = fila.get("Categoría")

    if id_producto is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdProducto vacío o con formato inválido"
        )
        return

    res = exec_sp(
        cursor,
        SP_INSERTAR_PRODUCTO,
        (
            id_producto,
            nombre,
            categoria,
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