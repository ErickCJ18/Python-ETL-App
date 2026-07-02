import datetime
from src.db import exec_sp

class ResolverClasificacion:
    """Resuelve o crea una fila en Clasificaciones a partir de su texto."""

    def __init__(self, cursor):
        self.cursor = cursor
        self._cache = {}
        self._siguiente_id = self._obtener_siguiente_id()

    def _obtener_siguiente_id(self):
        self.cursor.execute(
            "SELECT ISNULL(MAX(IdClasificacion), 0) + 1 FROM Clasificaciones"
        )
        return self.cursor.fetchone()[0]

    def resolver(self, texto):
        """Devuelve (IdClasificacion, estado)."""
        if not texto:
            return None, "ERROR: texto de Clasificacion vacío"

        if texto in self._cache:
            return self._cache[texto], "CACHE"

        # ¿Ya existe en la BD? (por si otro proceso previo ya la cargó)
        self.cursor.execute(
            "SELECT IdClasificacion FROM Clasificaciones WHERE Clasificacion = ?",
            (texto,),
        )
        row = self.cursor.fetchone()
        if row:
            self._cache[texto] = row[0]
            return row[0], "EXISTENTE"

        # No existe -> crearla con el siguiente Id disponible
        nuevo_id = self._siguiente_id
        res = exec_sp(self.cursor, "SP_LOADCLASIFICACION", (nuevo_id, texto))
        estado = res.get("Resultado", "ERROR: sin respuesta del SP")

        if estado != "INSERTADO":
            return None, estado

        self._cache[texto] = nuevo_id
        self._siguiente_id += 1
        return nuevo_id, estado


class ResolverRedSocial:
    """Resuelve o crea una fila en RedSocial a partir de su texto."""

    def __init__(self, cursor):
        self.cursor = cursor
        self._cache = {}
        self._siguiente_id = self._obtener_siguiente_id()

    def _obtener_siguiente_id(self):
        self.cursor.execute("SELECT ISNULL(MAX(IdRed), 0) + 1 FROM RedSocial")
        return self.cursor.fetchone()[0]

    def resolver(self, texto):
        """Devuelve (IdRed, estado)."""
        if not texto:
            return None, "ERROR: texto de Red vacío"

        if texto in self._cache:
            return self._cache[texto], "CACHE"

        self.cursor.execute(
            "SELECT IdRed FROM RedSocial WHERE Red = ?", (texto,)
        )
        row = self.cursor.fetchone()
        if row:
            self._cache[texto] = row[0]
            return row[0], "EXISTENTE"

        nuevo_id = self._siguiente_id
        res = exec_sp(self.cursor, "SP_LOADREDSOCIAL", (nuevo_id, texto))
        estado = res.get("Resultado", "ERROR: sin respuesta del SP")

        if estado != "INSERTADO":
            return None, estado

        self._cache[texto] = nuevo_id
        self._siguiente_id += 1
        return nuevo_id, estado


class ResolverFuenteDatosPorTipo:
    """
    Dado un texto de fuente (p.ej. 'Instagram', 'EncuestaInterna'), resuelve
    o crea en cadena:
      1. El TipoFuente correspondiente (vía ResolverTipoFuente).
      2. Una fila en fuente_datos asociada a ese TipoFuente.
    Devuelve el IdFuente resultante, listo para usarse como FK en
    surveys_part1.Fuente o social_comments.IdFuente.

    Nota: si para un mismo texto ya existe una fila de fuente_datos,
    se reutiliza esa (no se crea una nueva fila por cada carga).
    """

    def __init__(self, cursor, resolver_tipo_fuente):
        self.cursor = cursor
        self.resolver_tipo = resolver_tipo_fuente
        self._cache = {}
        self._siguiente_id = self._obtener_siguiente_id()

    def _obtener_siguiente_id(self):
        self.cursor.execute("SELECT ISNULL(MAX(IdFuente), 0) + 1 FROM fuente_datos")
        return self.cursor.fetchone()[0]

    def resolver(self, texto):
        """Devuelve (IdFuente, estado)."""
        if not texto:
            return None, "ERROR: texto de Fuente vacío"

        if texto in self._cache:
            return self._cache[texto], "CACHE"

        id_tipo_fuente, estado_tipo = self.resolver_tipo.resolver(texto)
        if id_tipo_fuente is None:
            return None, f"No se pudo resolver TipoFuente: {estado_tipo}"

        # ¿Ya existe una fila de fuente_datos para este TipoFuente?
        self.cursor.execute(
            "SELECT TOP 1 IdFuente FROM fuente_datos WHERE IdTipoFuente = ?",
            (id_tipo_fuente,),
        )
        row = self.cursor.fetchone()
        if row:
            self._cache[texto] = row[0]
            return row[0], "EXISTENTE"

        # No existe -> crearla con fecha de hoy
        nuevo_id = self._siguiente_id
        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
        res = exec_sp(self.cursor, "SP_LOADFUENTE", (nuevo_id, id_tipo_fuente, fecha_hoy))
        estado = res.get("Resultado", "ERROR: sin respuesta del SP")

        if estado != "INSERTADO":
            return None, estado

        self._cache[texto] = nuevo_id
        self._siguiente_id += 1
        return nuevo_id, estado
