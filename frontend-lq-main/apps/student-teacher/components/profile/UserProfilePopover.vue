<script setup lang="ts">
  import { useAuthStore } from "@lq/stores";
  import { FEATURE_FLAGS } from "~/types/feature-flags";
  import { AccountType } from "@lq/types";
  import { getRoleDashboardRoute } from "@lq/utils";

  interface Props {
    userAvatar?: string;
  }

  defineProps<Props>();

  const authStore = useAuthStore();
  const router = useRouter();

  const { t: $t } = useI18n();
  const { withRolePrefix } = useRoleLayout();

  const userProfile = computed(() => authStore.userProfile || authStore.userProfileComplete);
  const userAuth = computed(() => authStore.userAuth);

  const userFullName = computed(() => {
    if (!userProfile.value) return "User";
    return `${userProfile.value.firstName} ${userProfile.value.lastName}`.trim();
  });

  const userEmail = computed(() => {
    return userAuth.value?.email || userProfile.value?.user?.email || "";
  });

  // Get role display name
  const getRoleDisplayName = (role: string) => {
    const roleKey = role.toLowerCase().replace(/_/g, "");
    const roleMap: Record<string, string> = {
      student: "roles.student",
      teacher: "roles.teacher",
      admininstitucional: "roles.adminInstitucional",
      admin: "roles.admin",
    };
    return $t(roleMap[roleKey] || "roles.student");
  };

  const userRole = computed(() => {
    if (!userProfile.value?.primaryRole) return "";
    return getRoleDisplayName(userProfile.value.primaryRole);
  });

  // Multi-role support
  const isMultiRoleEnabled = computed(() => FEATURE_FLAGS.MULTI_ROLE_SUPPORT);

  // TODO: Replace with actual user roles from backend when available
  // For now, simulate multiple roles for demo purposes
  const availableRoles = computed<AccountType[]>(() => {
    if (!isMultiRoleEnabled.value) return [];
    // Simulate user having multiple roles
    return [AccountType.STUDENT, AccountType.TEACHER, AccountType.ADMIN_INSTITUCIONAL];
  });

  const hasMultipleRoles = computed(() => availableRoles.value.length > 1);

  const roleMenuOpen = ref(false);

  const toggleRoleMenu = () => {
    if (hasMultipleRoles.value) {
      roleMenuOpen.value = !roleMenuOpen.value;
    }
  };

  const switchRole = async (newRole: AccountType) => {
    if (newRole === userProfile.value?.primaryRole) {
      roleMenuOpen.value = false;
      return;
    }

    // TODO: Implement actual role switching logic with backend
    // For now, just update the store and navigate
    console.log(`Switching to role: ${newRole}`);

    // Close the role menu
    roleMenuOpen.value = false;

    // Hide the popover
    hide();

    // Navigate to the new role's dashboard
    await router.push(getRoleDashboardRoute(newRole));
  };

  const getRoleIcon = (role: AccountType) => {
    const iconMap: Record<AccountType, string> = {
      [AccountType.STUDENT]: "solar:book-linear",
      [AccountType.TEACHER]: "solar:book-2-linear",
      [AccountType.ADMIN_INSTITUCIONAL]: "solar:shield-user-linear",
    };
    return iconMap[role];
  };

  const userInitials = computed(() => {
    if (!userProfile.value) return "U";
    const firstName = userProfile.value.firstName || "";
    const lastName = userProfile.value.lastName || "";
    if (firstName && lastName) {
      return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    }
    return userFullName.value.charAt(0).toUpperCase();
  });

  const popoverRef = ref();

  const toggle = (event: Event) => {
    popoverRef.value?.toggle(event);
  };

  const hide = () => {
    popoverRef.value?.hide();
    roleMenuOpen.value = false;
  };

  defineExpose({
    toggle,
    hide,
  });

  const handleLogout = async () => {
    hide();
    await authStore.logout();
    await router.push("/auth/login");
  };
</script>

