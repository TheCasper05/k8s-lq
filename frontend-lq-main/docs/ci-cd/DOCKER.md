# Docker Setup Guide

Esta guía explica cómo usar Docker y Docker Compose con el monorepo de LingoQuesto.

## Prerrequisitos

- Docker Engine 20.10+
- Docker Compose 2.0+

## Estructura de Archivos Docker

```
frontend-lq/
├── docker-compose.yml           # Configuración de producción
├── .dockerignore                # Archivos ignorados en builds
├── .env.example                 # Variables de entorno de ejemplo
├── apps/
│   ├── student-teacher/
│   │   ├── Dockerfile           # Dockerfile de producción (Nuxt 4)
│   │   └── Dockerfile.dev       # Dockerfile de desarrollo (opcional)
│   └── institutional/
│       ├── Dockerfile           # Dockerfile de producción (Vue + Nginx)
│       ├── Dockerfile.dev       # Dockerfile de desarrollo (opcional)
│       └── nginx.conf           # Configuración de Nginx
└── turbo.json                   # Configuración de Turbo
```

## Comandos Rápidos

### Producción

```bash
# Construir y levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener todos los servicios
docker-compose down

# Reconstruir imágenes
docker-compose build

# Reconstruir y levantar
docker-compose up -d --build
```

### Desarrollo (con hot-reload)

```bash
# Levantar en modo desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Ver logs de desarrollo
docker-compose -f docker-compose.dev.yml logs -f

# Detener servicios de desarrollo
docker-compose -f docker-compose.dev.yml down
```

## Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores:

```env
NUXT_PUBLIC_GRAPHQL_ENDPOINT=http://tu-api:4000/graphql
NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT=ws://tu-api:4000/graphql
NUXT_PUBLIC_SENTRY_DSN=tu-sentry-dsn
```

## Servicios Disponibles

### student-teacher (Nuxt 4)

- **Puerto**: 3000
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000
- **Tecnologías**: Nuxt 4, Vue 3, Node.js

### institutional (Vue + Vite)

- **Puerto**: 8080
- **URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **Tecnologías**: Vue 3, Vite, Nginx

## Builds Optimizados con Turbo

Los Dockerfiles están configurados para usar Turbo, lo que proporciona:

- **Caché inteligente**: Solo reconstruye lo que cambió
- **Builds incrementales**: Más rápidos en reconstrucciones
- **Paralelización**: Builds más eficientes

## Troubleshooting

### Error: Cannot find module

Si encuentras errores de módulos faltantes:

```bash
# Reconstruir completamente las imágenes sin caché
docker-compose build --no-cache

# Limpiar volúmenes y reconstruir
docker-compose down -v
docker-compose up -d --build
```

### Los cambios no se reflejan en desarrollo

Si los cambios no aparecen en modo desarrollo:

```bash
# Reiniciar el servicio específico
docker-compose -f docker-compose.dev.yml restart student-teacher-dev

# O verificar que los volúmenes estén correctamente montados
docker-compose -f docker-compose.dev.yml config
```

### Problemas de permisos

Si encuentras problemas de permisos con los volúmenes:

```bash
# En Linux, asegúrate de que tu usuario tenga permisos
sudo chown -R $USER:$USER apps packages
```

## Limpieza

```bash
# Detener y eliminar contenedores, redes
docker-compose down

# Eliminar también volúmenes
docker-compose down -v

# Eliminar imágenes construidas
docker-compose down --rmi all

# Limpiar todo Docker (¡cuidado!)
docker system prune -a --volumes
```

## Producción

Para desplegar en producción:

1. Configura las variables de entorno en tu servidor
2. Usa un reverse proxy (Nginx, Traefik, etc.) frente a los contenedores
3. Configura SSL/TLS
4. Usa Docker Swarm o Kubernetes para orquestación avanzada

### Ejemplo con Nginx reverse proxy

```nginx
# /etc/nginx/sites-available/lingoquesto

upstream student_teacher {
    server localhost:3000;
}

upstream institutional {
    server localhost:8080;
}

server {
    listen 80;
    server_name app.lingoquesto.com;

    location / {
        proxy_pass http://student_teacher;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 80;
    server_name www.lingoquesto.com;

    location / {
        proxy_pass http://institutional;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoreo

Para ver el estado de los contenedores:

```bash
# Estado general
docker-compose ps

# Uso de recursos
docker stats

# Health checks
docker-compose ps | grep healthy
```
