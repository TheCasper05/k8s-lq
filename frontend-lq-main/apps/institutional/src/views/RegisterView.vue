<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="absolute top-4 right-4">
      <ThemeToggle />
    </div>

    <div class="w-full max-w-md px-4">
      <Card class="shadow-lg">
        <template #content>
          <h2 class="mb-6 text-center text-2xl font-bold text-[#7008E7]">{{ t("auth.register") }}</h2>

          <Message v-if="errorMessage" severity="error" :closable="true" class="mb-4" @close="errorMessage = ''">
            {{ errorMessage }}
          </Message>

          <form class="space-y-4" @submit.prevent="handleRegister">
            <div>
              <label for="firstName" class="mb-2 block text-sm font-medium text-gray-700">Nombre</label>
              <InputText
                id="firstName"
                v-model="form.firstName"
                type="text"
                class="w-full"
                placeholder="Ingresa tu nombre"
                :disabled="isLoading"
                autocomplete="given-name"
                required
              />
            </div>

            <div>
              <label for="lastName" class="mb-2 block text-sm font-medium text-gray-700">Apellido</label>
              <InputText
                id="lastName"
                v-model="form.lastName"
                type="text"
                class="w-full"
                placeholder="Ingresa tu apellido"
                :disabled="isLoading"
                autocomplete="family-name"
                required
              />
            </div>

            <div>
              <label for="email" class="mb-2 block text-sm font-medium text-gray-700">{{ t("auth.email") }}</label>
              <InputText
                id="email"
                v-model="form.email"
                type="email"
                class="w-full"
                :placeholder="t('auth.emailPlaceholder')"
                :disabled="isLoading"
                autocomplete="email"
                required
              />
            </div>

            <div>
              <label for="password" class="mb-2 block text-sm font-medium text-gray-700">
                {{ t("auth.password") }}
              </label>
              <Password
                id="password"
                v-model="form.password"
                class="w-full"
                :placeholder="t('auth.passwordPlaceholder')"
                :disabled="isLoading"
                toggle-mask
                :feedback="false"
                required
              />
            </div>

            <div>
              <label for="confirmPassword" class="mb-2 block text-sm font-medium text-gray-700">
                {{ t("auth.confirmPassword") }}
              </label>
              <Password
                id="confirmPassword"
                v-model="form.confirmPassword"
                class="w-full"
                :placeholder="t('auth.confirmPassword')"
                :disabled="isLoading"
                toggle-mask
                :feedback="false"
                required
              />
            </div>

            <Button
              type="submit"
              class="w-full"
              :loading="isLoading"
              :label="isLoading ? 'Creando cuenta...' : t('auth.registerButton')"
            />
          </form>

          <div class="mt-6 text-center text-sm text-gray-600">
            ¿Ya tienes cuenta?
            <RouterLink to="/login" class="font-semibold text-[#7008E7] hover:underline">
              {{ t("auth.login") }}
            </RouterLink>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { reactive, ref } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useI18n } from "vue-i18n";
  import { useToast } from "primevue/usetoast";
  import { useAuthStore } from "@lq/stores";
  import { ThemeToggle } from "@lq/ui";
  import Card from "primevue/card";
  import InputText from "primevue/inputtext";
  import Password from "primevue/password";
  import Button from "primevue/button";
  import Message from "primevue/message";

  const router = useRouter();
  const route = useRoute();
  const { t } = useI18n();
  const toast = useToast();
  const authStore = useAuthStore();

  const form = reactive({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const isLoading = ref(false);
  const errorMessage = ref("");

  const handleRegister = async () => {
    errorMessage.value = "";

    if (
      !form.firstName.trim() ||
      !form.lastName.trim() ||
      !form.email.trim() ||
      !form.password ||
      !form.confirmPassword
    ) {
      errorMessage.value = "Completa todos los campos obligatorios";
      toast.add({
        severity: "warn",
        summary: t("common.error"),
        detail: errorMessage.value,
        life: 3000,
      });
      return;
    }

    if (form.password !== form.confirmPassword) {
      errorMessage.value = "Las contraseñas no coinciden";
      toast.add({
        severity: "warn",
        summary: t("common.error"),
        detail: errorMessage.value,
        life: 3000,
      });
      return;
    }

    isLoading.value = true;
    try {
      const response = await authStore.register({
        firstName: form.firstName.trim(),
        lastName: form.lastName.trim(),
        email: form.email.trim(),
        password: form.password,
        password2: form.confirmPassword,
      });

      if (response.success) {
        toast.add({
          severity: "success",
          summary: "Cuenta creada",
          detail: "Bienvenido a LingoQuesto",
          life: 3000,
        });

        const redirect = (route.query.redirect as string) || "/dashboard";
        await router.push(redirect);
        return;
      }

      const hasVerifyFlow = response.requiresEmailVerification === true;

      toast.add({
        severity: "success",
        summary: "Revisa tu correo",
        detail: hasVerifyFlow
          ? "Te enviamos un enlace de verificación para activar tu cuenta."
          : "Tu cuenta fue creada, inicia sesión para continuar.",
        life: 4000,
      });

      await router.push({
        name: "login",
        query: route.query?.redirect ? { redirect: route.query.redirect as string } : {},
      });
    } catch (error: any) {
      const message = error?.message || "No pudimos completar el registro. Intenta de nuevo.";
      errorMessage.value = message;
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: message,
        life: 5000,
      });
    } finally {
      isLoading.value = false;
    }
  };
</script>