<template>
  <Popover ref="popoverRef" class="w-80">
    <div class="p-4">
      <!-- User Info Section -->
      <div class="flex items-center gap-4 pb-4 border-b border-surface-200 dark:border-surface-700">
        <!-- Avatar -->
        <div class="relative">
          <Avatar
            :image="userAvatar"
            :label="userInitials"
            size="large"
            shape="circle"
            class="bg-gradient-to-br from-primary-500 to-primary-600 text-white font-semibold"
          />
          <div
            class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-surface-800 rounded-full"
          />
        </div>

        <!-- User Details -->
        <div class="flex-1 min-w-0">
          <h3 class="text-base font-semibold text-surface-900 dark:text-surface-0 truncate">
            {{ userFullName }}
          </h3>
          <p class="text-sm text-surface-600 dark:text-surface-400 truncate">{{ userEmail }}</p>

          <!-- Role Badge - Clickable if multi-role enabled -->
          <button
            v-if="userRole"
            type="button"
            :class="[
              'inline-flex items-center gap-1.5 px-2 py-1 mt-1 rounded-md text-xs font-medium transition-all duration-200',
              hasMultipleRoles
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 hover:bg-primary-200 dark:hover:bg-primary-900/50 cursor-pointer'
                : 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 cursor-default',
            ]"
            @click="toggleRoleMenu"
          >
            <Icon
              v-if="userProfile?.primaryRole"
              :name="getRoleIcon(userProfile.primaryRole as AccountType)"
              class="w-3.5 h-3.5"
            />
            <span>{{ userRole }}</span>
            <Icon
              v-if="hasMultipleRoles"
              name="solar:alt-arrow-down-linear"
              class="w-3 h-3 transition-transform"
              :class="{ 'rotate-180': roleMenuOpen }"
            />
          </button>
        </div>
      </div>

      <!-- Role Selector (when multi-role is enabled) -->
      <Transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div v-if="roleMenuOpen && hasMultipleRoles" class="py-2 border-b border-surface-200 dark:border-surface-700">
          <p class="px-3 text-xs font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider mb-2">
            {{ $t("nav.switchRole") }}
          </p>
          <div class="space-y-1">
            <button
              v-for="role in availableRoles"
              :key="role"
              type="button"
              :class="[
                'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                role === userProfile?.primaryRole
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800',
              ]"
              @click="switchRole(role)"
            >
              <Icon :name="getRoleIcon(role)" class="w-5 h-5" />
              <span class="flex-1 text-left">{{ getRoleDisplayName(role) }}</span>
              <Icon
                v-if="role === userProfile?.primaryRole"
                name="solar:check-circle-bold"
                class="w-5 h-5 text-primary-600 dark:text-primary-400"
              />
            </button>
          </div>
        </div>
      </Transition>

      <!-- Menu Items -->
      <div class="py-2">
        <!-- Profile Link -->
        <NuxtLink
          :to="withRolePrefix('profile')"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors duration-200"
          @click="hide()"
        >
          <Icon name="solar:user-linear" class="w-5 h-5 text-surface-500 dark:text-surface-400" />
          <span class="text-sm font-medium">{{ $t("nav.profile") }}</span>
        </NuxtLink>

        <!-- Settings Link -->
        <NuxtLink
          to="/settings"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors duration-200"
          @click="hide()"
        >
          <Icon name="solar:settings-linear" class="w-5 h-5 text-surface-500 dark:text-surface-400" />
          <span class="text-sm font-medium">{{ $t("nav.settings") }}</span>
        </NuxtLink>
      </div>

      <!-- Logout Button -->
      <div class="pt-2 border-t border-surface-200 dark:border-surface-700">
        <Button :label="$t('nav.logout')" severity="danger" text class="w-full justify-start" @click="handleLogout">
          <template #icon>
            <Icon name="solar:logout-2-linear" class="w-5 h-5" />
          </template>
        </Button>
      </div>
    </div>
  </Popover>
</template>
