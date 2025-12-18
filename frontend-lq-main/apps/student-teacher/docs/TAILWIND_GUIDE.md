# Guía de Tailwind CSS - LingoQuesto

## Colores Personalizados

### Paleta de Colores

Todos los colores están disponibles en 11 tonos (50-950) para máxima flexibilidad:

#### Primary (Azul)

```vue
<div class="bg-primary-500 text-white">Botón Principal</div>
<div class="text-primary-600">Texto azul</div>
<div class="border-primary-500">Borde azul</div>
```

#### Secondary (Púrpura)

```vue
<div class="bg-secondary-500 text-white">Acento</div>
<div class="text-secondary-600">Texto púrpura</div>
```

#### Success (Verde)

```vue
<div class="bg-success-500 text-white">¡Éxito!</div>
<div class="text-success-600">Mensaje de éxito</div>
```

#### Warning (Amarillo)

```vue
<div class="bg-warning-500 text-white">Advertencia</div>
<div class="text-warning-600">Alerta</div>
```

#### Danger (Rojo)

```vue
<div class="bg-danger-500 text-white">Error</div>
<div class="text-danger-600">Mensaje de error</div>
```

## Clases de Componentes Personalizadas

### Botones

```vue
<!-- Botón primario -->
<button class="btn-primary">Iniciar Sesión</button>

<!-- Botón secundario -->
<button class="btn-secondary">Acción Secundaria</button>

<!-- Botón outline -->
<button class="btn-outline">Cancelar</button>
```

### Inputs

```vue
<input type="text" class="input-base" placeholder="Email" />
```

### Cards

```vue
<div class="card">
  <h3 class="text-xl font-bold mb-2">Título</h3>
  <p class="text-gray-600">Contenido de la tarjeta</p>
</div>
```

### Container

```vue
<div class="lq-container">
  <!-- Contenido con máximo ancho y padding responsive -->
</div>
```

## Utilidades Personalizadas

### Gradientes

```vue
<!-- Texto con gradiente -->
<h1 class="text-gradient text-4xl font-bold">LingoQuesto</h1>

<!-- Fondo gradiente primario -->
<div class="bg-gradient-primary p-6">Contenido</div>

<!-- Fondo gradiente secundario -->
<div class="bg-gradient-secondary p-6">Contenido</div>
```

### Sombras

```vue
<!-- Sombra suave personalizada -->
<div class="card shadow-soft">Tarjeta con sombra suave</div>
```

## Animaciones

```vue
<!-- Fade in -->
<div class="animate-fade-in">Aparece gradualmente</div>

<!-- Slide in -->
<div class="animate-slide-in">Se desliza hacia abajo</div>

<!-- Bounce sutil -->
<div class="animate-bounce-subtle">Rebote suave</div>
```

## Tipografía

```vue
<!-- Fuente display (Lexend) para títulos -->
<h1 class="font-display text-4xl font-bold">Título Principal</h1>

<!-- Fuente sans (Inter) para texto normal (por defecto) -->
<p class="font-sans text-base">Texto del cuerpo</p>
```

## Ejemplos Prácticos

### Tarjeta de Login

```vue
<div class="flex min-h-screen items-center justify-center bg-gray-100">
  <div class="w-full max-w-md">
    <div class="card shadow-soft">
      <h2 class="mb-6 text-center text-2xl font-bold text-primary-700">
        Iniciar Sesión
      </h2>

      <form>
        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            class="input-base"
            placeholder="tu@email.com"
          />
        </div>

        <button type="submit" class="btn-primary w-full">
          Entrar
        </button>
      </form>
    </div>
  </div>
</div>
```

### Alert Success

```vue
<div class="rounded-lg bg-success-50 border border-success-200 p-4">
  <div class="flex items-center gap-3">
    <div class="size-5 rounded-full bg-success-500"></div>
    <p class="text-success-800 font-medium">
      ¡Operación exitosa!
    </p>
  </div>
</div>
```

### Badge

```vue
<span class="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-800">
  Nuevo
</span>
```

## Modo Oscuro (Opcional)

Para agregar soporte de modo oscuro, usa el prefijo `dark:`:

```vue
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Contenido que se adapta al modo oscuro
</div>
```

## Responsive Design

Todos los colores y utilidades funcionan con los breakpoints de Tailwind:

```vue
<div class="bg-primary-500 md:bg-secondary-500 lg:bg-success-500">
  <!-- Cambia de color según el tamaño de pantalla -->
</div>
```

Breakpoints disponibles:

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

## Tips de Uso

1. **Usa los tonos correctos:**
   - 50-100: Fondos muy claros
   - 200-300: Fondos claros, bordes
   - 400-600: Colores principales (botones, texto destacado)
   - 700-900: Tonos oscuros (hover, texto sobre fondos claros)
   - 950: Muy oscuro

2. **Contraste de texto:**
   - Sobre fondos 50-400: usa texto oscuro (`text-gray-900`)
   - Sobre fondos 500-950: usa texto blanco (`text-white`)

3. **Estados hover:**

   ```vue
   <button class="bg-primary-600 hover:bg-primary-700">
     Botón con hover
   </button>
   ```

4. **Focus states:**
   ```vue
   <input class="focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
   ```
