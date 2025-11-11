#!/bin/bash

# Ejecutar migraciones
python manage.py migrate

# Cargar datos de ejemplo
python manage.py loaddata fixtures.json

# Crear superuser si no existe
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
