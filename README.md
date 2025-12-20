# LingoQuesto - Kubernetes Deployment

Despliegue completo de la plataforma LingoQuesto en Kubernetes (Minikube) con múltiples servicios: Frontend, Backend Django (GraphQL), Bot FastAPI y Realtime FastAPI.

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Rápida](#instalación-rápida)
- [Servicios Desplegados](#servicios-desplegados)
- [URLs de Acceso](#urls-de-acceso)
- [Comandos Útiles](#comandos-útiles)
- [Troubleshooting](#troubleshooting)

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ingress NGINX                            │
│  lingoquesto.local | api.lingoquesto.local | bot.lingoquesto   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│   Frontend     │   │ Django Backend │   │  FastAPI Bot   │
│ (Nuxt 4/Vue3)  │   │   (GraphQL)    │   │   (AI/LLM)     │
│   Port: 3000   │   │   Port: 8000   │   │   Port: 8081   │
└────────────────┘   └────────┬───────┘   └────────────────┘
                              │
                     ┌────────┴────────┐
                     │                 │
             ┌───────▼────────┐ ┌─────▼──────────┐
             │   PostgreSQL   │ │     Redis      │
             │   Port: 5432   │ │   Port: 6379   │
             └────────────────┘ └────────────────┘
                              │
                     ┌────────▼────────┐
                     │ FastAPI Realtime│
                     │  (WebSocket)    │
                     │   Port: 8082    │
                     └─────────────────┘
```

## 📦 Requisitos Previos

### Software Necesario

- **Docker**: >= 20.10
- **Minikube**: >= 1.30
- **kubectl**: >= 1.27
- **pnpm**: >= 10.15 (para desarrollo frontend)

### Iniciar Minikube

```bash
minikube start --cpus=4 --memory=8192
```

### Habilitar Addons

```bash
minikube addons enable ingress
```

### Configurar Docker para Minikube

```bash
eval $(minikube docker-env)
```

**Importante**: Ejecuta este comando en cada nueva terminal donde vayas a construir imágenes Docker.

## 🚀 Instalación Rápida

### 1. Construir Imágenes Docker

Desde la raíz del proyecto:

```bash
cd /home/jean/Documents/learning_projects/k8s_lq

# Activar el entorno Docker de Minikube
eval $(minikube docker-env)

# Backend Django
docker build -t django-backend:latest ./dj-backend-lq-main

# Bot FastAPI
docker build -t lq-bot:latest ./lq-bot-main

# Realtime FastAPI
docker build -t fastapi-realtime:latest ./lq-realtime-service-main

# Frontend Student-Teacher
cd frontend-lq-main
docker build -f apps/student-teacher/Dockerfile -t frontend-student-teacher:latest .
cd ..
```

**Tamaños de las imágenes**:
- `django-backend:latest` → ~892 MB
- `lq-bot:latest` → ~207 MB
- `fastapi-realtime:latest` → ~239 MB
- `frontend-student-teacher:latest` → ~205 MB

### 2. Desplegar Bases de Datos

```bash
cd k8s

# Desplegar PostgreSQL y Redis
./deploy-databases.sh
```

Verificar que estén corriendo:

```bash
kubectl get pods -n lingoquesto
```

Espera hasta que `postgres-0` y `redis-0` estén en estado `1/1 Running`.

### 3. Crear Schema de PostgreSQL

```bash
kubectl exec -n lingoquesto postgres-0 -- psql -U lq-dbuser -d lq-db -c "CREATE SCHEMA IF NOT EXISTS lq;"
```

### 4. Desplegar Servicios

```bash
./deploy-services.sh
```

### 5. Configurar /etc/hosts

Agrega estas líneas a `/etc/hosts`:

```bash
echo "$(minikube ip) lingoquesto.local api.lingoquesto.local bot.lingoquesto.local realtime.lingoquesto.local" | sudo tee -a /etc/hosts
```

O manualmente:

```bash
sudo nano /etc/hosts
```

Agregar:

```
192.168.49.2 lingoquesto.local
192.168.49.2 api.lingoquesto.local
192.168.49.2 bot.lingoquesto.local
192.168.49.2 realtime.lingoquesto.local
```

### 6. Aplicar Ingress

```bash
kubectl apply -f ingress/ingress-rules.yaml
```

## 🌐 Servicios Desplegados

### Bases de Datos

| Servicio | Tipo | Puerto | Replicas | Almacenamiento |
|----------|------|--------|----------|----------------|
| PostgreSQL 16 | StatefulSet | 5432 | 1 | 10Gi PVC |
| Redis 7 | StatefulSet | 6379 | 1 | 5Gi PVC |

**Conexión interna**:
- PostgreSQL: `postgres:5432` / Database: `lq-db` / User: `lq-dbuser` / Schema: `lq`
- Redis: `redis:6379`

### Aplicaciones

| Servicio | Tipo | Puerto | Replicas | Health Check |
|----------|------|--------|----------|--------------|
| Django Backend | Deployment | 8000 | 2 | `/health/` |
| FastAPI Bot | Deployment | 8081 | 1 | `/health` |
| FastAPI Realtime | Deployment | 8082 | 1 | `/health` |
| Frontend Student-Teacher | Deployment | 3000 | 2 | `/` |

## 🔗 URLs de Acceso

### Frontend (Nuxt 4 + Vue 3)

**Base URL**: http://lingoquesto.local

#### Rutas Públicas (Sin Autenticación)

- **Login**: http://lingoquesto.local/auth/login
- **Login con Email**: http://lingoquesto.local/auth/login/email
- **Registro**: http://lingoquesto.local/auth/register
  - Tipo de cuenta: http://lingoquesto.local/auth/register/account-type
  - Información personal: http://lingoquesto.local/auth/register/personal-info
  - Información institución: http://lingoquesto.local/auth/register/institution-info
  - Preferencias de idioma: http://lingoquesto.local/auth/register/language-preferences
- **Verificar Email**: http://lingoquesto.local/auth/verify-email
- **Recuperar Contraseña**: http://lingoquesto.local/auth/forgot-password
  - Revisar Email: http://lingoquesto.local/auth/forgot-password/check-email
  - Resetear: http://lingoquesto.local/auth/forgot-password/reset
- **OAuth Callbacks**:
  - Google: http://lingoquesto.local/auth/google/callback
  - Microsoft: http://lingoquesto.local/auth/microsoft/callback

#### Rutas de Estudiante (Requiere Autenticación)

- **Dashboard**: http://lingoquesto.local/student/dashboard
- **Perfil**: http://lingoquesto.local/student/profile
- **Cursos**: http://lingoquesto.local/student/courses
- **Tareas**: http://lingoquesto.local/student/assignments
- **Design System**: http://lingoquesto.local/student/design-system
- **Raíz Estudiante**: http://lingoquesto.local/student

#### Rutas de Profesor (Requiere Autenticación)

- **Dashboard**: http://lingoquesto.local/teacher/dashboard
- **Perfil**: http://lingoquesto.local/teacher/profile
- **Clases**: http://lingoquesto.local/teacher/classes
- **Estudiantes**: http://lingoquesto.local/teacher/students
- **Actividades**: http://lingoquesto.local/teacher/activities
- **Design System**: http://lingoquesto.local/teacher/design-system
- **Raíz Profesor**: http://lingoquesto.local/teacher

#### Rutas de Administrador (Requiere Autenticación)

- **Dashboard**: http://lingoquesto.local/admin/dashboard
- **Perfil**: http://lingoquesto.local/admin/profile
- **Usuarios**: http://lingoquesto.local/admin/users
- **Invitaciones**: http://lingoquesto.local/admin/invitations
- **Design System**: http://lingoquesto.local/admin/design-system

#### Ayuda

- **Centro de Ayuda**: http://lingoquesto.local/help

### Backend Django (GraphQL API)

**Base URL**: http://api.lingoquesto.local

#### Endpoints Principales

- **GraphQL Playground**: http://api.lingoquesto.local/graphql/
- **Health Check**: http://api.lingoquesto.local/health/
- **Readiness Check**: http://api.lingoquesto.local/readiness/
- **Liveness Check**: http://api.lingoquesto.local/liveness/
- **Admin Panel**: http://api.lingoquesto.local/admin/
- **Archivos Estáticos**: http://api.lingoquesto.local/static/
- **Archivos Media**: http://api.lingoquesto.local/media/

#### APIs Disponibles

Todas las queries y mutations están disponibles a través de GraphQL en `/graphql/`:

**Ejemplo de Query**:
```bash
curl -X POST http://api.lingoquesto.local/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

**Módulos GraphQL**:
- Autenticación (Login, Register, Token Management)
- Usuarios (Profiles, Roles, Permissions)
- Actividades (CRUD, Assignments)
- Cursos (Courses, Enrollment)
- Tareas (Tasks, Submissions)
- Archivos (Upload, Download)

### FastAPI Bot (AI/LLM Service)

**Base URL**: http://bot.lingoquesto.local

#### Endpoints

- **Health Check**: http://bot.lingoquesto.local/health
- **API Docs (Swagger)**: http://bot.lingoquesto.local/docs
- **ReDoc**: http://bot.lingoquesto.local/redoc
- **OpenAPI Schema**: http://bot.lingoquesto.local/openapi.json

**Funcionalidades**:
- Generación de contenido educativo con LLMs
- Múltiples proveedores (OpenAI, Anthropic, etc.)
- Procesamiento de lenguaje natural
- Evaluación automática

### FastAPI Realtime (WebSocket Service)

**Base URL**: http://realtime.lingoquesto.local (WS: ws://realtime.lingoquesto.local)

#### Endpoints HTTP

- **Health Check**: http://realtime.lingoquesto.local/health
- **API Docs (Swagger)**: http://realtime.lingoquesto.local/docs
- **ReDoc**: http://realtime.lingoquesto.local/redoc

#### WebSocket

- **Connection**: `ws://realtime.lingoquesto.local/ws/{token}`

**Funcionalidades**:
- Chat en tiempo real
- Notificaciones push
- Actualizaciones live de actividades
- Sincronización de estado

## 🛠️ Comandos Útiles

### Verificar Estado

```bash
# Ver todos los pods
kubectl get pods -n lingoquesto

# Ver todos los servicios
kubectl get svc -n lingoquesto

# Ver ingress
kubectl get ingress -n lingoquesto

# Ver detalles de un pod
kubectl describe pod <pod-name> -n lingoquesto

# Ver logs de un pod
kubectl logs <pod-name> -n lingoquesto

# Ver logs en tiempo real
kubectl logs -f <pod-name> -n lingoquesto
```

### Acceder a Contenedores

```bash
# Shell interactivo en un pod
kubectl exec -it <pod-name> -n lingoquesto -- /bin/bash

# Ejecutar comando en PostgreSQL
kubectl exec -n lingoquesto postgres-0 -- psql -U lq-dbuser -d lq-db -c "SELECT * FROM pg_catalog.pg_tables WHERE schemaname = 'lq';"

# Ejecutar comando en Redis
kubectl exec -n lingoquesto redis-0 -- redis-cli PING
```

### Port Forwarding (Desarrollo)

```bash
# Acceder directamente a un servicio sin Ingress
kubectl port-forward -n lingoquesto svc/django-backend 8000:8000
kubectl port-forward -n lingoquesto svc/frontend-student-teacher 3000:3000
kubectl port-forward -n lingoquesto svc/fastapi-bot 8081:8081
kubectl port-forward -n lingoquesto svc/postgres 5432:5432
```

### Reiniciar Servicios

```bash
# Reiniciar un deployment
kubectl rollout restart deployment/django-backend -n lingoquesto
kubectl rollout restart deployment/frontend-student-teacher -n lingoquesto

# Ver estado del rollout
kubectl rollout status deployment/django-backend -n lingoquesto
```

### Reconstruir y Redesplegar

```bash
# 1. Activar entorno Docker de Minikube
eval $(minikube docker-env)

# 2. Reconstruir imagen (ejemplo: frontend)
cd /home/jean/Documents/learning_projects/k8s_lq/frontend-lq-main
docker build -f apps/student-teacher/Dockerfile -t frontend-student-teacher:latest .

# 3. Reiniciar deployment
kubectl rollout restart deployment/frontend-student-teacher -n lingoquesto
```

### Escalar Servicios

```bash
# Escalar replicas
kubectl scale deployment/django-backend --replicas=3 -n lingoquesto
kubectl scale deployment/frontend-student-teacher --replicas=4 -n lingoquesto
```

### Limpiar Todo

```bash
# Eliminar todos los recursos del namespace
kubectl delete namespace lingoquesto

# O eliminar servicios específicos
kubectl delete -f k8s/services/django-backend/
kubectl delete -f k8s/databases/postgres/
```

## 🔧 Troubleshooting

### Pods en CrashLoopBackOff

```bash
# Ver logs del pod
kubectl logs <pod-name> -n lingoquesto --previous

# Ver eventos del pod
kubectl describe pod <pod-name> -n lingoquesto
```

**Problemas comunes**:
- **Frontend**: Verificar que `ssr: true` y `nitro.preset: "node-server"` en `nuxt.config.ts`
- **Backend**: Verificar que las migraciones se ejecutaron y el schema `lq` existe
- **Secrets**: Verificar que todos los secrets estén configurados correctamente

### Health Checks Fallando

```bash
# Probar health check manualmente desde dentro del pod
kubectl exec -n lingoquesto <pod-name> -- curl http://localhost:8000/health/

# Ver eventos del pod
kubectl get events -n lingoquesto --sort-by=.metadata.creationTimestamp
```

### Bases de Datos No Responden

```bash
# PostgreSQL
kubectl exec -n lingoquesto postgres-0 -- psql -U lq-dbuser -d lq-db -c "SELECT 1;"

# Redis
kubectl exec -n lingoquesto redis-0 -- redis-cli PING

# Ver logs
kubectl logs -n lingoquesto postgres-0
kubectl logs -n lingoquesto redis-0
```

### Ingress No Funciona

```bash
# Verificar que el addon esté habilitado
minikube addons list | grep ingress

# Ver logs del ingress controller
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verificar /etc/hosts
cat /etc/hosts | grep lingoquesto

# Probar con IP directa
curl -H "Host: lingoquesto.local" http://$(minikube ip)
```

### Reconstruir Imágenes Desde Cero

```bash
# Activar Docker de Minikube
eval $(minikube docker-env)

# Reconstruir sin cache
docker build --no-cache -t django-backend:latest ./dj-backend-lq-main
docker build --no-cache -t frontend-student-teacher:latest -f ./frontend-lq-main/apps/student-teacher/Dockerfile ./frontend-lq-main

# Reiniciar deployments
kubectl rollout restart deployment/django-backend -n lingoquesto
kubectl rollout restart deployment/frontend-student-teacher -n lingoquesto
```

### Ver Uso de Recursos

```bash
# Uso de recursos por pod
kubectl top pods -n lingoquesto

# Uso de recursos por nodo
kubectl top nodes
```

## 📝 Notas Importantes

### Configuraciones Clave

1. **PostgreSQL Schema**: Todas las tablas de Django están en el schema `lq`, no en `public`
2. **Frontend SSR**: El frontend está configurado con SSR (Server-Side Rendering), no SPA
3. **JWT Keys**: Django tiene configuradas claves JWT para comunicación con el servicio Realtime
4. **CORS**: Configurado para permitir peticiones desde todos los servicios

### Archivos de Configuración

- **Django**: `/k8s/services/django-backend/`
  - `deployment.yaml` - Configuración del deployment
  - `service.yaml` - Exposición del servicio
  - `configmap.yaml` - Variables de entorno públicas
  - `secret.yaml` - Credenciales sensibles (base64)

- **Frontend**: `/k8s/services/frontend-student-teacher/`
- **Bot**: `/k8s/services/fastapi-bot/`
- **Realtime**: `/k8s/services/fastapi-realtime/`
- **Ingress**: `/k8s/ingress/ingress-rules.yaml`

### Desarrollo Local

Para desarrollo, puedes ejecutar servicios localmente y conectarlos a las bases de datos en Minikube usando port-forwarding:

```bash
# Forward de bases de datos
kubectl port-forward -n lingoquesto svc/postgres 5432:5432 &
kubectl port-forward -n lingoquesto svc/redis 6379:6379 &

# Ahora puedes correr Django localmente
cd dj-backend-lq-main
python manage.py runserver

# O el frontend
cd frontend-lq-main/apps/student-teacher
pnpm run dev
```

## 📚 Documentación Adicional

- [Construir Imágenes Docker](k8s/BUILD_IMAGES.md)
- [Configuración de Credenciales](k8s/CREDENTIALS.md)
- [README Kubernetes](k8s/README.md)

## 🎉 ¡Listo!

Tu aplicación LingoQuesto está completamente desplegada en Kubernetes. Accede a:

👉 **http://lingoquesto.local**

---

**Desarrollado con**: Kubernetes, Docker, Django, FastAPI, Nuxt 4, Vue 3, PostgreSQL, Redis
