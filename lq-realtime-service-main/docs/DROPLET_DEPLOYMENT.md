# DigitalOcean Droplet Deployment Guide

Esta guía cubre el proceso completo de deployment del servicio LQ Realtime en DigitalOcean Droplets con CI/CD automatizado.

## Resumen del Proceso

```
GitHub Push → GitHub Actions → Build Docker Image → Push to Registry → SSH to Droplet → Deploy
```

## Prerequisitos

- Cuenta de DigitalOcean
- DigitalOcean Container Registry configurado
- Droplets creados (uno para QA, uno para Producción)
- Instancia de Redis (puede ser DigitalOcean Managed Redis o cualquier otra)

## Paso 1: Configurar DigitalOcean Container Registry

1. Crear un Container Registry en DigitalOcean:
   ```bash
   doctl registry create lq-registry
   ```

2. Obtener el token de acceso:
   - Ve a API → Tokens/Keys
   - Crea un nuevo token con permisos de lectura/escritura
   - Guarda el token (lo necesitarás para GitHub Secrets)

## Paso 2: Crear y Configurar Droplets

### 2.1 Crear Droplets

Crea dos droplets (QA y Producción):

**Especificaciones recomendadas:**
- **QA**: 2 GB RAM / 2 vCPUs / 60 GB SSD
- **Producción**: 4 GB RAM / 2 vCPUs / 80 GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Región**: La más cercana a tus usuarios

### 2.2 Configurar SSH

Genera una clave SSH para el deployment (o usa una existente):

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/lq-deploy
```

Agrega la clave pública a tus droplets:

```bash
# Para cada droplet
ssh-copy-id -i ~/.ssh/lq-deploy.pub root@DROPLET_IP
```

### 2.3 Ejecutar Script de Setup

En cada droplet, ejecuta el script de setup:

```bash
# SSH al droplet
ssh root@DROPLET_IP

# Descargar y ejecutar el script
wget https://raw.githubusercontent.com/YOUR_ORG/lq-realtime-service/main/scripts/setup-droplet.sh
chmod +x setup-droplet.sh
./setup-droplet.sh
```

El script instalará:
- Docker y Docker Compose
- Configuración de firewall (UFW)
- Fail2ban para seguridad
- Creará el directorio `/opt/lq-realtime-service`

## Paso 3: Configurar Redis

Tienes dos opciones:

### Opción A: DigitalOcean Managed Redis (Recomendado)

1. Crea una instancia de Redis en DigitalOcean
2. Anota el host, puerto y password
3. Configura las reglas de firewall para permitir acceso desde tus droplets

### Opción B: Redis en el mismo Droplet

Puedes usar Redis en el mismo droplet, pero no es recomendado para producción:

```bash
docker run -d \
  --name redis \
  --restart unless-stopped \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes
```

## Paso 4: Configurar GitHub Secrets

Ve a tu repositorio → Settings → Secrets and variables → Actions

### Secrets Globales (Repository secrets)

```
DO_REGISTRY_TOKEN     = <tu-token-de-digitalocean>
DO_REGISTRY_NAME      = lq-registry
JWT_SECRET_KEY        = <tu-jwt-secret-key-min-32-chars>
```

### Secrets de Ambiente QA (Environment: qa)

```
QA_DROPLET_HOST       = <ip-del-droplet-qa>
QA_DROPLET_USER       = root
QA_SSH_PRIVATE_KEY    = <contenido-del-archivo-lq-deploy-private-key>
QA_REDIS_HOST         = <redis-host-qa>
QA_REDIS_PORT         = 6379
QA_REDIS_PASSWORD     = <redis-password-si-aplica>
```

### Variables de Ambiente QA (Environment: qa)

```
APP_URL               = http://DROPLET_IP:8082
ALLOWED_ORIGINS       = https://qa.linguoquesto.com,http://localhost:3000
```

### Secrets de Ambiente Production (Environment: production)

```
PROD_DROPLET_HOST     = <ip-del-droplet-production>
PROD_DROPLET_USER     = root
PROD_SSH_PRIVATE_KEY  = <contenido-del-archivo-lq-deploy-private-key>
PROD_REDIS_HOST       = <redis-host-production>
PROD_REDIS_PORT       = 6379
PROD_REDIS_PASSWORD   = <redis-password-si-aplica>
```

### Variables de Ambiente Production (Environment: production)

```
APP_URL               = https://realtime.linguoquesto.com
ALLOWED_ORIGINS       = https://app.linguoquesto.com,https://www.linguoquesto.com
```

## Paso 5: Deployment Automático

### Para QA

```bash
git checkout staging
git merge main
git push origin staging
```

Esto disparará el workflow de deployment a QA automáticamente.

### Para Producción

```bash
git checkout main
git push origin main
```

Esto disparará el workflow de deployment a producción automáticamente.

## Paso 6: Verificar Deployment

### Verificar Health Check

```bash
# Para QA
curl http://QA_DROPLET_IP:8082/health

