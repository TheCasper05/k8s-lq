/* This TypeScript code snippet is defining a custom composition function `useSidebar` that manages the
state of a sidebar in a Vue 3 application. Here's a breakdown of what each part of the code is
doing: */
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
import { useLayout } from "@lq/composables";

const breakpoints = useBreakpoints(breakpointsTailwind);
const isSmallerThanLg = breakpoints.smaller("lg");

// Drawer visibility (only for mobile/tablet)
// In desktop, sidebar is always visible (fixed)
const sidebarVisible = ref(false);

// Auto-close drawer when switching from mobile to desktop
watch(isSmallerThanLg, (isSmaller) => {
  if (!isSmaller) {
    sidebarVisible.value = false; // Close drawer when switching to desktop
  }
});

/**
 * The useSidebar function manages the visibility and styling of a sidebar in a TypeScript application.
 */
export const useSidebar = () => {
  const { menuType } = useLayout();

  /**
   * The function `toggleSidebar` toggles the visibility of the sidebar.
   */
  const toggleSidebar = () => {
    sidebarVisible.value = !sidebarVisible.value;
  };

  /**
   * The `openSidebar` function sets the value of `sidebarVisible` to true.
   */
  const openSidebar = () => {
    sidebarVisible.value = true;
  };

  /**
   * The function `closeSidebar` sets the value of `sidebarVisible` to false.
   */
  const closeSidebar = () => {
    sidebarVisible.value = false;
  };

  /* The `contentMargin` computed property calculates the margin based on the menu type variant.
  Icon-only variant uses 80px, other variants use 300px.
  On mobile/tablet (< 1024px), margin is always 0 to allow full-width content (drawer overlay).
  On desktop (>= 1024px), margin is always applied (sidebar is fixed and pushes content).
  Uses VueUse breakpoints for reactive detection. */
  const contentMargin = computed(() => {
    // Mobile/tablet: no margin (drawer overlays content)
    if (isSmallerThanLg.value) {
      return "0px";
    }

    // Desktop: always apply margin (sidebar is fixed and visible)
    return menuType.value === "icon-only" ? "80px" : "300px";
  });

  return {
    sidebarVisible,
    toggleSidebar,
    openSidebar,
    closeSidebar,
    contentMargin,
  };
};
