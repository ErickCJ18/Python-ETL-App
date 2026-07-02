import csv

from src.db import exec_sp
from src.utils import (
    parsear_fecha,
    nuevo_resultado,
    registrar,
)
from src.resolvers.tipo_fuente_resolver import ResolverTipoFuente
from src.resolvers.resolvers_side import (ResolverClasificacion, ResolverFuenteDatosPorTipo)

SP_INSERTAR_SURVEY = "SP_LOADSURVEYS"

def cargar_surveys(cursor, ruta_csv):
    resultado = nuevo_resultado()

    resolver_tipo = ResolverTipoFuente(cursor)
    resolver_clasificacion = ResolverClasificacion(cursor)
    resolver_fuente = ResolverFuenteDatosPorTipo(cursor, resolver_tipo)

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            try:
                _procesar_fila(
                    cursor,
                    fila,
                    fila_num,
                    resultado,
                    resolver_clasificacion,
                    resolver_fuente,
                )

            except Exception as ex:
                registrar(
                    resultado,
                    "ERROR",
                    fila_num,
                    f"EXCEPCIÓN - {ex}",
                )

    return resultado


def _procesar_fila(
    cursor,
    fila,
    fila_num,
    resultado,
    resolver_clasificacion,
    resolver_fuente,
):

    try:
        id_opinion = int(fila["IdOpinion"]) if fila["IdOpinion"] else None
    except ValueError:
        id_opinion = None

    try:
        id_cliente = int(fila["IdCliente"]) if fila["IdCliente"] else None
    except ValueError:
        id_cliente = None

    try:
        id_producto = int(fila["IdProducto"]) if fila["IdProducto"] else None
    except ValueError:
        id_producto = None

    try:
        puntaje = (
            int(fila["PuntajeSatisfacción"])
            if fila["PuntajeSatisfacción"]
            else None
        )
    except ValueError:
        puntaje = None

    fecha = parsear_fecha(fila.get("Fecha"))
    comentario = fila.get("Comentario")
    clasificacion_texto = fila.get("Clasificación")
    fuente_texto = fila.get("Fuente")

    if id_opinion is None or id_producto is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdOpinion/IdProducto obligatorios",
        )
        return

    id_clasificacion = None
    if clasificacion_texto:
        id_clasificacion, estado_cl = resolver_clasificacion.resolver(
            clasificacion_texto
        )

        if id_clasificacion is None:
            registrar(
                resultado,
                "ERROR",
                fila_num,
                f"Clasificación no resuelta: {estado_cl}",
            )
            return

    id_fuente = None
    if fuente_texto:
        id_fuente, estado_f = resolver_fuente.resolver(fuente_texto)

        if id_fuente is None:
            registrar(
                resultado,
                "ERROR",
                fila_num,
                f"Fuente no resuelta: {estado_f}",
            )
            return

    res = exec_sp(
        cursor,
        SP_INSERTAR_SURVEY,
        (
            id_opinion,
            id_cliente,
            id_producto,
            fecha,
            comentario,
            id_clasificacion,
            puntaje,
            id_fuente,
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