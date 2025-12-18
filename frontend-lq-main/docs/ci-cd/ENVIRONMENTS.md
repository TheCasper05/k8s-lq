# Guía de Manejo de Ambientes (Staging y Producción)

## 🎯 Arquitectura de Ambientes

### Estrategia de Branches → Environments

```
git branch          AWS Amplify Branch      Environment       URL
─────────────────────────────────────────────────────────────────────
main           →    main                →   Production    →   app.lingoquest.com
develop        →    develop             →   Staging/QA    →   staging.lingoquest.com
feature/*      →    (preview)           →   Preview       →   pr-123.lingoquest.com
```

### Variables de Entorno por Ambiente

```
Production (main):
  GRAPHQL_ENDPOINT=https://api.lingoquest.com/graphql
  SENTRY_ENVIRONMENT=production
  NODE_ENV=production

Staging (develop):
  GRAPHQL_ENDPOINT=https://api-staging.lingoquest.com/graphql
  SENTRY_ENVIRONMENT=staging
  NODE_ENV=production

Preview (PR):
  GRAPHQL_ENDPOINT=https://api-staging.lingoquest.com/graphql
  SENTRY_ENVIRONMENT=preview
  NODE_ENV=production
```

---

## 🏗️ Configuración en AWS Amplify

### Paso 1: Crear Branch en Amplify (Staging)

Para cada app (student-teacher e institutional):