# Para Producción
curl https://realtime.linguoquesto.com/health
```

Deberías recibir:
```json
{"status": "healthy"}
```

### Ver Logs en el Droplet

```bash
# SSH al droplet
ssh root@DROPLET_IP

# Ver logs
cd /opt/lq-realtime-service
docker-compose -f docker-compose.production.yml logs -f
```

### Ver Status de los Contenedores

```bash
docker-compose -f docker-compose.production.yml ps
```

## Troubleshooting

### El deployment falla en GitHub Actions

1. Verifica que todos los secrets estén configurados correctamente
2. Revisa los logs de GitHub Actions
3. Verifica que el droplet sea accesible vía SSH

### El servicio no inicia

```bash
# SSH al droplet
ssh root@DROPLET_IP
cd /opt/lq-realtime-service

# Ver logs
docker-compose -f docker-compose.production.yml logs

# Verificar variables de entorno
cat .env.production

# Reintentar deployment
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml --env-file .env.production up -d
```

### No se puede conectar a Redis

1. Verifica que Redis esté corriendo:
   ```bash
   # Si Redis está en el mismo droplet
   docker ps | grep redis

   # Si es Managed Redis, verifica la conectividad
   telnet REDIS_HOST REDIS_PORT
   ```

2. Verifica las reglas de firewall en DigitalOcean

3. Verifica las credenciales en los secrets de GitHub

### El health check falla

```bash
# Desde el droplet
curl http://localhost:8082/health

# Ver logs del servicio
docker-compose -f docker-compose.production.yml logs ws-service

# Verificar que el contenedor está corriendo
docker ps
```

## Deployment Manual (Emergencia)

Si necesitas hacer deployment manual:

```bash
# SSH al droplet
ssh root@DROPLET_IP

# Ir al directorio
cd /opt/lq-realtime-service

# Login al registry
echo YOUR_DO_TOKEN | docker login registry.digitalocean.com -u YOUR_DO_TOKEN --password-stdin

# Pull de la imagen
docker pull registry.digitalocean.com/lq-registry/lq-realtime-service:prod-latest

# Actualizar .env.production con los valores correctos
nano .env.production

# Redesplegar
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

## Rollback

Si necesitas hacer rollback a una versión anterior:

```bash
# SSH al droplet
ssh root@DROPLET_IP
cd /opt/lq-realtime-service

# Ver tags disponibles en el registry
doctl registry repository list-tags lq-realtime-service

# Pull de la versión anterior
docker pull registry.digitalocean.com/lq-registry/lq-realtime-service:prod-SHA_ANTERIOR

# Actualizar .env.production
nano .env.production
# Cambiar DOCKER_IMAGE a la versión anterior

# Redesplegar
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml --env-file .env.production up -d
```

## Configuración de Nginx (Opcional)

Si quieres usar Nginx como reverse proxy:

```bash
# Instalar Nginx
apt-get update
apt-get install nginx certbot python3-certbot-nginx

# Crear configuración
nano /etc/nginx/sites-available/lq-realtime
```

```nginx
server {
    listen 80;
    server_name realtime.linguoquesto.com;

    location / {
        proxy_pass http://localhost:8082;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeout
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

```bash
# Activar sitio
ln -s /etc/nginx/sites-available/lq-realtime /etc/nginx/sites-enabled/

# Obtener certificado SSL
certbot --nginx -d realtime.linguoquesto.com

# Reiniciar Nginx
systemctl restart nginx
```

## Monitoreo

### Ver métricas de Docker

```bash
docker stats
```

### Ver uso de recursos

```bash
htop
```

### Logs en tiempo real

```bash
docker-compose -f docker-compose.production.yml logs -f --tail=100
```

## Mantenimiento

### Actualizar paquetes del sistema

```bash
apt-get update
apt-get upgrade -y
```

### Limpiar imágenes Docker antiguas

```bash
docker image prune -a -f
docker system prune -f
```

### Backup de datos de Redis (si aplica)

```bash
# Si Redis está en el droplet
docker exec redis redis-cli BGSAVE
docker cp redis:/data/dump.rdb ./backup-$(date +%Y%m%d).rdb
```

## Próximos Pasos

- Configurar alertas de monitoreo (DataDog, New Relic, etc.)
- Implementar backups automáticos
- Configurar load balancer si se necesitan múltiples instancias
- Implementar auto-scaling si es necesario
