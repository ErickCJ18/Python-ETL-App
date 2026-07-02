import csv

from src.db import exec_sp
from src.utils import (
    extraer_id_numerico,
    parsear_fecha,
    nuevo_resultado,
    registrar,
)
from src.resolvers.resolvers_side import ResolverRedSocial

SP_INSERTAR_COMMENT = "SP_LOADCOMMENTS"

def cargar_social_comments(cursor, ruta_csv):
    resultado = nuevo_resultado()
    resolver_red = ResolverRedSocial(cursor)

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            try:
                _procesar_fila(
                    cursor,
                    fila,
                    fila_num,
                    resultado,
                    resolver_red,
                )

            except Exception as ex:
                registrar(
                    resultado,
                    "ERROR",
                    fila_num,
                    f"EXCEPCIÓN - {ex}",
                )

    return resultado


def _procesar_fila(cursor, fila, fila_num, resultado, resolver_red):
    id_comment = extraer_id_numerico(fila.get("IdComment"))
    id_cliente = extraer_id_numerico(fila.get("IdCliente"))  # Puede ser None
    id_producto = extraer_id_numerico(fila.get("IdProducto"))
    red_texto = fila.get("Fuente")
    fecha = parsear_fecha(fila.get("Fecha"))
    comentario = fila.get("Comentario")

    if id_comment is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdComment vacío o con formato inválido",
        )
        return

    if id_producto is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdProducto vacío o con formato inválido",
        )
        return

    if not red_texto:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "Fuente (red social) obligatoria",
        )
        return

    id_red, estado_red = resolver_red.resolver(red_texto)

    if id_red is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            f"Red social no resuelta: {estado_red}",
        )
        return

    res = exec_sp(
        cursor,
        SP_INSERTAR_COMMENT,
        (
            id_comment,
            id_cliente,
            id_producto,
            id_red,
            fecha,
            comentario,
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