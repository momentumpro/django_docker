#!/bin/bash
set -e

echo "Iniciando proceso de despliegue..."

# Desactivar variables de entorno de testing para usar PostgreSQL en producción
unset TEST_DATABASE_ENGINE
unset TEST_DATABASE_NAME

# Crear directorios si no existen
if [ -n "$VOLUME_PATH" ]; then
    echo "Usando volumen de Railway en $VOLUME_PATH"
    mkdir -p "$VOLUME_PATH/static" "$VOLUME_PATH/media"
else
    echo "Usando directorios locales"
    mkdir -p /app/staticfiles /app/media
fi

# Crear migraciones (si es necesario)
echo "Creando migraciones..."
python manage.py makemigrations --noinput || echo "No hay nuevas migraciones para crear"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Asegurar que el sitio con SITE_ID=1 existe
echo "Verificando sitio de Django..."
# Usar RAILWAY_PUBLIC_DOMAIN si está disponible, sino usar SITE_DOMAIN o un valor por defecto
SITE_DOMAIN="${RAILWAY_PUBLIC_DOMAIN:-${SITE_DOMAIN:-djangodocker-production.up.railway.app}}"
SITE_NAME="${SITE_NAME:-Django Docker Production}"
export SITE_DOMAIN SITE_NAME

python manage.py shell << EOF
from django.contrib.sites.models import Site
import os
site_domain = os.environ.get('SITE_DOMAIN', 'djangodocker-production.up.railway.app')
site_name = os.environ.get('SITE_NAME', 'Django Docker Production')
site, created = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': site_domain,
        'name': site_name
    }
)
if not created:
    # Actualizar el dominio si ha cambiado
    if site.domain != site_domain:
        site.domain = site_domain
        site.name = site_name
        site.save()
        print(f"Sitio actualizado: {site.domain}")
    else:
        print(f"Sitio existente: {site.domain}")
else:
    print(f"Sitio creado: {site.domain}")
EOF

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar Gunicorn
echo "Iniciando servidor Gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 project.wsgi:application

