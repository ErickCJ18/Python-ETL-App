from src.resolvers.tipo_fuente_resolver import resolver_tipo_fuente


def test_resolver_tipo_fuente_valores_conocidos():
    assert resolver_tipo_fuente("Web") == "WEB"
    assert resolver_tipo_fuente("social") == "SOCIAL"
    assert resolver_tipo_fuente("Encuesta") == "SURVEY"


def test_resolver_tipo_fuente_valor_desconocido():
    assert resolver_tipo_fuente("xyz") == "DESCONOCIDO"
    assert resolver_tipo_fuente("") == "DESCONOCIDO"
    assert resolver_tipo_fuente(None) == "DESCONOCIDO"
