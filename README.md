# Comics Vault

Aplicación Django con arquitectura MVT multiapp:

- `comic_store/`: configuración, ASGI/WSGI y enrutamiento del proyecto Django.
- `comics/`: catálogo, cómics, categorías, registro/autenticación y perfiles de lectores.
- `administrador/`: operaciones administrativas de cómics y bitácora.

El catálogo admite búsquedas por título o autor y filtros por categoría. Crear, editar y
eliminar cómics, administrar categorías y gestionar perfiles de lectores están limitados
a usuarios staff o superusuarios. Las portadas se guardan en `media/portadas/`.

## Requisitos

- Python 3.10 o superior.
- PowerShell en Windows.
- Dependencias de `requirements.txt`.

## Instalación en Windows

Desde la carpeta que contiene `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación, puede usar el intérprete del entorno sin activarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para desarrollo, Django usa un valor de clave local no secreto si no se define
`DJANGO_SECRET_KEY`. No reutilice ese valor en producción. En PowerShell genere y
configure una clave privada para la sesión:

```powershell
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Para producción configure también `DJANGO_DEBUG=False` y `DJANGO_ALLOWED_HOSTS` con
los nombres de host permitidos. La configuración de base de datos predeterminada es
SQLite (`db.sqlite3`); puede ajustarse en `comic_store/settings.py`.

## Base de datos y ejecución

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra <http://127.0.0.1:8000/>. La administración de Django está en
<http://127.0.0.1:8000/admin/>. El panel administrativo propio se encuentra bajo
`/gestion/`; las acciones administrativas se guardan en `ReporteBitacora`.

## Verificación

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test
```

No se debe borrar ni regenerar la base de datos ni las migraciones para actualizar el
proyecto: los cambios del esquema se aplican creando y ejecutando migraciones nuevas.
