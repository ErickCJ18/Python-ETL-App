# ETL App

Pipeline ETL en Python que carga datos de clientes, productos, encuestas, comentarios
sociales y reseñas web hacia SQL Server mediante stored procedures.

## Estructura

```
etlapp/
├── .env                  # credenciales reales (no se commitea)
├── .env.example          # plantilla de configuración
├── config/
│   └── settings.py       # toda la config viene de variables de entorno
├── src/
│   ├── db.py             # conexión + ejecución segura de SPs (whitelist)
│   ├── logger.py         # logging a consola y archivo
│   ├── loaders/          # un archivo por fuente: solo leen CSV e insertan
│   └── resolvers/        # lógica de clasificación/transformación
├── data/                 # CSVs (ignorados por git)
├── logs/                 # logs por fecha (ignorados por git)
├── tests/
└── main.py               # orquestador del pipeline
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edita .env con tu servidor, base de datos y SPs permitidos
```

## Ejecutar

```bash
python main.py
```

Los logs quedan en `logs/etl_YYYYMMDD.log` y también se imprimen en consola.

## Seguridad

- Ninguna credencial ni nombre de servidor vive en el código: todo sale de `.env`
  (que nunca se sube al repositorio, ver `.gitignore`).
- `src/db.py` solo ejecuta stored procedures que estén en la whitelist `ALLOWED_SPS`
  del `.env`, como defensa adicional contra SQL injection por nombre de SP.
- Los parámetros de cada SP siempre se pasan como placeholders (`?`), nunca
  concatenados en el string SQL.
- Los CSV de `data/` están en `.gitignore`: si contienen datos reales de clientes,
  no deben terminar versionados en el repositorio.

## Migrar los loaders existentes

Usa `src/loaders/clientes.py` como plantilla: cada loader debe limitarse a leer el
CSV y llamar al SP correspondiente vía `exec_sp`. Cualquier lógica de clasificación
o normalización de datos va en `src/resolvers/`, no en el loader.

## Tests

```bash
pytest tests/
```
