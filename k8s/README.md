# LingoQuesto - Kubernetes Deployment

Configuración de Kubernetes para el ecosistema LingoQuesto.

## 📋 Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Credenciales y Configuración](#credenciales-y-configuración)
- [Despliegue](#despliegue)
- [Comandos Útiles](#comandos-útiles)
- [Arquitectura](#arquitectura)

---

## 🔧 Prerequisitos

### Software Requerido

```bash
# Minikube (Kubernetes local)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl (CLI de Kubernetes)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Verificar instalación
minikube version
kubectl version --client
```

### Iniciar Minikube

```bash
# Iniciar Minikube con recursos adecuados
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verificar estado
minikube status

# Habilitar addons útiles
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard
```

---

## 📁 Estructura del Proyecto

```
k8s/
├── base/
│   ├── namespace.yaml          # Namespace 'lingoquesto'
│   └── kustomization.yaml      # (Futuro: Kustomize config)
│
├── databases/
│   ├── postgres/
│   │   ├── secret.yaml         # Credenciales de PostgreSQL
│   │   ├── pvc.yaml            # Almacenamiento persistente (5GB)
│   │   ├── statefulset.yaml    # PostgreSQL StatefulSet
│   │   └── service.yaml        # Service (postgres:5432)
│   │
│   └── redis/
│       ├── configmap.yaml      # Configuración de Redis
│       ├── pvc.yaml            # Almacenamiento persistente (2GB)
│       ├── statefulset.yaml    # Redis StatefulSet
│       └── service.yaml        # Service (redis:6379)
│
├── services/
│   ├── django-backend/         # (Próximamente)
│   ├── fastapi-bot/            # (Próximamente)
│   ├── fastapi-realtime/       # (Próximamente)
│   ├── frontend-student-teacher/
│   └── frontend-institutional/
│
├── ingress/
│   └── ingress-rules.yaml      # (Próximamente)
│
└── README.md                    # Este archivo
```

---

## 🔐 Credenciales y Configuración

### PostgreSQL

**Service DNS:** `postgres.lingoquesto.svc.cluster.local` (o simplemente `postgres`)

**Credenciales:**
```bash
Usuario:   lq-dbuser
Password:  lq-secure-password-2024
Database:  lq-db
Puerto:    5432
```

**Connection String:**
```bash
postgresql://lq-dbuser:lq-secure-password-2024@postgres:5432/lq-db
```

**Con opciones adicionales (Django):**
```bash
postgresql://lq-dbuser:lq-secure-password-2024@postgres:5432/lq-db?sslmode=disable&options=-c%20search_path%3Dlq
```

### Redis

**Service DNS:** `redis.lingoquesto.svc.cluster.local` (o simplemente `redis`)

**Configuración:**
```bash
Host:      redis
Puerto:    6379
Password:  (ninguno - desarrollo local)
DB:        0
SSL:       false
```

**Connection String:**
```bash
redis://redis:6379/0
```

### Nombres de Services (DNS)

Todos los servicios en el namespace `lingoquesto` pueden comunicarse usando:

| Servicio | DNS Corto | DNS Completo |
|----------|-----------|--------------|
| PostgreSQL | `postgres` | `postgres.lingoquesto.svc.cluster.local` |
| Redis | `redis` | `redis.lingoquesto.svc.cluster.local` |
| Django Backend | `django-backend` | `django-backend.lingoquesto.svc.cluster.local` |
| FastAPI Bot | `fastapi-bot` | `fastapi-bot.lingoquesto.svc.cluster.local` |
| FastAPI Realtime | `fastapi-realtime` | `fastapi-realtime.lingoquesto.svc.cluster.local` |
| Frontend Student | `frontend-student-teacher` | `frontend-student-teacher.lingoquesto.svc.cluster.local` |
| Frontend Institutional | `frontend-institutional` | `frontend-institutional.lingoquesto.svc.cluster.local` |

---

## 🚀 Despliegue

### Fase 1: Desplegar Bases de Datos

#### Paso 1: Crear Namespace

```bash
kubectl apply -f base/namespace.yaml

# Verificar
kubectl get namespaces
```

#### Paso 2: Desplegar PostgreSQL

```bash
# Aplicar en orden
kubectl apply -f databases/postgres/secret.yaml
kubectl apply -f databases/postgres/pvc.yaml
kubectl apply -f databases/postgres/statefulset.yaml
kubectl apply -f databases/postgres/service.yaml

# Verificar despliegue
kubectl get all -n lingoquesto -l app=postgres

# Ver logs
kubectl logs -f postgres-0 -n lingoquesto

# Esperar a que esté listo (puede tomar 30-60 segundos)
kubectl wait --for=condition=ready pod/postgres-0 -n lingoquesto --timeout=120s
```

#### Paso 3: Desplegar Redis

```bash
# Aplicar en orden
kubectl apply -f databases/redis/configmap.yaml
kubectl apply -f databases/redis/pvc.yaml
kubectl apply -f databases/redis/statefulset.yaml
kubectl apply -f databases/redis/service.yaml

# Verificar despliegue
kubectl get all -n lingoquesto -l app=redis

# Ver logs
kubectl logs -f redis-0 -n lingoquesto

# Esperar a que esté listo
kubectl wait --for=condition=ready pod/redis-0 -n lingoquesto --timeout=120s
```

#### Paso 4: Verificar Todo

```bash
# Ver todos los recursos en el namespace
kubectl get all -n lingoquesto

# Debería mostrar:
# - 2 Pods (postgres-0, redis-0)
# - 2 Services (postgres, redis)
# - 2 StatefulSets (postgres, redis)
# - 2 PVCs (postgres-pvc, redis-pvc)
```

---

## 🧪 Comandos Útiles

### Debugging General

```bash
# Ver todos los recursos
kubectl get all -n lingoquesto

# Describir un recurso (muestra eventos y configuración)
kubectl describe pod postgres-0 -n lingoquesto
kubectl describe service postgres -n lingoquesto

# Ver logs en tiempo real
kubectl logs -f postgres-0 -n lingoquesto
kubectl logs -f redis-0 -n lingoquesto

# Ver logs anteriores (si el Pod se reinició)
kubectl logs postgres-0 -n lingoquesto --previous

# Ejecutar comandos dentro de un Pod
kubectl exec -it postgres-0 -n lingoquesto -- /bin/sh
```

### PostgreSQL

```bash
# Conectarse a PostgreSQL desde el Pod
kubectl exec -it postgres-0 -n lingoquesto -- psql -U lq-dbuser -d lq-db

# Ver bases de datos
kubectl exec -it postgres-0 -n lingoquesto -- psql -U lq-dbuser -l

# Ejecutar query desde la terminal
kubectl exec -it postgres-0 -n lingoquesto -- \
  psql -U lq-dbuser -d lq-db -c "SELECT version();"

# Port-forward para conectarte desde tu máquina local
kubectl port-forward -n lingoquesto pod/postgres-0 5432:5432
# Ahora puedes conectarte con: psql -h localhost -U lq-dbuser -d lq-db
```

### Redis

```bash
# Conectarse a Redis CLI
kubectl exec -it redis-0 -n lingoquesto -- redis-cli

# Ver keys almacenadas
kubectl exec -it redis-0 -n lingoquesto -- redis-cli KEYS '*'

# Ver configuración
kubectl exec -it redis-0 -n lingoquesto -- redis-cli CONFIG GET maxmemory

# Test de ping
kubectl exec -it redis-0 -n lingoquesto -- redis-cli ping

# Port-forward para conectarte desde tu máquina local
kubectl port-forward -n lingoquesto pod/redis-0 6379:6379
# Ahora puedes conectarte con: redis-cli -h localhost
```

### Secrets

```bash
# Ver secrets
kubectl get secrets -n lingoquesto

# Decodificar un valor
kubectl get secret postgres-secret -n lingoquesto -o jsonpath='{.data.POSTGRES_USER}' | base64 -d
kubectl get secret postgres-secret -n lingoquesto -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d
```

### Storage

```bash
# Ver PVCs
kubectl get pvc -n lingoquesto

# Ver detalles de un PVC
kubectl describe pvc postgres-pvc -n lingoquesto

# Ver uso de almacenamiento
kubectl exec -it postgres-0 -n lingoquesto -- df -h /var/lib/postgresql/data
kubectl exec -it redis-0 -n lingoquesto -- df -h /data
```

### Limpieza

```bash
# Eliminar recursos específicos
kubectl delete -f databases/postgres/
kubectl delete -f databases/redis/

# Eliminar todo el namespace (⚠️ ELIMINA TODO)
kubectl delete namespace lingoquesto

# Reiniciar un StatefulSet (sin perder datos)
kubectl rollout restart statefulset/postgres -n lingoquesto
kubectl rollout restart statefulset/redis -n lingoquesto
```

---

## 🏗️ Arquitectura

### Diagrama de Componentes (Bases de Datos)

```
┌─────────────────────────────────────────────────────────┐
│              Namespace: lingoquesto                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ PostgreSQL   │         │    Redis     │            │
│  │  Pod         │         │    Pod       │            │
│  │              │         │              │            │
│  │ postgres-0   │         │  redis-0     │            │
│  │  :5432       │         │   :6379      │            │
│  └──────┬───────┘         └──────┬───────┘            │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ postgres-pvc │         │  redis-pvc   │            │
│  │    5GB       │         │    2GB       │            │
│  └──────────────┘         └──────────────┘            │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ Service      │         │  Service     │            │
│  │ postgres     │         │   redis      │            │
│  │  :5432       │         │   :6379      │            │
│  └──────────────┘         └──────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Aplicaciones** se conectan a los Services (`postgres:5432`, `redis:6379`)
2. **Services** enrutan el tráfico a los Pods
3. **Pods** acceden a datos persistentes en los PVCs
4. **PVCs** mantienen los datos incluso si los Pods se reinician

---

## 📚 Próximos Pasos

- [ ] Desplegar servicios de aplicación (Django, FastAPI)
- [ ] Configurar Ingress para acceso externo
- [ ] Implementar ConfigMaps para cada servicio
- [ ] Configurar Secrets para API keys
- [ ] Agregar monitoreo con Prometheus/Grafana

---

## 🆘 Troubleshooting

### PostgreSQL no inicia

```bash
# Ver eventos del Pod
kubectl describe pod postgres-0 -n lingoquesto

# Ver logs detallados
kubectl logs postgres-0 -n lingoquesto

# Problemas comunes:
# - PVC no creado: kubectl get pvc -n lingoquesto
# - Secret no encontrado: kubectl get secret postgres-secret -n lingoquesto
```

### Redis no acepta conexiones

```bash
# Verificar que el Pod esté listo
kubectl get pod redis-0 -n lingoquesto

# Probar conexión
kubectl exec -it redis-0 -n lingoquesto -- redis-cli ping

# Verificar configuración
kubectl exec -it redis-0 -n lingoquesto -- cat /usr/local/etc/redis/redis.conf
```

### No puedo conectarme desde mi máquina local

```bash
# Usar port-forward para debugging
kubectl port-forward -n lingoquesto svc/postgres 5432:5432 &
kubectl port-forward -n lingoquesto svc/redis 6379:6379 &

# Ahora puedes conectarte a localhost:5432 y localhost:6379
```

---

**¡Listo para la Fase 4: Desplegar Servicios de Aplicación!** 🚀
