# LingoQuesto Backend - Docker Setup Guide

Este manual explica cómo ejecutar LingoQuesto Backend usando Docker y Docker Compose.

## 📋 Tabla de Contenidos

1. [Arquitectura de Servicios](#arquitectura-de-servicios)
2. [Configuración Inicial](#configuración-inicial)
3. [Comandos Básicos](#comandos-básicos)
4. [Gestión de Base de Datos](#gestión-de-base-de-datos)
5. [Configuración Selectiva de Servicios](#configuración-selectiva-de-servicios)
6. [Monitoreo y Logs](#monitoreo-y-logs)
7. [Solución de Problemas](#solución-de-problemas)

## 🏗️ Arquitectura de Servicios

La aplicación está compuesta por los siguientes servicios Docker:

### Servicios Principales

- **`web`**: Servidor Django (puerto 8000)
- **`db`**: Base de datos PostgreSQL 16 (puerto 5432)
- **`redis`**: Cache y message broker (puerto 6380)

### Servicios de Procesamiento

- **`celery-worker`**: Procesador de tareas asíncronas
- **`celery-flower`**: Interfaz de monitoreo Celery (puerto 5555)
- **`celery-beat`**: Programador de tareas (comentado por defecto)

### Volúmenes Persistentes

- `postgres_data`: Datos de PostgreSQL
- `redis_data`: Datos de Redis
- `media_files`: Archivos multimedia subidos
- `static_files`: Archivos estáticos de Django
- `celery_beat_data`: Programación de Celery Beat

## 🚀 Configuración Inicial

### Prerrequisitos

- Docker >= 20.10
- Docker Compose >= 2.0

### 1. Preparación del Entorno

```bash
# Opcional: Copiar configuración personalizada
cp .env.example .env

# El archivo .env.docker ya contiene configuración optimizada para Docker
# No es necesario modificarlo para desarrollo básico
```

### 2. Construcción e Inicio de Servicios

```bash
# Construir todas las imágenes
docker compose build

# Iniciar todos los servicios en background
docker compose up -d

# Ver logs en tiempo real
docker compose up
```

### 3. Configuración de Base de Datos

```bash
# Ejecutar migraciones
docker compose exec web python manage.py migrate
docker compose exec web uv run python manage.py migrate
# Crear superusuario
docker compose exec web python manage.py createsuperuser

# O usar credenciales por defecto del .env.docker:
# Username: admin
# Password: admin123
```

## 🎯 Comandos Básicos

### Gestión de Servicios

```bash
# Iniciar todos los servicios
docker compose up

# Iniciar servicios en background
docker compose up -d

# Detener todos los servicios
docker compose down

# Reiniciar un servicio específico
docker compose restart web

# Ver estado de servicios
docker compose ps

# Reconstruir y reiniciar
docker compose up --build
```

### Comandos Django

El script `entrypoint.sh` proporciona comandos predefinidos:

```bash
# Servidor de desarrollo
docker compose exec web server

# Migraciones
docker compose exec web migrate
docker compose exec web makemigrations

# Shell de Django
docker compose exec web shell

# Ejecutar tests
docker compose exec web test

# Shell de sistema
docker compose exec web bash

# Ver comandos disponibles
docker compose exec web help
```

## 🗄️ Gestión de Base de Datos

### Importar Réplica desde DigitalOcean

#### 1. Hacer Backup de Producción/QA

```bash
# Comando base para hacer backup
pg_dump --no-sync -h [HOST] -p [PORT] -U [USER] -d [DATABASE] > backup-qa-lq-qa-db.sql

# Ejemplo con DigitalOcean
/usr/lib/postgresql/17/bin/pg_dump \
  -h app-4fb09df8-ac78-4674-92df-00a72c6df5d6-do-user-16943065-0.k.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d lq-qa-db > backup-qa-lq-qa-db.sql
```

#### 2. Limpiar el Backup para Docker

```bash
# Limpiar comandos incompatibles y cambiar ownership
sed -e '/^SET transaction_timeout/d' \
    -e '/^ALTER TABLE.*OWNER TO doadmin/d' \
    -e '/^CREATE ROLE doadmin/d' \
    -e 's/OWNER TO doadmin/OWNER TO lqqauser/g' \
    ./backup-qa-lq-qa-db.sql > ./docker/backup-qa-lq-qa-db.sql
```

#### 3. Importar a PostgreSQL Local

```bash
# Asegurarse que la base de datos esté corriendo
docker compose up db -d

# Importar backup limpio
psql -h localhost -p 5432 -U lqqauser -d lq-qa-db < ./docker/backup-qa-lq-qa-db.sql

# O desde el contenedor
docker compose exec db psql -U lqqauser -d lq-qa-db < /docker/backup-cleaned.sql
```

### Acceso Directo a PostgreSQL

```bash
# Conectar a PostgreSQL desde host
psql -h localhost -p 5432 -U lqqauser -d lq-qa-db

# Conectar desde el contenedor
docker compose exec db psql -U lqqauser -d lq-qa-db

# Ejecutar SQL desde archivo
docker compose exec db psql -U lqqauser -d lq-qa-db -f /path/to/script.sql
```

## ⚙️ Configuración Selectiva de Servicios

### Solo Aplicación Web (sin workers)

```bash

# Iniciar solo web, db y redis
docker compose up web db redis
```

### Solo Base de Datos y Redis

```bash
# Para desarrollar localmente con servicios externos
docker compose up db redis -d
```

### Perfil de Servicios Personalizados

Crear `docker-compose.dev.yml`:

```yaml
# docker-compose.dev.yml
services:
  web:
    profiles: ["app"]
  celery-worker:
    profiles: ["workers"]
  celery-flower:
    profiles: ["workers"]
```

```bash
# Solo aplicación
docker compose --profile app up

# Solo workers
docker compose --profile workers up

# Todo
docker compose --profile app --profile workers up
```

## 📊 Monitoreo y Logs

### Acceso a Interfaces Web

- **Django Admin**: http://localhost:8000/admin
- **GraphQL API**: http://localhost:8000/graphql
- **Celery Flower**: http://localhost:5555
- **Auth Specs**: http://localhost:8000/\_allauth/openapi.html

### Logs de Servicios

```bash
# Logs de todos los servicios
docker compose logs -f

# Logs de un servicio específico
docker compose logs -f web
docker compose logs -f celery-worker
docker compose logs -f db

# Últimas 100 líneas
docker compose logs --tail=100 web

# Logs desde hace 10 minutos
docker compose logs --since=10m web
```

### Monitoreo de Recursos

```bash
# Estadísticas de contenedores
docker stats

# Información de volúmenes
docker volume ls
docker volume inspect back-lq-v2_postgres_data

# Espacio usado por Docker
docker system df
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Puerto ya en uso

```bash
# Encontrar proceso usando el puerto
lsof -i :8000
sudo netstat -tulpn | grep :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usa puerto 8001 en lugar de 8000
```

#### 2. Permisos de archivos

```bash
# Cambiar propietario de archivos
sudo chown -R $USER:$USER .

# Permisos para logs
chmod -R 755 logs/
```

#### 3. Base de datos no se conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker compose exec db pg_isready -U lqqauser

# Reiniciar servicio de base de datos
docker compose restart db

# Verificar logs de base de datos
docker compose logs db
```

#### 4. Celery no procesa tareas

```bash
# Verificar conexión a Redis
docker compose exec redis redis-cli ping

# Reiniciar worker
docker compose restart celery-worker

# Verificar logs de worker
docker compose logs celery-worker
```

### Comandos de Limpieza

```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no usadas
docker image prune

# Limpiar todo (¡cuidado con volúmenes!)
docker system prune -a

# Rebuild completo
docker compose down -v  # ¡Elimina volúmenes!
docker compose build --no-cache
docker compose up -d
```

### Variables de Entorno Importantes

```bash
# Verificar variables dentro del contenedor
docker compose exec web env | grep -E "(DATABASE|REDIS|CELERY)"

# Cambiar variables temporalmente
docker compose exec -e DEBUG=False web python manage.py check
```

## 📚 Comandos de Referencia Rápida

```bash
# Setup inicial completo
docker compose build && docker compose up -d
docker compose exec web migrate
docker compose exec web createsuperuser

# Desarrollo diario
docker compose up        # Con logs
docker compose up -d     # En background
docker compose down      # Detener todo

# Base de datos
docker compose exec web shell
docker compose exec db psql -U lqqauser -d lq-qa-db

# Debugging
docker compose logs -f web
docker compose exec web bash
```
