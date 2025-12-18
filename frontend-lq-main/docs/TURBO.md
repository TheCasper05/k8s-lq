# Guia de Turborepo

## indice

1. [Introducción](#introducción)
2. [Conceptos Básicos](#conceptos-básicos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Gestión de Dependencias](#gestión-de-dependencias)
5. [Comandos Principales](#comandos-principales)
6. [Sistema de Filtros](#sistema-de-filtros)
7. [Configuración de Tareas](#configuración-de-tareas)
8. [Sistema de Caché](#sistema-de-caché)
9. [Dependencias entre Tareas](#dependencias-entre-tareas)
10. [Mejores Prácticas](#mejores-prácticas)
11. [Troubleshooting](#troubleshooting)

## Introducción

Turborepo es una herramienta de build system de alto rendimiento para monorepos de JavaScript y TypeScript. En
LingoQuesto, usamos Turborepo para:

- Ejecutar tareas en paralelo en múltiples paquetes
- Cachear resultados de builds para evitar trabajo redundante
- Gestionar dependencias entre paquetes
- Optimizar tiempos de CI/CD

## Conceptos Básicos

### ¿Qué es un Monorepo?

Un monorepo es un repositorio que contiene múltiples proyectos relacionados. Nuestro monorepo incluye:

- **Apps**: Aplicaciones independientes (`student-teacher`, `institutional`)
- **Packages**: Código compartido (`@lq/ui`, `@lq/graphql`, `@lq/stores`, `@lq/utils`)

### ¿Cómo Funciona Turborepo?

Turborepo:

1. Lee la configuración de `turbo.json`
2. Analiza el grafo de dependencias entre paquetes
3. Determina qué tareas ejecutar y en qué orden
4. Ejecuta tareas en paralelo cuando es posible
5. Cachea los resultados para futuras ejecuciones

## Estructura del Proyecto

```
frontend-lq/
   apps/                     # Aplicaciones
      student-teacher/
      institutional/
   packages/                # Paquetes compartidos
      ui/
      graphql/
      stores/
      utils/
  package.json             # Root package.json
  pnpm-workspace.yaml     # Configuración de workspace
  turbo.json              # Configuración de Turborepo
```

## Gestión de Dependencias

En un monorepo con Turborepo y pnpm, la gestión de dependencias es crucial para mantener la coherencia y evitar
problemas.

### Agregar Dependencias al Paquete Principal (Root)

Las dependencias en el root se usan para herramientas de desarrollo compartidas (eslint, typescript, turbo, etc.).

```bash
# Agregar dependencia de desarrollo al root
pnpm add -D -w <paquete>

# Ejemplos:
pnpm add -D -w eslint
pnpm add -D -w typescript
pnpm add -D -w prettier

# -D: devDependency
# -w: workspace root (necesario para agregar al root)
```

**Nota**: El flag `-w` es necesario para indicar que quieres instalar en el workspace root.

### Agregar Dependencias a un Paquete Específico

Para agregar dependencias a un paquete o app específica:

```bash
# Sintaxis general
pnpm add <paquete> --filter=<nombre-paquete>

# Ejemplos para apps:
pnpm add vue --filter=@lq/student-teacher
pnpm add axios --filter=@lq/institutional
pnpm add -D vitest --filter=@lq/student-teacher

# Ejemplos para packages:
pnpm add zod --filter=@lq/ui
pnpm add graphql --filter=@lq/graphql
pnpm add -D @types/node --filter=@lq/utils
```

### Agregar Dependencias Locales (Workspace)

Para que una app use un paquete local del monorepo:

```bash
# Agregar paquete local como dependencia
pnpm add @lq/ui --filter=@lq/student-teacher --workspace

# O manualmente en package.json:
{
  "dependencies": {
    "@lq/ui": "workspace:*"
  }
}
```

**Nota**: El protocolo `workspace:*` es específico de pnpm y asegura que siempre use la versión local.

### Tipos de Dependencias

#### 1. dependencies

Para paquetes necesarios en producción:

```bash
pnpm add vue --filter=@lq/student-teacher
pnpm add axios --filter=@lq/institutional
```

#### 2. devDependencies

Para herramientas de desarrollo (no se incluyen en producción):

```bash
pnpm add -D vitest --filter=@lq/student-teacher
pnpm add -D @types/node --filter=@lq/ui
pnpm add -D eslint --filter=@lq/utils
```

#### 3. peerDependencies

Para paquetes compartidos que la app host debe proveer:

```json
// En packages/ui/package.json
{
  "peerDependencies": {
    "vue": "^3.4.0"
  }
}
```

### Comandos Útiles

```bash
# Ver todas las dependencias de un paquete
pnpm list --filter=@lq/student-teacher

# Ver dependencias de todo el workspace
pnpm list -r

# Ver por qué un paquete está instalado
pnpm why <paquete> --filter=@lq/student-teacher

# Actualizar dependencias
pnpm update --filter=@lq/student-teacher

# Actualizar dependencias de todo el workspace
pnpm update -r

# Remover dependencia
pnpm remove <paquete> --filter=@lq/student-teacher

# Verificar dependencias desactualizadas
pnpm outdated --filter=@lq/student-teacher
```

### Mejores Prácticas para Dependencias

#### 1. Evita Duplicación

Si múltiples paquetes necesitan la misma dependencia, considera:

```bash
# Opción A: Instalar en root si es herramienta de dev
pnpm add -D -w typescript

# Opción B: Crear un paquete compartido
# packages/shared-config/package.json
```

#### 2. Versiones Consistentes

Mantén versiones consistentes en todo el monorepo:

```bash
# Ver versiones de una dependencia en todo el workspace
pnpm list vue -r

# Si hay inconsistencias, actualiza:
pnpm add vue@3.4.0 --filter=@lq/student-teacher
pnpm add vue@3.4.0 --filter=@lq/institutional
```

#### 3. Usa workspace:\* para Paquetes Locales

Siempre usa `workspace:*` para dependencias internas:

```json
{
  "dependencies": {
    "@lq/ui": "workspace:*",
    "@lq/utils": "workspace:*"
  }
}
```

#### 4. Instala Tipos de TypeScript

Si usas TypeScript, instala los tipos correspondientes:

```bash
# Junto con el paquete
pnpm add axios --filter=@lq/student-teacher
pnpm add -D @types/axios --filter=@lq/student-teacher
```

### Ejemplo Completo: Agregar Nueva Dependencia

```bash
# 1. Agregar pinia a student-teacher
pnpm add pinia --filter=@lq/student-teacher

# 2. Si necesita tipos
pnpm add -D @pinia/nuxt --filter=@lq/student-teacher

# 3. Verificar que se instaló correctamente
pnpm list pinia --filter=@lq/student-teacher

# 4. Si otros paquetes también lo necesitan
pnpm add pinia --filter=@lq/institutional

# 5. (Opcional) Si es una dependencia compartida, considerar moverla a @lq/stores
```

### Troubleshooting de Dependencias

#### Problema: "ERR_PNPM_ADDING_TO_ROOT"

**Solución**: Usa el flag `-w` para agregar al root:

```bash
pnpm add -D -w <paquete>
```

#### Problema: Dependencia no se encuentra

**Solución**: Reinstala las dependencias:

```bash
# Limpiar y reinstalar todo
pnpm clean:install

# O solo reinstalar
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

#### Problema: Versiones conflictivas

**Solución**: Usa `pnpm list` para identificar y resolver:

```bash
pnpm list <paquete> -r
# Actualiza a la versión deseada en cada paquete
```

#### Problema: Workspace dependency no se actualiza

**Solución**: Fuerza la reinstalación:

```bash
# Rebuild el paquete dependiente
turbo run build --filter=@lq/ui --force

# Luego rebuild lo que depende de él
turbo run build --filter=@lq/student-teacher... --force
```

## Comandos Principales

### Desarrollo

```bash
# Ejecutar dev en todas las apps
pnpm dev

# Ejecutar dev en una app especifica
pnpm dev:student-teacher
pnpm dev:institutional

# Ejecutar dev con Turbo directamente
turbo run dev
turbo run dev --filter=@lq/student-teacher
```

### Build

```bash
# Build de todas las apps
pnpm build

# Build de una app especifica
pnpm build:student-teacher
pnpm build:institutional

# Build con Turbo
turbo run build
turbo run build --filter=@lq/institutional
```

### Testing

```bash
# Ejecutar todos los tests
pnpm test

# Tests unitarios
pnpm test:unit

# Tests E2E
pnpm test:e2e

# Con Turbo
turbo run test
turbo run test:unit
```

### Linting y Formateo

```bash
# Lint
pnpm lint
turbo run lint

# Lint con fix
pnpm lint:fix
turbo run lint:fix

# Format
pnpm format
turbo run format

# Typecheck
pnpm typecheck
turbo run typecheck
```

## Sistema de Filtros

Los filtros permiten ejecutar tareas en paquetes especificos.

### Filtros Básicos

```bash
# Por nombre de paquete
turbo run build --filter=@lq/ui

# Múltiples paquetes
turbo run build --filter=@lq/ui --filter=@lq/graphql

# Todas las apps
turbo run dev --filter="./apps/**"

# Todos los packages
turbo run build --filter="./packages/**"
```

### Filtros Avanzados

```bash
# Paquete y sus dependencias
turbo run build --filter=@lq/student-teacher...

# Dependencias de un paquete (sin incluir el paquete)
turbo run build --filter=...@lq/student-teacher

# Paquetes afectados desde un commit
turbo run test --filter=[HEAD^1]

# Paquetes en un directorio especifico
turbo run build --filter="./apps/*"
```

### Ejemplos Prácticos

```bash
# Build solo la app student-teacher y sus dependencias
turbo run build --filter=@lq/student-teacher...

# Test solo los paquetes que cambiaron
turbo run test --filter=[main]

# Lint todas las apps pero no los packages
turbo run lint --filter="./apps/**"
```

## Configuración de Tareas

Nuestro `turbo.json` define las siguientes tareas:

### Tarea: build

```json
{
  "build": {
    "dependsOn": ["^build"],
    "outputs": [".nuxt/**", ".output/**", "dist/**"],
    "env": ["NODE_ENV"]
  }
}
```

- `dependsOn: ["^build"]`: Primero buildea las dependencias
- `outputs`: Archivos que se cachean
- `env`: Variables de entorno que invalidan el caché

### Tarea: dev

```json
{
  "dev": {
    "cache": false,
    "persistent": true
  }
}
```

- `cache: false`: No cachea (dev es siempre fresh)
- `persistent: true`: Proceso que se mantiene corriendo

### Tarea: lint

```json
{
  "lint": {
    "dependsOn": ["^build"],
    "outputs": []
  }
}
```

- `dependsOn: ["^build"]`: Requiere que las dependencias estén buildeadas
- `outputs: []`: No produce archivos para cachear

### Añadir Nueva Tarea

Para añadir una nueva tarea al pipeline:

1. Añadir en `turbo.json`:

```json
{
  "tasks": {
    "nueva-tarea": {
      "dependsOn": ["^build"],
      "outputs": ["output-folder/**"],
      "cache": true
    }
  }
}
```

2. Añadir el script en los `package.json` de apps/packages:

```json
{
  "scripts": {
    "nueva-tarea": "comando-aqui"
  }
}
```

3. (Opcional) Añadir script en el root `package.json`:

```json
{
  "scripts": {
    "nueva-tarea": "turbo run nueva-tarea"
  }
}
```

## Sistema de Caché

### Cómo Funciona el Caché

Turborepo cachea los resultados de las tareas basado en:

1. **Inputs**: Código fuente, configuración, dependencias
2. **Outputs**: Archivos generados (definidos en `turbo.json`)
3. **Environment**: Variables de entorno especificadas

Si nada cambia, Turbo reutiliza el resultado cacheado.

### Ver el Estado del Caché

```bash
# Ejecutar con verbose para ver hits/misses
turbo run build --filter=@lq/ui --verbosity=2

# Ver estadisticas
turbo run build --summarize
```

### Limpiar el Caché

```bash
# Limpiar caché de Turbo
rm -rf .turbo

# Forzar rebuild sin usar caché
turbo run build --force

# Limpiar todo y reinstalar
pnpm clean:install
```

### Caché Remoto (Opcional)

Para compartir caché entre el equipo:

```bash
# Login a Vercel (provee caché remoto gratis)
turbo login

# Link el proyecto
turbo link

# Ahora el caché se comparte automáticamente
turbo run build
```

## Dependencias entre Tareas

### Simbolos de Dependencias

- `^`: Dependencias topológicas (upstream dependencies)
- Sin simbolo: Dependencias dentro del mismo paquete

### Ejemplos

```json
{
  "typecheck": {
    "dependsOn": ["^build"] // Buildea deps primero, luego typecheck
  },
  "deploy": {
    "dependsOn": ["build", "test"] // Build y test en el mismo paquete primero
  }
}
```

### Orden de Ejecución

Para `turbo run build --filter=@lq/student-teacher`:

1. Build `@lq/ui`
2. Build `@lq/graphql`
3. Build `@lq/stores`
4. Build `@lq/utils`
5. Build `@lq/student-teacher` (usa las deps buildeadas)

Turbo ejecuta los pasos 1-4 en paralelo si es posible.

## Mejores Prácticas

### 1. Usa Filtros para Desarrollo

```bash
# En vez de ejecutar todo
turbo run dev

# Ejecuta solo lo que necesitas
turbo run dev --filter=@lq/student-teacher
```

### 2. Aprovecha el Caché

```bash
# Primera vez: ejecuta todo
turbo run build  # ~2 minutos

# Sin cambios: instantáneo
turbo run build  # ~100ms (cached)

# Solo rebuilds lo que cambió
# (editas @lq/ui)
turbo run build  # Solo rebuilds apps que usan @lq/ui
```

### 3. Define Outputs Correctamente

```json
{
  "build": {
    "outputs": [
      ".nuxt/**", // Nuxt output
      ".output/**", // Nuxt production
      "dist/**" // Vite output
    ]
  }
}
```

### 4. Usa --dry-run para Probar

```bash
# Ver qué haria Turbo sin ejecutarlo
turbo run build --dry-run

# Ver qué paquetes se afectarian
turbo run test --filter=[main] --dry-run
```

### 5. Paralelize Cuando Sea Posible

```bash
# Ejecuta múltiples tareas en paralelo
turbo run lint test typecheck
```

### 6. Usa --continue en CI

```bash
# No detiene si un paquete falla
turbo run test --continue
```

## Troubleshooting

### Problema: "No turbo.json found"

**Solución**: Asegúrate de estar en el directorio root del proyecto.

```bash
cd /path/to/frontend-lq
turbo run build
```

### Problema: "Task X not found"

**Solución**: La tarea no existe en el `package.json` del paquete.

```bash
# Verifica que el paquete tenga el script
cat apps/student-teacher/package.json | grep "\"build\""

# O añade el script al package.json
```

### Problema: Caché no funciona correctamente

**Solución**: Limpia el caché y vuelve a intentar.

```bash
rm -rf .turbo
turbo run build --force
```

### Problema: Build falla con dependencias

**Solución**: Asegúrate de que las dependencias estén buildeadas primero.

```bash
# Build todas las dependencias primero
turbo run build --filter=...@lq/student-teacher

# Luego build la app
turbo run build --filter=@lq/student-teacher
```

### Problema: "Cannot use 'import.meta' outside a module"

**Solución**: Este error suele ocurrir cuando faltan archivos de configuración. Por ejemplo, si usas TailwindCSS,
necesitas un `postcss.config.js`:

```javascript
// postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### Problema: Dev server no se reinicia con cambios

**Solución**: Asegúrate de que `persistent: true` esté en la tarea `dev`.

```json
{
  "dev": {
    "cache": false,
    "persistent": true
  }
}
```

### Problema: Turbo muy lento

**Solución**: Reduce el scope con filtros.

```bash
# En vez de
turbo run build  # Builds everything

# Usa
turbo run build --filter=@lq/student-teacher...  # Solo lo necesario
```

## Comandos Rápidos de Referencia

```bash
# Desarrollo
pnpm dev                                    # Todas las apps
pnpm dev:student-teacher                    # Solo student-teacher
pnpm dev:institutional                      # Solo institutional

# Build
pnpm build                                  # Todo
pnpm build:student-teacher                  # Solo student-teacher
turbo run build --filter=@lq/ui...          # UI y dependientes

# Testing
pnpm test                                   # Todos los tests
turbo run test --filter=[main]              # Solo cambios desde main

# Linting
pnpm lint                                   # Lint todo
pnpm lint:fix                               # Fix automático
turbo run lint --filter="./apps/**"         # Solo apps

# Utilidades
turbo run build --dry-run                   # Ver qué se ejecutaria
turbo run build --force                     # Ignorar caché
turbo run build --verbosity=2               # Modo verbose
turbo run build --summarize                 # Resumen de ejecución
pnpm clean                                  # Limpiar artifacts
pnpm clean:install                          # Reinstalar todo
```

## Recursos Adicionales

- [Documentación Oficial de Turborepo](https://turbo.build/repo/docs)
- [Guia de Filtros](https://turbo.build/repo/docs/core-concepts/monorepos/filtering)
- [Configuración de Pipelines](https://turbo.build/repo/docs/core-concepts/monorepos/running-tasks)
- [Sistema de Caché](https://turbo.build/repo/docs/core-concepts/caching)

## Preguntas Frecuentes

### ¿Cuándo debo usar filtros?

Usa filtros cuando:

- Solo trabajas en una app especifica
- Quieres reducir tiempo de ejecución en dev
- En CI, solo quieres testear lo que cambió

### ¿Cómo sé si el caché funcionó?

Verás `>>> FULL TURBO` en la consola cuando todo viene del caché.

### ¿Puedo desactivar el caché para una tarea?

Si, en `turbo.json`:

```json
{
  "tasks": {
    "mi-tarea": {
      "cache": false
    }
  }
}
```

### ¿Cómo optimizo CI con Turbo?

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: turbo run test --filter=[main] --continue
```

Esto solo testea lo que cambió y continúa aunque algo falle.
