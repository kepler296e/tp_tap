### Instrucciones para ejecutar (sin Docker)
1. Crear y activar entorno virtual (opcional):
```bash
python -m venv .venv
source .venv/bin/activate
```
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

### Dependencias
- **Django**: Framework principal para desarrollar aplicaciones web en Python.
- **djangorestframework**: Extensión para Django que facilita la creación de APIs REST.
- **psycopg2-binary**: Driver que permite a Django conectarse y trabajar con bases de datos PostgreSQL.
