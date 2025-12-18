import { computed, type Ref } from "vue";

/**
 * Composable to generate user initials from first and last name
 * @param firstName - Reactive reference to first name
 * @param lastName - Reactive reference to last name
 * @returns Computed uppercase initials (e.g., "JD" for "John Doe")
 */
export const useUserInitials = (firstName: Ref<string>, lastName: Ref<string>) => {
  const initials = computed(() => {
    const first = firstName.value?.[0] || "";
    const last = lastName.value?.[0] || "";
    return `${first}${last}`.toUpperCase();
  });

  return {
    initials,
  };
};
