from src.db import exec_sp

class ResolverTipoFuente:
    def __init__(self, cursor):
        self.cursor = cursor
        self._cache = {}

    def resolver(self, texto):
        if not texto:
            return None, "ERROR: texto de TipoFuente vacio"

        if texto in self._cache:
            return self._cache[texto], "CACHE"

        res = exec_sp(self.cursor, "SP_LOADTIPOFUENTE", (texto,))
        estado = res.get("Resultado", "ERROR: sin respuesta del SP")
        id_tipo = res.get("IdFuenteType")

        if estado.startswith("ERROR") or id_tipo is None:
            return None, estado

        self._cache[texto] = id_tipo
        return id_tipo, estado
