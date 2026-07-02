import re
from datetime import datetime

def limpiar_texto(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    return texto or None


def extraer_id_numerico(valor):
    texto = limpiar_texto(valor)
    if texto is None:
        return None

    match = re.search(r"\d+", texto)
    return int(match.group()) if match else None


def a_entero(valor):
    texto = limpiar_texto(valor)
    if texto is None:
        return None

    try:
        return int(float(texto))
    except (ValueError, TypeError):
        return None


def parsear_fecha(valor):
    texto = limpiar_texto(valor)
    if texto is None:
        return None

    formatos = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
    )

    for formato in formatos:
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def nuevo_resultado():
    return {
        "procesados": 0,
        "insertados": 0,
        "duplicados": 0,
        "rechazados": 0,
        "errores": [],
    }


def registrar(resultado, estado, fila_num, detalle=None):
    resultado["procesados"] += 1

    estado = estado.upper()

    if estado == "INSERTADO":
        resultado["insertados"] += 1

    elif estado in ("DUPLICADO", "EXISTENTE"):
        resultado["duplicados"] += 1

    else:
        resultado["rechazados"] += 1
        resultado["errores"].append(
            f"Fila {fila_num}: {detalle or estado}"
        )