# Guía de Despliegue en AWS Amplify

## Configuración de Variables de Entorno

Para que tu aplicación funcione correctamente en Amplify, debes configurar las siguientes variables de entorno en la
consola de AWS Amplify:

### Variables Requeridas

1. **NUXT_PUBLIC_API_BASE_URL**
   - Valor: URL de tu API de producción (ej: `https://api.lingoquest.com`)
   - Descripción: URL base de tu API Django

2. **NUXT_PUBLIC_GRAPHQL_ENDPOINT**
   - Valor: URL del endpoint GraphQL (ej: `https://api.lingoquest.com/graphql`)
   - Descripción: Endpoint GraphQL de tu API

3. **NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT**
   - Valor: URL WebSocket (ej: `wss://api.lingoquest.com/graphql`)
   - Descripción: Endpoint WebSocket para subscripciones GraphQL

4. **NUXT_PUBLIC_SENTRY_ENVIRONMENT**
   - Valor: `production`
   - Descripción: Ambiente de Sentry

5. **NODE_ENV**
   - Valor: `production`
   - Descripción: Ambiente de Node.js

### Variables Opcionales

6. **NUXT_PUBLIC_SENTRY_DSN**
   - Valor: Tu DSN de Sentry (opcional)
   - Descripción: Para reportar errores a Sentry

7. **SENTRY_ORG** (solo si usas Sentry)
   - Valor: Tu organización de Sentry
   - Descripción: Para subir source maps

8. **SENTRY_PROJECT** (solo si usas Sentry)
   - Valor: Tu proyecto de Sentry
   - Descripción: Para subir source maps

9. **NUXT_PUBLIC_BYPASS_ONBOARDING** (solo entornos de prueba/desarrollo)
   - Valor: `true` o `false` (por defecto `false`)
   - Descripción:
     - Cuando está en `true`, la app **omite el login y el onboarding** y redirige directamente al dashboard por rol.
     - Desactiva las restricciones de los middlewares de autenticación/rol y permite navegar por la app sin sesión real.
     - Útil **solo para pruebas locales o de staging** cuando la API de autenticación no está disponible o está
       inestable.
     - **No habilitar en producción**: permitiría acceso a pantallas internas sin autenticación real.

## Pasos para Configurar en AWS Amplify

1. Ve a la consola de AWS Amplify
2. Selecciona tu aplicación `student-teacher`
3. Ve a "Environment variables" en el menú lateral
4. Haz clic en "Manage variables"
5. Agrega cada variable con su valor correspondiente
6. Guarda los cambios
7. Vuelve a hacer un deploy desde la consola o haciendo push a tu repositorio

## Cambios Realizados

### 1. Archivo `amplify.yml`

- ✅ Cambiado de `nuxt build` a `nuxt generate` para generar archivos estáticos
- ✅ Actualizado `baseDirectory` a `apps/student-teacher/.output/public`

### 2. Archivo `nuxt.config.ts`

- ✅ Agregadas reglas de rutas para deshabilitar SSR en páginas que requieren API
- ✅ Páginas configuradas: `/bookmarks`, `/messages`, `/reports/**`, etc.

## Verificación del Despliegue

Después de configurar las variables y hacer deploy:

1. Visita tu URL de Amplify: https://main.d1fwb24ra7kk6a.amplifyapp.com/
2. Verifica que la página de inicio cargue correctamente
3. Revisa los logs de build en la consola de Amplify si hay errores

## Solución de Problemas

### Error 500

- ✅ **Causa**: Falta configuración de variables de entorno o directorio incorrecto
- ✅ **Solución**: Configurar todas las variables requeridas listadas arriba

### Páginas en blanco

- **Causa**: Páginas que requieren API no están configuradas para client-side rendering
- **Solución**: Ya configurado en `nuxt.config.ts` con `ssr: false`
