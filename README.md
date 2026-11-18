# Comics Vault

## Descripción

Comics Vault es una aplicación web desarrollada con Django para consultar un catálogo de cómics,
registrar lectores y administrar categorías, publicaciones y mensajes de contacto. Conserva una
interfaz responsive con identidad visual neobrutalista.

El proyecto utiliza una arquitectura MVT distribuida en dos aplicaciones:

- `comic_store/`: configuración del proyecto, archivos estáticos y rutas principales.
- `comics/`: catálogo, categorías, lectores, autenticación, páginas legales y mensajes.
- `administrador/`: alta, edición y eliminación administrativa de cómics, con bitácora.

## Tecnologías

- Python
- Django
- SQLite
- HTML y Tailwind CSS
- JavaScript
- Toastr
- Google Maps
- Pillow

## Requisitos

- Python 3.14 o compatible con Django 6.1.
- PowerShell o terminal compatible.
- Dependencias indicadas en `requirements.txt`.

## Instalación en Windows

Desde la carpeta que contiene `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Variables de entorno

Para desarrollo Django utiliza una clave local si no se define `DJANGO_SECRET_KEY`. No reutilice
ese valor en producción.

```powershell
$env:DJANGO_SECRET_KEY = "clave-secreta-generada-por-el-entorno"
$env:DJANGO_DEBUG = "False"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
```

La configuración predeterminada usa SQLite y el archivo `db.sqlite3`. Las variables no deben
contener espacios adicionales ni comillas dentro del valor almacenado.

## Configuración de correo SMTP

El proyecto puede enviar una notificación al administrador y una respuesta automática al usuario.
Configure las credenciales mediante variables de entorno; no las escriba en archivos del proyecto:

```powershell
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "true"
$env:EMAIL_USE_SSL = "false"
$env:EMAIL_HOST_USER = "tu_correo@gmail.com"
$env:EMAIL_HOST_PASSWORD = "tu_contrasena_de_aplicacion"
$env:DEFAULT_FROM_EMAIL = "tu_correo@gmail.com"
```

Para Gmail debe utilizarse una contraseña de aplicación configurada en la cuenta. Los intentos
fallidos quedan registrados en el log de Django y no exponen la contraseña.

## Migraciones y servidor

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra <http://127.0.0.1:8000/>. No elimine las migraciones ni reinicie la base de datos para aplicar
cambios posteriores al esquema.

## Rutas principales

| Ruta | Función |
| --- | --- |
| `/` | Página de inicio |
| `/catalogo/` | Catálogo y búsqueda |
| `/detalle/<id>/` | Detalle de un cómic |
| `/contacto/` | Formulario de contacto |
| `/gracias/` | Confirmación de recepción |
| `/politica-privacidad/` | Política de privacidad |
| `/terminos-condiciones/` | Términos y condiciones |
| `/listar-mensajes/` | Mensajes recibidos, solo staff |
| `/registro/` | Registro de lector |
| `/login/` | Inicio de sesión |
| `/perfil/` | Perfil del lector |
| `/gestion/nuevo/` | Alta administrativa de cómics |
| `/admin/` | Administración integrada de Django |

## Acceso administrativo

Las vistas administrativas propias requieren `is_staff=True` o `is_superuser=True`.
Para crear un usuario administrador desde la terminal:

```powershell
python manage.py createsuperuser
```

El listado `/listar-mensajes/` muestra 5 mensajes por página. Las operaciones sobre cómics y perfiles
también cuentan con protección de permisos y registros de auditoría cuando corresponde.

## Verificación

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test
```
