#!/bin/bash

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
until python manage.py check --database default 2>&1 | grep -q "System check identified\|no issues"; do
  echo "PostgreSQL no está listo todavía - esperando..."
  sleep 2
done

echo "PostgreSQL está listo. Creando y ejecutando migraciones..."

# Crear migraciones si no existen
python manage.py makemigrations

# Ejecutar migraciones
python manage.py migrate

# Cargar datos de ejemplo
python manage.py loaddata fixtures.json

# Crear superuser si no existe
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
