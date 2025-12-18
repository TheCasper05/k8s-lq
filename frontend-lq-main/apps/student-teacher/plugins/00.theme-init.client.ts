/**
 * Theme initialization plugin
 * Runs BEFORE app mounts to apply dark mode immediately
 * The 00. prefix ensures this runs first
 */
export default defineNuxtPlugin({
  name: "theme-init",
  enforce: "pre",
  setup() {
    if (typeof window === "undefined") return;

    try {
      const config = localStorage.getItem("lq-theme-config");
      if (config) {
        const parsed = JSON.parse(config);
        if (parsed.darkMode) {
          document.documentElement.classList.add("p-dark");
        }
      }
    } catch {
      // Silently fail
    }
  },
});