1. Ve a [Amplify Console](https://console.aws.amazon.com/amplify/)
2. Selecciona tu app
3. Click en **"Connect branch"**
4. Selecciona branch: `develop`
5. Configura build settings (usa el mismo `amplify.yml`)

**Resultado**:

```
App: lingoquest-student-teacher
├── Branch: main (production)
│   └── URL: https://main.d1234abcd.amplifyapp.com
└── Branch: develop (staging)
    └── URL: https://develop.d1234abcd.amplifyapp.com
```

### Paso 2: Configurar Variables de Entorno por Branch

#### En Amplify Console:

**App settings > Environment variables > Manage variables**

```yaml
# Variables compartidas (todas las branches)
NODE_ENV: production
SENTRY_DSN: https://...@sentry.io/123456

# Variables específicas por branch
Branch: main
  GRAPHQL_ENDPOINT: https://api.lingoquest.com/graphql
  SENTRY_ENVIRONMENT: production
  NUXT_PUBLIC_API_URL: https://api.lingoquest.com

Branch: develop
  GRAPHQL_ENDPOINT: https://api-staging.lingoquest.com/graphql
  SENTRY_ENVIRONMENT: staging
  NUXT_PUBLIC_API_URL: https://api-staging.lingoquest.com
```

**Configuración visual**:

```
┌─────────────────────────────────────────────────┐
│ Environment variable    │ Value    │ Branches   │
├─────────────────────────────────────────────────┤
│ NODE_ENV                │ prod...  │ All        │
│ GRAPHQL_ENDPOINT        │ https... │ main       │
│ GRAPHQL_ENDPOINT        │ https... │ develop    │
│ SENTRY_ENVIRONMENT      │ prod...  │ main       │
│ SENTRY_ENVIRONMENT      │ staging  │ develop    │
└─────────────────────────────────────────────────┘
```

---

## 🔧 GitHub Actions con Environments

### Opción 1: GitHub Environments (Recomendado)

GitHub Actions tiene un feature de "Environments" que permite:

- ✅ Variables/secrets específicos por environment
- ✅ Protection rules (ej: require approval para production)
- ✅ Deployment history
- ✅ Rollback fácil

#### Configurar GitHub Environments:

1. Ve a **Settings > Environments**
2. Crea dos environments:
   - `staging`
   - `production`

**Environment: production**:

```yaml
Protection rules:
  ✅ Required reviewers: 1 (opcional)
  ✅ Wait timer: 0 minutes
  ✅ Deployment branches: Only main

Environment secrets:
  AMPLIFY_APP_ID_STUDENT_TEACHER: d1234production
  AMPLIFY_APP_ID_INSTITUTIONAL: d5678production
  GRAPHQL_ENDPOINT: https://api.lingoquest.com/graphql
```

**Environment: staging**:

```yaml
Protection rules: (ninguno - deploy automático)

Deployment branches: Only develop

Environment secrets:
  AMPLIFY_APP_ID_STUDENT_TEACHER: d1234staging
  AMPLIFY_APP_ID_INSTITUTIONAL: d5678staging
  GRAPHQL_ENDPOINT: https://api-staging.lingoquest.com/graphql
```

---

## 📝 Workflows Actualizados

### .github/workflows/amplify-student-teacher.yml (CON ENVIRONMENTS)

```yaml
name: Deploy Student-Teacher to Amplify

on:
  push:
    branches:
      - main # Production
      - develop # Staging
    paths:
      - "apps/student-teacher/**"
      - "packages/**"
      - "pnpm-lock.yaml"
      - "turbo.json"
      - "package.json"
  pull_request:
    branches:
      - main
      - develop
    paths:
      - "apps/student-teacher/**"
      - "packages/**"
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to deploy to"
        required: true
        type: choice
        options:
          - staging
          - production

env:
  NODE_VERSION: "24.11.1"
  PNPM_VERSION: "10.15.1"

jobs:
  # Job 1: Determine environment
  setup:
    name: Determine Environment
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
      branch: ${{ steps.set-env.outputs.branch }}
    steps:
      - name: Set environment based on branch
        id: set-env
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ inputs.environment }}" >> $GITHUB_OUTPUT
            if [[ "${{ inputs.environment }}" == "production" ]]; then
              echo "branch=main" >> $GITHUB_OUTPUT
            else
              echo "branch=develop" >> $GITHUB_OUTPUT
            fi
          elif [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
            echo "branch=main" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "branch=develop" >> $GITHUB_OUTPUT
          else
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "branch=develop" >> $GITHUB_OUTPUT
          fi

  # Job 2: Build and Deploy
  deploy:
    name: Build and Deploy Student-Teacher
    runs-on: ubuntu-latest
    needs: setup
    # Usa el environment de GitHub
    environment:
      name: ${{ needs.setup.outputs.environment }}
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
          run_install: false

      - name: Get pnpm store directory
        id: pnpm-cache
        shell: bash
        run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

      - name: Setup pnpm cache
        uses: actions/cache@v4
        with:
          path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pnpm-store-

      - name: Setup Turbo cache
        uses: actions/cache@v4
        with:
          path: .turbo
          key: ${{ runner.os }}-turbo-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-turbo-

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run linter
        run: pnpm --filter @lq/student-teacher lint

      - name: Run type check
        run: pnpm --filter @lq/student-teacher typecheck

      - name: Build application
        run: pnpm build:student-teacher
        env:
          NODE_ENV: production
          # Estas variables vienen del GitHub Environment
          NUXT_PUBLIC_API_URL: ${{ vars.NUXT_PUBLIC_API_URL }}
          GRAPHQL_ENDPOINT: ${{ vars.GRAPHQL_ENDPOINT }}
          SENTRY_ENVIRONMENT: ${{ needs.setup.outputs.environment }}

      - name: Configure AWS Credentials
        if: github.event_name == 'push'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Trigger Amplify deployment
        if: github.event_name == 'push'
        id: deploy
        run: |
          # Obtener el APP_ID correcto según el environment
          if [[ "${{ needs.setup.outputs.environment }}" == "production" ]]; then
            APP_ID="${{ secrets.AMPLIFY_APP_ID_STUDENT_TEACHER_PROD }}"
          else
            APP_ID="${{ secrets.AMPLIFY_APP_ID_STUDENT_TEACHER_STAGING }}"
          fi

          # Disparar deployment
          JOB_ID=$(aws amplify start-job \
            --app-id "$APP_ID" \
            --branch-name ${{ needs.setup.outputs.branch }} \
            --job-type RELEASE \
            --query 'jobSummary.jobId' \
            --output text)

          echo "Job ID: $JOB_ID"
          echo "job_id=$JOB_ID" >> $GITHUB_OUTPUT

          # Obtener URL de la app
          APP_URL=$(aws amplify get-branch \
            --app-id "$APP_ID" \
            --branch-name ${{ needs.setup.outputs.branch }} \
            --query 'branch.defaultDomain' \
            --output text)

          echo "url=https://$APP_URL" >> $GITHUB_OUTPUT

      - name: Deployment Summary
        if: github.event_name == 'push'
        run: |
          echo "✅ Deployed to ${{ needs.setup.outputs.environment }}"
          echo "🌐 URL: ${{ steps.deploy.outputs.url }}"
          echo "🆔 Job ID: ${{ steps.deploy.outputs.job_id }}"
          echo "🌿 Branch: ${{ needs.setup.outputs.branch }}"
```

### .github/workflows/amplify-institutional.yml

```yaml
# Similar a student-teacher, pero para institutional
name: Deploy Institutional to Amplify

on:
  push:
    branches:
      - main
      - develop
    paths:
      - "apps/institutional/**"
      - "packages/**"
      - "pnpm-lock.yaml"
      - "turbo.json"
      - "package.json"
  pull_request:
    branches:
      - main
      - develop
    paths:
      - "apps/institutional/**"
      - "packages/**"
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to deploy to"
        required: true
        type: choice
        options:
          - staging
          - production

env:
  NODE_VERSION: "24.11.1"
  PNPM_VERSION: "10.15.1"

jobs:
  setup:
    name: Determine Environment
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
      branch: ${{ steps.set-env.outputs.branch }}
    steps:
      - name: Set environment based on branch
        id: set-env
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ inputs.environment }}" >> $GITHUB_OUTPUT
            if [[ "${{ inputs.environment }}" == "production" ]]; then
              echo "branch=main" >> $GITHUB_OUTPUT
            else
              echo "branch=develop" >> $GITHUB_OUTPUT
            fi
          elif [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
            echo "branch=main" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "branch=develop" >> $GITHUB_OUTPUT
          fi

  deploy:
    name: Build and Deploy Institutional
    runs-on: ubuntu-latest
    needs: setup
    environment:
      name: ${{ needs.setup.outputs.environment }}
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
          run_install: false

      - name: Get pnpm store directory
        id: pnpm-cache
        shell: bash
        run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

      - name: Setup pnpm cache
        uses: actions/cache@v4
        with:
          path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pnpm-store-

      - name: Setup Turbo cache
        uses: actions/cache@v4
        with:
          path: .turbo
          key: ${{ runner.os }}-turbo-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-turbo-

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run linter
        run: pnpm --filter @lq/institutional lint

      - name: Run type check
        run: pnpm --filter @lq/institutional typecheck

      - name: Build application
        run: pnpm build:institutional
        env:
          NODE_ENV: production
          VITE_API_URL: ${{ vars.VITE_API_URL }}
          GRAPHQL_ENDPOINT: ${{ vars.GRAPHQL_ENDPOINT }}
          SENTRY_ENVIRONMENT: ${{ needs.setup.outputs.environment }}

      - name: Configure AWS Credentials
        if: github.event_name == 'push'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Trigger Amplify deployment
        if: github.event_name == 'push'
        id: deploy
        run: |
          if [[ "${{ needs.setup.outputs.environment }}" == "production" ]]; then
            APP_ID="${{ secrets.AMPLIFY_APP_ID_INSTITUTIONAL_PROD }}"
          else
            APP_ID="${{ secrets.AMPLIFY_APP_ID_INSTITUTIONAL_STAGING }}"
          fi

          JOB_ID=$(aws amplify start-job \
            --app-id "$APP_ID" \
            --branch-name ${{ needs.setup.outputs.branch }} \
            --job-type RELEASE \
            --query 'jobSummary.jobId' \
            --output text)

          echo "job_id=$JOB_ID" >> $GITHUB_OUTPUT

          APP_URL=$(aws amplify get-branch \
            --app-id "$APP_ID" \
            --branch-name ${{ needs.setup.outputs.branch }} \
            --query 'branch.defaultDomain' \
            --output text)

          echo "url=https://$APP_URL" >> $GITHUB_OUTPUT

      - name: Deployment Summary
        if: github.event_name == 'push'
        run: |
          echo "✅ Deployed to ${{ needs.setup.outputs.environment }}"
          echo "🌐 URL: ${{ steps.deploy.outputs.url }}"
```

---

## 🔑 GitHub Secrets y Variables

### Secrets (Settings > Secrets > Actions)

```bash
# Compartidos (Repository secrets)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Por environment
# Environment: production
AMPLIFY_APP_ID_STUDENT_TEACHER_PROD=d1234prod
AMPLIFY_APP_ID_INSTITUTIONAL_PROD=d5678prod

# Environment: staging
AMPLIFY_APP_ID_STUDENT_TEACHER_STAGING=d1234staging
AMPLIFY_APP_ID_INSTITUTIONAL_STAGING=d5678staging
```

### Variables (Settings > Secrets > Variables)

```bash
# Environment: production
NUXT_PUBLIC_API_URL=https://api.lingoquest.com
VITE_API_URL=https://api.lingoquest.com
GRAPHQL_ENDPOINT=https://api.lingoquest.com/graphql

# Environment: staging
NUXT_PUBLIC_API_URL=https://api-staging.lingoquest.com
VITE_API_URL=https://api-staging.lingoquest.com
GRAPHQL_ENDPOINT=https://api-staging.lingoquest.com/graphql
```

---

## 🚀 Flujo de Trabajo

### Escenario 1: Feature Development

```bash
# 1. Crear feature branch
git checkout -b feature/new-quiz

# 2. Hacer cambios
git commit -m "feat: add new quiz"

# 3. Push y crear PR a develop
git push origin feature/new-quiz
gh pr create --base develop

# 4. GitHub Actions corre tests (pero NO deploya)
# ✅ Lint, typecheck pasan

# 5. Merge a develop
gh pr merge

# 6. Automáticamente deploya a STAGING
# → https://develop.d1234.amplifyapp.com
```

### Escenario 2: Release to Production

```bash
# 1. Crear PR de develop → main
gh pr create --base main --head develop --title "Release v1.2.0"

# 2. Review y approval (si está configurado)

# 3. Merge a main
gh pr merge

# 4. Automáticamente deploya a PRODUCTION
# → https://main.d1234.amplifyapp.com
# → https://app.lingoquest.com (si tienes DNS)
```

### Escenario 3: Hotfix en Production

```bash
# 1. Crear hotfix branch desde main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix
git commit -m "fix: critical bug"

# 3. PR a main
gh pr create --base main

# 4. Merge y deploy directo a production
```

### Escenario 4: Deploy Manual

```bash
# Desde GitHub UI:
# Actions > Deploy Student-Teacher > Run workflow
# Selecciona: staging o production

# Desde CLI:
gh workflow run amplify-student-teacher.yml \
  -f environment=staging

gh workflow run amplify-student-teacher.yml \
  -f environment=production
```

---

## 📊 Visualización de Deployments

En GitHub:

```
Repository > Deployments

┌──────────────────────────────────────────────┐
│ Environment: production                      │
│ ✅ main@abc123 - 2 hours ago                 │
│ ✅ main@def456 - 1 day ago                   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ Environment: staging                         │
│ ✅ develop@xyz789 - 30 minutes ago           │
│ ✅ develop@qrs012 - 3 hours ago              │
└──────────────────────────────────────────────┘
```

---

## ✅ Checklist de Setup

### 1. Amplify Console

- [ ] Branch `main` conectada (production)
- [ ] Branch `develop` conectada (staging)
- [ ] Variables de entorno configuradas por branch
- [ ] DNS configurado (opcional)
  - [ ] app.lingoquest.com → main
  - [ ] staging.lingoquest.com → develop

### 2. GitHub Environments

- [ ] Environment `production` creado
  - [ ] Protection rules configuradas (opcional)
  - [ ] Secrets añadidos (APP_IDs)
  - [ ] Variables añadidas (API URLs)
- [ ] Environment `staging` creado
  - [ ] Secrets añadidos
  - [ ] Variables añadidas

### 3. GitHub Secrets

- [ ] `AWS_ACCESS_KEY_ID` (repository secret)
- [ ] `AWS_SECRET_ACCESS_KEY` (repository secret)
- [ ] `AMPLIFY_APP_ID_STUDENT_TEACHER_PROD` (production secret)
- [ ] `AMPLIFY_APP_ID_STUDENT_TEACHER_STAGING` (staging secret)
- [ ] `AMPLIFY_APP_ID_INSTITUTIONAL_PROD` (production secret)
- [ ] `AMPLIFY_APP_ID_INSTITUTIONAL_STAGING` (staging secret)

### 4. Branch Protection

- [ ] `main` branch protegido
  - [ ] Require PR reviews
  - [ ] Require status checks (CI)
  - [ ] No force push
- [ ] `develop` branch (opcional)
  - [ ] Require status checks

---

## 🐛 Troubleshooting

### Problema: Variables de entorno no se cargan

**Solución**: Verifica que uses `vars.*` para variables y `secrets.*` para secrets:

```yaml
# ✅ Correcto
VITE_API_URL: ${{ vars.VITE_API_URL }}
AWS_SECRET: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

# ❌ Incorrecto
VITE_API_URL: ${{ secrets.VITE_API_URL }}  # Las variables NO son secrets
```

### Problema: Deploy se dispara en branch equivocada

**Solución**: Verifica los `on.push.branches` en el workflow:

```yaml
on:
  push:
    branches:
      - main # Solo main
      - develop # Solo develop
    # NO uses - '**' (dispara en todas)
```

### Problema: Environment protection rules no funcionan

**Solución**: Asegúrate de que el workflow use `environment:`:

```yaml
jobs:
  deploy:
    environment:
      name: production # ← Esto activa las protection rules
```

---

## 📚 Recursos

- [GitHub Environments Docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Amplify Multi-environment](https://docs.aws.amazon.com/amplify/latest/userguide/multi-environments.html)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🎯 Resumen

**Setup básico** (solo staging por ahora):

```
1. Conecta branch develop en Amplify
2. Crea environment staging en GitHub
3. Añade secrets/variables
4. Push a develop → deploya a staging ✅
```

**Cuando quieras production**:

```
1. Conecta branch main en Amplify
2. Crea environment production en GitHub
3. Añade secrets/variables
4. Push a main → deploya a production ✅
```

**Ventajas**:

- ✅ Deploy automático por branch
- ✅ Variables diferentes por ambiente
- ✅ Protection rules en production
- ✅ History de deployments
- ✅ Rollback fácil
