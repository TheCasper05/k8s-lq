# LqMetricCard

A specialized card component for displaying metrics and KPIs with multiple layout variants.

## Features

- 🎨 **3 Variants**: Default (vertical), Horizontal, and Boxed layouts
- 🎯 **5 Color Themes**: Primary, Info, Success, Warning, Danger
- 📊 **Trend Support**: Optional trend badge for showing changes
- ♿ **Accessible**: Built with semantic HTML
- 🌙 **Dark Mode**: Full dark mode support
- ✨ **Hover Effects**: Built-in hover animations

## Installation

```typescript
import { LqMetricCard, type LqMetric } from "@lq/ui";
```

## Basic Usage

### Boxed Variant (Recommended for Dashboards)

```vue
<script setup lang="ts">
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  const metric: LqMetric = {
    icon: "solar:users-group-rounded-line-duotone",
    label: "Total Students",
    value: 1234,
    color: "primary",
    trend: "+12%",
  };
</script>

<template>
  <LqMetricCard :metric="metric" variant="boxed" />
</template>
```

### Default Variant (Vertical)

```vue
<script setup lang="ts">
  const metric: LqMetric = {
    icon: "solar:chart-line-duotone",
    label: "Revenue",
    value: "$45.2K",
    color: "success",
  };
</script>

<template>
  <LqMetricCard :metric="metric" variant="default" />
</template>
```

### Horizontal Variant

```vue
<script setup lang="ts">
  const metric: LqMetric = {
    icon: "solar:clock-circle-line-duotone",
    label: "Practice Time",
    value: "127h 45m",
    color: "info",
  };
</script>

<template>
  <LqMetricCard :metric="metric" variant="horizontal" />
</template>
```

## Props

### LqMetricCard Props

| Prop      | Type                                   | Default      | Description        |
| --------- | -------------------------------------- | ------------ | ------------------ |
| `metric`  | `LqMetric`                             | **required** | Metric data object |
| `variant` | `'default' \| 'horizontal' \| 'boxed'` | `'default'`  | Layout variant     |

### LqMetric Interface

```typescript
interface LqMetric {
  icon: string; // Icon name (e.g., "solar:users-group-rounded-line-duotone")
  label: string; // Metric label/description
  value: string | number; // Metric value
  color?: "primary" | "info" | "success" | "warning" | "danger"; // Color theme
  trend?: string; // Optional trend indicator (e.g., "+12%", "-5%")
}
```

## Variants

### Default (Vertical)

Large, prominent display with icon on the right. Best for hero metrics.

**Layout:**

- Label and icon in header row
- Large value display (5xl font)
- Rounded corners (3xl)
- Padding: 6

**Use case:** Main dashboard KPIs, hero metrics

### Horizontal

Icon on the left with label and value stacked on the right.

**Layout:**

- 16x16 icon with colored background
- Label above value
- Rounded corners (2xl)
- Padding: 6

**Use case:** Sidebar metrics, compact displays

### Boxed

Compact layout with icon and optional trend badge.

**Layout:**

- 10x10 icon in top-left
- Optional trend badge in top-right
- Value and label stacked below
- Rounded corners (2xl)
- Padding: 5

**Use case:** Dashboard grids, metric cards

## Color Themes

Each color theme provides consistent styling across light and dark modes:

| Color     | Use Case           | Light Mode    | Dark Mode                |
| --------- | ------------------ | ------------- | ------------------------ |
| `primary` | General metrics    | Blue tones    | Blue tones (adjusted)    |
| `info`    | Informational      | Blue          | Blue (adjusted)          |
| `success` | Positive metrics   | Emerald green | Emerald green (adjusted) |
| `warning` | Alerts, time-based | Amber         | Amber (adjusted)         |
| `danger`  | Critical metrics   | Rose red      | Rose red (adjusted)      |

## Examples

### Dashboard Metrics Grid

```vue
<script setup lang="ts">
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  const metrics: LqMetric[] = [
    {
      icon: "solar:users-group-rounded-line-duotone",
      label: "Total Students",
      value: 1234,
      color: "primary",
      trend: "+12%",
    },
    {
      icon: "solar:document-text-line-duotone",
      label: "Active Scenarios",
      value: 45,
      color: "info",
      trend: "+8%",
    },
    {
      icon: "solar:clock-circle-line-duotone",
      label: "Practice Time",
      value: "127h",
      color: "success",
      trend: "+15%",
    },
    {
      icon: "solar:chart-line-duotone",
      label: "Avg Score",
      value: "85%",
      color: "warning",
    },
  ];
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <LqMetricCard v-for="(metric, index) in metrics" :key="index" :metric="metric" variant="boxed" />
  </div>
</template>
```

### With Computed Values

```vue
<script setup lang="ts">
  import { computed } from "vue";
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  const totalUsers = ref(1234);
  const previousTotal = ref(1100);

  const userMetric = computed(
    (): LqMetric => ({
      icon: "solar:users-group-rounded-line-duotone",
      label: "Total Users",
      value: totalUsers.value,
      color: "primary",
      trend: `+${Math.round(((totalUsers.value - previousTotal.value) / previousTotal.value) * 100)}%`,
    }),
  );
</script>

<template>
  <LqMetricCard :metric="userMetric" variant="boxed" />
</template>
```

### Mixed Variants Layout

```vue
<template>
  <div class="space-y-6">
    <!-- Hero Metric -->
    <LqMetricCard :metric="heroMetric" variant="default" />

    <!-- Grid of Boxed Metrics -->
    <div class="grid grid-cols-3 gap-4">
      <LqMetricCard v-for="metric in gridMetrics" :key="metric.label" :metric="metric" variant="boxed" />
    </div>

    <!-- Horizontal Metrics in Sidebar -->
    <div class="space-y-3">
      <LqMetricCard v-for="metric in sidebarMetrics" :key="metric.label" :metric="metric" variant="horizontal" />
    </div>
  </div>
</template>
```

## Styling

The component uses `LqCard` internally and inherits its styling system. Custom styling can be applied via:

- Tailwind utility classes on the wrapper
- CSS custom properties for theme colors
- PrimeVue theme configuration

## Accessibility

- Semantic HTML structure
- Proper color contrast ratios
- Screen reader friendly labels
- Keyboard navigation support (via LqCard)

## Related Components

- **LqCard**: Base card component
- **LqDataTable**: For tabular metrics
- **LqBadge**: For status indicators

## Best Practices

1. **Use appropriate variants**: Boxed for grids, Default for hero metrics, Horizontal for sidebars
2. **Consistent colors**: Use color themes consistently across your app
3. **Meaningful trends**: Only show trends when they add value
4. **Readable values**: Format large numbers (e.g., "1.2K" instead of "1234")
5. **Icon selection**: Use icons that clearly represent the metric

## Notes

- The component automatically handles hover effects
- All variants are fully responsive
- Dark mode is automatically applied based on theme
- Trend badges use the same color as the metric for consistency
