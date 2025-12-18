<script setup lang="ts">
  import ThemeConfiguratorContent from "./ThemeConfiguratorContent.vue";
  import Popover from "primevue/popover";
  import { ref } from "vue";

  defineOptions({
    name: "ThemeConfigurator",
  });

  interface Props {
    /**
     * Show primary color picker
     * @default true
     */
    showPrimary?: boolean;
    /**
     * Show surface color picker
     * @default true
     */
    showSurface?: boolean;
    /**
     * Show menu type selector
     * @default true
     */
    showMenuType?: boolean;
    /**
     * Additional CSS classes for the container
     * @default ''
     */
    class?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    showPrimary: true,
    showSurface: true,
    showMenuType: true,
    class: "",
  });

  const popover = ref<InstanceType<typeof Popover>>();

  const toggle = (event: Event) => {
    popover.value?.toggle(event);
  };

  defineExpose({
    toggle,
  });
</script>

<template>
  <Popover ref="popover" :class="['!w-80', props.class]" append-to="body">
    <ThemeConfiguratorContent :show-primary="showPrimary" :show-surface="showSurface" :show-menu-type="showMenuType" />
  </Popover>
</template>
