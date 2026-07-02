import csv

from src.db import exec_sp
from src.utils import (
    extraer_id_numerico,
    parsear_fecha,
    nuevo_resultado,
    registrar,
)
from src.resolvers.tipo_fuente_resolver import ResolverTipoFuente

SP_INSERTAR_FUENTE = "SP_LOADFUENTE"

def cargar_fuente_datos(cursor, ruta_csv):
    resultado = nuevo_resultado()
    resolver_tipo = ResolverTipoFuente(cursor)

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for fila_num, fila in enumerate(reader, start=2):
            try:
                _procesar_fila(
                    cursor,
                    fila,
                    fila_num,
                    resultado,
                    resolver_tipo,
                )

            except Exception as ex:
                registrar(
                    resultado,
                    "ERROR",
                    fila_num,
                    f"EXCEPCIÓN - {ex}",
                )

    return resultado


def _procesar_fila(cursor, fila, fila_num, resultado, resolver_tipo):
    """
    Procesa una fila del CSV y ejecuta el stored procedure correspondiente.
    """

    id_fuente = extraer_id_numerico(fila.get("IdFuente"))
    tipo_texto = fila.get("TipoFuente")
    fecha_carga = parsear_fecha(fila.get("FechaCarga"))

    if id_fuente is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "IdFuente vacío o con formato inválido",
        )
        return

    if fecha_carga is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            "FechaCarga inválida",
        )
        return

    id_tipo_fuente, estado_tipo = resolver_tipo.resolver(tipo_texto)

    if id_tipo_fuente is None:
        registrar(
            resultado,
            "ERROR",
            fila_num,
            f"No se pudo resolver TipoFuente: {estado_tipo}",
        )
        return

    res = exec_sp(
        cursor,
        SP_INSERTAR_FUENTE,
        (
            id_fuente,
            id_tipo_fuente,
            fecha_carga,
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