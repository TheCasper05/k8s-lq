<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <!-- Theme Toggle (top right) -->
    <div class="absolute top-4 right-4">
      <ThemeToggle />
    </div>

    <div class="w-full max-w-md px-4">
      <!-- Logo/Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-[#7008E7]">LingoQuesto</h1>
        <p class="mt-2 text-sm text-gray-600">Portal Institucional</p>
      </div>

      <Card class="shadow-lg">
        <template #content>
          <h2 class="mb-6 text-center text-2xl font-bold">
            {{ t("auth.login") }}
          </h2>

          <!-- Error Message -->
          <Message v-if="errorMessage" severity="error" :closable="true" @close="errorMessage = ''">
            {{ errorMessage }}
          </Message>

          <form class="space-y-4" @submit.prevent="handleLogin">
            <div>
              <label for="email" class="mb-2 block text-sm font-medium">
                {{ t("auth.email") }}
              </label>
              <InputText
                id="email"
                v-model="form.email"
                type="email"
                class="w-full"
                :placeholder="t('auth.emailPlaceholder')"
                :disabled="isLoading"
                required
              />
            </div>

            <div>
              <label for="password" class="mb-2 block text-sm font-medium">
                {{ t("auth.password") }}
              </label>
              <Password
                id="password"
                v-model="form.password"
                class="w-full"
                :placeholder="t('auth.passwordPlaceholder')"
                :disabled="isLoading"
                :feedback="false"
                toggle-mask
                required
              />
            </div>

            <Button
              type="submit"
              class="w-full"
              :loading="isLoading"
              :label="isLoading ? 'Iniciando sesión...' : t('auth.loginButton')"
            />
          </form>
        </template>
      </Card>

      <!-- Footer info -->
      <div class="mt-4 text-center text-sm text-gray-600">
        <p>Usuario de prueba: e@e.com</p>
        <p class="text-xs text-gray-500">Contraseña: Contrasena1</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { reactive, ref } from "vue";
  import { useRouter, useRoute } from "vue-router";
  import { useI18n } from "vue-i18n";
  import { useAuthStore } from "@lq/stores";
  import { ThemeToggle } from "@lq/ui";
  import InputText from "primevue/inputtext";
  import Password from "primevue/password";
  import Button from "primevue/button";
  import Card from "primevue/card";
  import Message from "primevue/message";

  const { t } = useI18n();
  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore();

  const form = reactive({
    email: "",
    password: "",
  });

  const isLoading = ref(false);
  const errorMessage = ref("");

  const handleLogin = async () => {
    isLoading.value = true;
    errorMessage.value = "";

    try {
      await authStore.login(form.email, form.password);
      const redirect = (route.query.redirect as string) || "/dashboard";
      router.push(redirect);
    } catch (error: any) {
      console.error("Login failed:", error);
      errorMessage.value = error.message || "Error al iniciar sesión. Por favor, intenta de nuevo.";
    } finally {
      isLoading.value = false;
    }
  };
</script>
