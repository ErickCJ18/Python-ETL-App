import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from config.settings import DATA_DIR
from src.db import get_connection
from src.logger import get_logger
from src.loaders.clientes import cargar_clientes
from src.loaders.products import cargar_products
from src.loaders.fuente_datos import cargar_fuente_datos
from src.loaders.surveys import cargar_surveys
from src.loaders.social_comments import cargar_social_comments
from src.loaders.web_reviews import cargar_web_reviews

logger = get_logger("etl.main")

# Rutas absolutas: el script funciona sin importar desde dónde se ejecute
PROCESOS = [
    ("Clientes", cargar_clientes, DATA_DIR / "clients.csv"),
    ("Productos", cargar_products, DATA_DIR / "products.csv"),
    ("Fuente de Datos", cargar_fuente_datos, DATA_DIR / "fuente_datos.csv"),
    ("Encuestas (Surveys)", cargar_surveys, DATA_DIR / "surveys_part1.csv"),
    ("Comentarios Sociales", cargar_social_comments, DATA_DIR / "social_comments.csv"),
    ("Reseñas Web", cargar_web_reviews, DATA_DIR / "web_reviews.csv"),
]

MAX_ERRORES_MOSTRADOS = 10


def ejecutar_proceso(nombre, funcion, ruta, cursor, conn):
    logger.info(f"=== Iniciando: {nombre} ===")

    if not ruta.exists():
        logger.error(f"[{nombre}] Archivo no encontrado: {ruta}")
        return None

    try:
        resultado = funcion(cursor, str(ruta))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        logger.exception(f"[{nombre}] ERROR CRÍTICO, se hizo rollback: {ex}")
        return None

    logger.info(
        f"[{nombre}] procesados={resultado['procesados']} "
        f"insertados={resultado['insertados']} "
        f"duplicados={resultado['duplicados']} "
        f"rechazados={resultado['rechazados']}"
    )

    for err in resultado["errores"][:MAX_ERRORES_MOSTRADOS]:
        logger.warning(f"[{nombre}] {err}")
    restantes = len(resultado["errores"]) - MAX_ERRORES_MOSTRADOS
    if restantes > 0:
        logger.warning(f"[{nombre}] ... y {restantes} error(es) más")

    return resultado


def imprimir_resumen(resumen_total):
    logger.info("=" * 80)
    logger.info("RESUMEN FINAL DEL PROCESO ETL")
    logger.info("=" * 80)

    totales = {"procesados": 0, "insertados": 0, "duplicados": 0, "rechazados": 0}
    for nombre, r in resumen_total:
        logger.info(
            f"{nombre:25s} | procesados={r['procesados']:6d} | "
            f"insertados={r['insertados']:6d} | "
            f"duplicados={r['duplicados']:6d} | "
            f"rechazados={r['rechazados']:6d}"
        )
        for k in totales:
            totales[k] += r[k]

    logger.info("-" * 80)
    logger.info(
        f"{'TOTAL':25s} | procesados={totales['procesados']:6d} | "
        f"insertados={totales['insertados']:6d} | "
        f"duplicados={totales['duplicados']:6d} | "
        f"rechazados={totales['rechazados']:6d}"
    )


def main():
    try:
        conn = get_connection()
    except Exception:
        logger.critical("No se pudo establecer conexión a la base de datos. Abortando ETL.")
        sys.exit(1)

    resumen_total = []

    try:
        with conn:
            cursor = conn.cursor()
            for nombre, funcion, ruta in PROCESOS:
                resultado = ejecutar_proceso(nombre, funcion, ruta, cursor, conn)
                if resultado is not None:
                    resumen_total.append((nombre, resultado))
            cursor.close()
    finally:
        conn.close()

    imprimir_resumen(resumen_total)


if __name__ == "__main__":
    main()
