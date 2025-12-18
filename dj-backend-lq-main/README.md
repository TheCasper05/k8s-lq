# LingoQuesto Backend

This is the backend for the LingoQuesto project developed with Django.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package and project manager)
- Python: uv will automatically use the version specified in the `.python-version` file

## Installation for local development:

1. Clone this repository using [GitHub CLI](https://cli.github.com/):

```bash
gh repo clone LingoQuesto/back-lq-v2
cd back-lq-v2
```

2. Sync environment:

```bash
uv sync
```

3. Create a `.env` file in the project root based on the `.env.example` file:

```bash
cp .env.example .env
```

4. Edit the `.env` file with your configurations:
   _Only the `GOOGLE_CLIENT_ID` and `GOOGLE_SECRET` variables are mandatory. The rest can be left as is for local development._

| Variable                       | Description                                           |
| ------------------------------ | ----------------------------------------------------- |
| DEBUG                          | Debug mode (True in development, False in production) |
| SECRET_KEY                     | Django secret key                                     |
| ALLOWED_HOSTS                  | Allowed hosts separated by commas                     |
| DATABASE_URL                   | Database connection URL                               |
| STATIC_ROOT                    | Static files path                                     |
| STATIC_URL                     | URL for static files                                  |
| MEDIA_URL                      | URL for media files                                   |
| MEDIA_ROOT                     | Media files path                                      |
| ENDPOINT_URL_FRONTEND_ST          | Frontend URL                                          |
| GOOGLE_CLIENT_ID               | Google OAuth Client ID                                |
| GOOGLE_SECRET                  | Google OAuth Secret Key                               |
| EMAIL_URL                      | Email configuration URL                               |
| HEADLESS_SERVE_SPECIFICATION   | Serve API specifications (True/False)                 |
| CORS_ALLOWED_ORIGINS           | CORS allowed origins separated by commas              |
| CSRF_TRUSTED_ORIGINS           | CSRF trusted origins separated by commas              |
| SESSION_COOKIE_SECURE          | Secure session cookies (True in production)           |
| CSRF_COOKIE_SECURE             | Secure CSRF cookies (True in production)              |
| SECURE_SSL_REDIRECT            | SSL redirection (True in production)                  |
| SECURE_HSTS_SECONDS            | HSTS duration in seconds                              |
| SECURE_HSTS_INCLUDE_SUBDOMAINS | Include subdomains in HSTS (True in production)       |
| SECURE_HSTS_PRELOAD            | HSTS preload (True in production)                     |

## Database Migrations

Apply migrations to create the database structure:

```bash
./manage.py migrate
```

## Create Superuser (Optional)

Create an admin user to access the administration panel:

```bash
./manage.py createsuperuser
```

## Run the Development Server

```bash
./manage.py runserver
```

The server will start at [http://localhost:8000](http://localhost:8000)

## Development tooling

Before running tests or committing code, sync the dev dependencies so tools like `ruff` and `pre-commit` are available:

```bash
uv sync --group dev
```

Install the `pre-commit` hook once per clone to automatically format files before each commit and keep the repository consistent:

```bash
pre-commit install
```

If you ever need to format everything or validate the hook manually, run:

```bash
pre-commit run --all-files
```

## Project Features

- Framework: Django
- API: GraphQL with Graphene
- Authentication: Django-allauth (includes social authentication with Google)
- Security: CORS, CSRF, HSTS
- Internationalization: Support for multiple languages (English, Spanish, German, Arabic)

## Application Structure

- **core**: Core functionalities
- **accounts**: User management
- **activities**: System activities
- **analytics**: Analysis and metrics
- **billing**: Billing and payments
- **evaluation**: User evaluation
- **learning**: Learning system
- **notifications**: Notification system

## API Access

The GraphQL API is available at [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Admin Panel

The Django admin panel is available at [http://localhost:8000/admin](http://localhost:8000/admin)

## Auth

The authentication system uses Django-allauth, Specifications are available at [http://localhost:8000/\_allauth/openapi.html](http://localhost:8000/_allauth/openapi.html)

## Load initial data

https://coderwall.com/p/mvsoyg/django-dumpdata-and-loaddata

Search folder fixtures # TODO: complete this doc

### Para exportar los paquetes gestionados por **uv** a un archivo `requirements.txt`, puedes utilizar el siguiente comando:

```bash
uv export --format requirements-txt > requirements.txt
```

Este comando genera un archivo `requirements.txt` con las versiones exactas de las dependencias definidas en tu archivo `uv.lock`.

Si prefieres que el archivo generado no incluya los hashes de las dependencias (útil en ciertos entornos como Docker o CI/CD), puedes añadir la opción `--no-hashes`:

```bash
uv export --format requirements-txt --no-hashes > requirements.txt
```

Esto es especialmente útil si tu pipeline de CI/CD o entorno de despliegue no requiere verificación de hashes.

### Recomendaciones

- **No mantengas ambos archivos (`uv.lock` y `requirements.txt`) en tu repositorio**: La documentación oficial de uv sugiere evitar mantener ambos archivos simultáneamente para prevenir inconsistencias. ([Locking and syncing | uv - Astral Docs](https://docs.astral.sh/uv/concepts/projects/sync/?utm_source=chatgpt.com))

- **Utiliza `uv.lock` para el desarrollo**: Este archivo asegura entornos reproducibles durante el desarrollo.

- **Genera `requirements.txt` para despliegues**: Si tu entorno de producción o herramientas de CI/CD requieren un archivo `requirements.txt`, genera este archivo a partir de `uv.lock` utilizando el comando mencionado anteriormente.

# rebuild
# hola 
docker build . -t registry.digitalocean.com/lq-registry/dj-backend:qa-latest

docker push registry.digitalocean.com/lq-registry/dj-backend:qa-latest
docker pull registry.digitalocean.com/lq-registry/dj-backend:qa-latest
docker stop dj-backend-lq-qa
docker rm dj-backend-lq-qa
docker run -d --name dj-backend-lq-qa --network lq-net --restart unless-stopped -p 8000:8000 --env-file ./dj-backend-lq/.env.qa registry.digitalocean.com/lq-registry/dj-backend:qa-latest


