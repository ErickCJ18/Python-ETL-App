# ETL con Python

Pipeline ETL en Python que carga datos de clientes, productos, encuestas, comentarios
sociales y reseñas web hacia SQL Server mediante stored procedures.

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

- Ninguna credencial ni nombre de servidor vive en el código porque todo sale de `.env`
  (que nunca se sube al repositorio, ver `.gitignore`).
- `src/db.py` solo ejecuta stored procedures que estén en la whitelist `ALLOWED_SPS`
  del `.env`, como defensa adicional contra SQL injection por nombre de SP.
- Los parámetros de cada SP siempre se pasan como placeholders (`?`), nunca
  concatenados en el string SQL.
