# 📚 Documentación de LingoQuesto Frontend

Guías y documentación para el monorepo de LingoQuesto.

## 🔧 Desarrollo

### GraphQL Codegen

**Configuración de variables de entorno**

Para generar tipos TypeScript desde el schema GraphQL, necesitas configurar el archivo `.env` en el **root del
monorepo**:

```shell
# GraphQL Codegen - Build time (para generar tipos TypeScript)
GRAPHQL_ENDPOINT=http://localhost:4000/graphql

# GraphQL Runtime - Endpoints para las apps
NUXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql
```

**Comandos**:

```bash
# Generar tipos desde el schema
pnpm graphql:codegen

# Modo watch (regenera automáticamente)
pnpm graphql:watch
```

**Troubleshooting común**:

- **Error: "Failed to load schema from undefined"**
  - Verifica que `GRAPHQL_ENDPOINT` esté en `.env` del root
  - Asegúrate de que el backend esté corriendo
- **Error: "Unable to find any GraphQL type definitions"**
  - Verifica que existan queries/mutations en `packages/graphql/src/`

👉 Ver [DEVELOPMENT.md#graphql](./DEVELOPMENT.md#graphql) para más detalles.

---

## 🚀 CI/CD y Deployment

### [AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md)

**Guía completa de configuración de AWS Amplify**

- ✅ Setup paso a paso de CI/CD
- ✅ Configuración de monorepo en Amplify
- ✅ Variables de entorno por app
- ✅ Troubleshooting común
- ✅ Comandos útiles

👉 **Empieza aquí** si es tu primera vez configurando Amplify.

---

### [SELECTIVE_DEPLOYMENT.md](./SELECTIVE_DEPLOYMENT.md)

**Estrategia de deploy selectivo en monorepo**

- ⚡ Cómo funciona el deploy selectivo
- 📊 Escenarios reales con ejemplos
- 💰 Ahorro de costos y tiempo
- 🧪 Tests del sistema
- ✅ Best practices

👉 Lee esto para entender **cuándo se despliega cada app**.

---

### [ENVIRONMENTS.md](./ENVIRONMENTS.md)

**Manejo de ambientes (Staging y Production)**

- 🌍 Configuración de múltiples ambientes
- 🔑 Secrets y variables por ambiente
- 🚀 Deploy automático por branch
- 📊 GitHub Environments setup
- ✅ Flujos de trabajo completos

👉 Lee esto para **configurar staging (QA) y production**

---

### [DOCKER_VS_NATIVE.md](./DOCKER_VS_NATIVE.md)

**Comparación: Docker vs Native Build**

- 📊 Tabla comparativa
- 💰 Análisis de costos
- 🐳 Configuración Docker (si la necesitas)
- 🎯 Recomendación para LingoQuesto

👉 Lee esto si te preguntas **"¿debo usar Docker?"**

---

### [HOSTING_COMPARISON.md](./HOSTING_COMPARISON.md)

**Comparación de opciones de hosting**

- 💰 Amplify vs S3 vs DigitalOcean
- 📊 Análisis de costos detallado
- 🎯 Recomendaciones por caso de uso
- 📈 Proyección de costos a 1 año

👉 Lee esto si te preguntas **"¿qué hosting es más barato?"**

---

### [S3_CLOUDFRONT_SETUP.md](./S3_CLOUDFRONT_SETUP.md)

**Guía de migración a S3 + CloudFront**

- 🪣 Configuración de S3 buckets
- ☁️ Setup de CloudFront
- 🚀 Workflows de GitHub Actions para S3
- 💰 Ahorro: ~$36/año vs Amplify

👉 Usa esto para **migrar a la opción más económica**

---

## 🔧 Archivos de Configuración

### [amplify-cicd-policy.json](./amplify-cicd-policy.json)

Política IAM para el usuario de CI/CD en AWS.

```bash
# Úsalo así:
aws iam put-user-policy \
  --user-name github-amplify-cicd \
  --policy-name AmplifyDeployPolicy \
  --policy-document file://docs/amplify-cicd-policy.json
```

---

## 🛠️ Scripts de Automatización

### [../scripts/setup-amplify.sh](../scripts/setup-amplify.sh)

Script interactivo para configurar AWS Amplify CI/CD.

```bash
# Ejecuta:
./scripts/setup-amplify.sh
```

**Hace automáticamente**:

1. ✅ Crea usuario IAM
2. ✅ Asigna política
3. ✅ Genera access keys
4. ✅ Configura GitHub secrets (opcional)

### [../scripts/setup-github-environments.sh](../scripts/setup-github-environments.sh)

Script interactivo para configurar GitHub Environments (staging/production).

```bash
# Ejecuta:
./scripts/setup-github-environments.sh
```

**Hace automáticamente**:

1. ✅ Crea environments en GitHub
2. ✅ Configura secrets por ambiente
3. ✅ Configura variables por ambiente
4. ✅ Verifica configuración AWS

---

## 📖 Índice por Tarea

### "Quiero generar tipos de GraphQL"

1. Copia `.env.example` a `.env` en el root
2. Agrega `GRAPHQL_ENDPOINT=http://localhost:4000/graphql`
3. Ejecutar `pnpm graphql:codegen`
4. Ver [DEVELOPMENT.md#graphql](./DEVELOPMENT.md#graphql) para más info

### "Quiero configurar CI/CD desde cero"

1. [AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md) - Guía completa
2. Ejecutar `./scripts/setup-amplify.sh`
3. Seguir checklist al final de AMPLIFY_SETUP.md

### "Quiero entender el deploy selectivo"

1. [SELECTIVE_DEPLOYMENT.md](./SELECTIVE_DEPLOYMENT.md)
2. Ver sección "Escenarios Reales"

### "¿Cómo configuro staging y production?"

1. [ENVIRONMENTS.md](./ENVIRONMENTS.md)
2. Ejecutar `./scripts/setup-github-environments.sh`
3. Push a `develop` → Staging, Push a `main` → Production

### "¿Debo usar Docker?"

1. [DOCKER_VS_NATIVE.md](./DOCKER_VS_NATIVE.md)
2. **Spoiler**: No, para tu caso Native es mejor

### "¿Qué hosting es más barato?"

1. [HOSTING_COMPARISON.md](./HOSTING_COMPARISON.md)
2. **TL;DR**: S3 + CloudFront ($12/mes) vs Amplify ($15/mes) vs DigitalOcean ($7-10/mes)

### "Quiero migrar a S3 para ahorrar costos"

1. [S3_CLOUDFRONT_SETUP.md](./S3_CLOUDFRONT_SETUP.md)
2. Seguir pasos de configuración
3. **Ahorro**: $36/año

### "Tengo un error en el build"

1. [AMPLIFY_SETUP.md#troubleshooting](./AMPLIFY_SETUP.md#troubleshooting)
2. Busca tu error específico

### "Quiero añadir una tercera app"

1. Crear carpeta en `apps/nueva-app/`
2. Añadir `amplify.yml` en la nueva app
3. Crear workflow `.github/workflows/amplify-nueva-app.yml`
4. Configurar en Amplify Console
5. Leer [SELECTIVE_DEPLOYMENT.md](./SELECTIVE_DEPLOYMENT.md) para paths

---

## 🏗️ Estructura de Archivos Creados

```
frontend-lq/
├── .github/
│   └── workflows/
│       ├── amplify-student-teacher.yml   # CI/CD Student-Teacher
│       └── amplify-institutional.yml     # CI/CD Institutional
├── apps/
│   ├── student-teacher/
│   │   └── amplify.yml                   # Config Amplify
│   └── institutional/
│       └── amplify.yml                   # Config Amplify
├── docs/
│   ├── README.md                         # Este archivo
│   ├── AMPLIFY_SETUP.md                  # Guía principal
│   ├── SELECTIVE_DEPLOYMENT.md           # Deploy selectivo
│   ├── ENVIRONMENTS.md                   # Staging y Production
│   ├── DOCKER_VS_NATIVE.md               # Docker vs Native
│   ├── HOSTING_COMPARISON.md             # Comparación de hosting
│   ├── S3_CLOUDFRONT_SETUP.md            # Setup S3 + CloudFront
│   └── amplify-cicd-policy.json          # Política IAM
└── scripts/
    ├── setup-amplify.sh                  # Setup AWS Amplify
    └── setup-github-environments.sh      # Setup Environments
```

---

## 🎯 Quick Start

### Setup completo en 5 pasos:

```bash
# 1. Ejecuta el script de setup
./scripts/setup-amplify.sh

# 2. Crea las apps en Amplify Console
# → https://console.aws.amazon.com/amplify/

# 3. Configura variables de entorno en cada app
# → Ver AMPLIFY_SETUP.md#variables-de-entorno

# 4. Haz un test deploy
git checkout -b test/amplify-setup
git push origin test/amplify-setup

# 5. Verifica en GitHub Actions
gh run list
```

---

## 📞 Soporte

### Problemas comunes:

- Ver [AMPLIFY_SETUP.md#troubleshooting](./AMPLIFY_SETUP.md#troubleshooting)

### GitHub Actions no se dispara:

- Revisa los `paths:` en los workflows
- Ver [SELECTIVE_DEPLOYMENT.md](./SELECTIVE_DEPLOYMENT.md)

### Build falla en Amplify:

- Revisa los logs en Amplify Console
- Verifica que `amplify.yml` esté correcto

### ¿Usar Docker?:

- Ver [DOCKER_VS_NATIVE.md](./DOCKER_VS_NATIVE.md)
- **TL;DR**: No lo necesitas

### ¿Qué hosting usar?:

- Ver [HOSTING_COMPARISON.md](./HOSTING_COMPARISON.md)
- **TL;DR**: S3 más barato ($12/mes), Amplify más fácil ($15/mes), DO más predecible ($10/mes)

---

## 🔄 Actualizaciones

Este documento y los relacionados se actualizarán cuando:

- ✅ Se agregue una nueva app al monorepo
- ✅ Cambien las configuraciones de Amplify
- ✅ Haya nuevos problemas comunes (troubleshooting)

---

## 📊 Resumen de Decisiones Técnicas

### ✅ Decisiones tomadas:

| Decisión             | Alternativa  | Razón                                                 |
| -------------------- | ------------ | ----------------------------------------------------- |
| **Native Build**     | Docker       | Más rápido, más barato, suficiente para nuestro stack |
| **Monorepo**         | Multi-repo   | Código compartido, deploy atómico                     |
| **Deploy selectivo** | Deploy todo  | Ahorra tiempo y dinero (40% menos builds)             |
| **GitHub Actions**   | Amplify solo | Mayor control, CI/CD completo con lint/test           |
| **pnpm**             | npm/yarn     | Más rápido, mejor para monorepos                      |
| **Turbo**            | Lerna/Nx     | Simple, cache inteligente                             |

### 📈 Métricas esperadas:

```
Build time: 3-5 min por app
Deploy frequency: ~20-30 deploys/semana
Success rate: > 95%
Cost: ~$15-20/mes (ambas apps)
```

---

## 🎓 Aprendizajes del Monorepo

### Ventajas comprobadas:

✅ Un cambio en `@lq/ui` actualiza ambas apps ✅ No hay desincronización de versiones ✅ DRY (Don't Repeat Yourself) en
componentes ✅ Un PR puede tocar múltiples apps

### Desventajas conocidas:

⚠️ Builds iniciales más lentos (primera vez) ⚠️ Configuración inicial más compleja ⚠️ Debes pensar en breaking changes

### Balance final:

Para LingoQuesto con 2+ apps que comparten código: **Monorepo es la mejor opción**.

---

Última actualización: 2025-11-21
