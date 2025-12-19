# 🐳 Guía para Construir Imágenes Docker

Antes de desplegar los servicios en Kubernetes, necesitas construir las imágenes Docker.

## ⚙️ Configurar Docker para usar Minikube

```bash
# Configurar el entorno de Docker para usar el daemon de Minikube
eval $(minikube docker-env)

# Verificar que estás usando el Docker de Minikube
docker ps

# Para volver al Docker local (si lo necesitas)
eval $(minikube docker-env -u)
```

---

## 📦 Construir Imágenes

### 1. FastAPI Bot (lq-bot)

```bash
# Desde la raíz del proyecto
cd ../lq-bot-main

# Construir imagen
docker build -t lq-bot:latest .

# Verificar
docker images | grep lq-bot
```

---

### 2. Django Backend (dj-backend)

```bash
# Desde la raíz del proyecto
cd ../dj-backend-lq-main

# Construir imagen
docker build -t django-backend:latest .

# Verificar
docker images | grep django-backend
```

---

### 3. FastAPI Realtime Service

```bash
# Desde la raíz del proyecto
cd ../lq-realtime-service-main

# Construir imagen
docker build -t fastapi-realtime:latest .

# Verificar
docker images | grep fastapi-realtime
```

---

### 4. Frontend Student-Teacher (Nuxt 4)

```bash
# Desde la raíz del MONOREPO frontend
cd ../frontend-lq-main

# ⚠️ IMPORTANTE: Construir desde la raíz del monorepo
docker build -f apps/student-teacher/Dockerfile -t frontend-student-teacher:latest .

# Verificar
docker images | grep frontend-student-teacher
```

---

### 5. Frontend Institutional (Vue 3 + Nginx)

```bash
# Desde la raíz del MONOREPO frontend
cd ../frontend-lq-main

# ⚠️ IMPORTANTE: Construir desde la raíz del monorepo
docker build -f apps/institutional/Dockerfile -t frontend-institutional:latest .

# Verificar
docker images | grep frontend-institutional
```

---

## 🚀 Script Automatizado

Puedes usar este script para construir todas las imágenes de una vez:

```bash
#!/bin/bash

# Ir a la raíz del proyecto
cd "$(dirname "$0")/.."

# Configurar Docker para Minikube
eval $(minikube docker-env)

echo "🐳 Construyendo imágenes Docker para Minikube..."

# FastAPI Bot
echo "📦 1/5 - Construyendo lq-bot..."
cd lq-bot-main && docker build -t lq-bot:latest . && cd ..

# Django Backend
echo "📦 2/5 - Construyendo django-backend..."
cd dj-backend-lq-main && docker build -t django-backend:latest . && cd ..

# FastAPI Realtime
echo "📦 3/5 - Construyendo fastapi-realtime..."
cd lq-realtime-service-main && docker build -t fastapi-realtime:latest . && cd ..

# Frontend Student-Teacher
echo "📦 4/5 - Construyendo frontend-student-teacher..."
cd frontend-lq-main && docker build -f apps/student-teacher/Dockerfile -t frontend-student-teacher:latest . && cd ..

# Frontend Institutional
echo "📦 5/5 - Construyendo frontend-institutional..."
cd frontend-lq-main && docker build -f apps/institutional/Dockerfile -t frontend-institutional:latest . && cd ..

echo "✅ Todas las imágenes construidas!"
docker images | grep -E "lq-bot|django-backend|fastapi-realtime|frontend"
```

Guarda este script como `build-all-images.sh` y ejecútalo:

```bash
chmod +x build-all-images.sh
./build-all-images.sh
```

---

## 🔍 Verificar Imágenes

```bash
# Ver todas las imágenes construidas
docker images | grep -E "lq-bot|django-backend|fastapi-realtime|frontend"

# Debería mostrar:
# lq-bot                    latest
# django-backend            latest
# fastapi-realtime          latest
# frontend-student-teacher  latest
# frontend-institutional    latest
```

---

## ⚠️ Problemas Comunes

### Problema: "Error: Cannot connect to Docker daemon"

**Solución:**
```bash
# Asegúrate de haber ejecutado:
eval $(minikube docker-env)
```

### Problema: "BUILD FAILED" en frontends

**Solución:**
- Los frontends deben construirse desde la raíz del monorepo (`frontend-lq-main`)
- Usa el flag `-f apps/[app]/Dockerfile`

### Problema: Imagen no encontrada en K8s

**Solución:**
- Verifica que `imagePullPolicy: Never` esté en el Deployment
- Confirma que construiste la imagen con el Docker de Minikube

---

## 🔄 Reconstruir Imágenes

Si haces cambios en el código y necesitas reconstruir:

```bash
# Reconstruir una imagen específica
eval $(minikube docker-env)
cd [directorio-del-servicio]
docker build -t [nombre-imagen]:latest .

# Reiniciar el deployment en K8s
kubectl rollout restart deployment/[nombre-deployment] -n lingoquesto
```

Ejemplo:
```bash
# Reconstruir Django Backend
eval $(minikube docker-env)
cd dj-backend-lq-main
docker build -t django-backend:latest .

# Reiniciar deployment
kubectl rollout restart deployment/django-backend -n lingoquesto
```

---

**¡Listo!** Una vez construidas las imágenes, puedes desplegar los servicios con el script de despliegue.
