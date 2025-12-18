<script setup lang="ts">
  import { computed } from "vue";
  import ProfileHeader from "~/components/profile/ProfileHeader.vue";
  import PersonalInfoSection from "~/components/profile/PersonalInfoSection.vue";
  import ContactInfoSection from "~/components/profile/ContactInfoSection.vue";
  import SecuritySection from "~/components/profile/SecuritySection.vue";
  import AcademicInfoSection from "~/components/profile/AcademicInfoSection.vue";
  import ChangePasswordModal from "~/components/profile/ChangePasswordModal.vue";
  import { useProfileEditor } from "~/composables/useProfileEditor";
  import { useUserInitials } from "~/composables/useUserInitials";

  // Use profile editor composable
  const {
    localProfile,
    isEditing,
    showPasswordModal,
    startEditing,
    cancelEditing,
    saveProfile,
    updateLocalProfile,
    openPasswordModal,
    handlePasswordChange,
  } = useProfileEditor();

  // Use user initials composable
  const firstName = computed(() => localProfile.value.firstName);
  const lastName = computed(() => localProfile.value.lastName);
  const { initials } = useUserInitials(firstName, lastName);
</script>

<template>
  <div class="py-8 space-y-6">
    <!-- Top Banner -->
    <ProfileHeader />

    <!-- Main Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left Column (Sidebar) - Spans 4 columns -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Avatar & Contact Card -->
        <div
          class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6 shadow-sm"
        >
          <!-- Avatar Section -->
          <div class="flex flex-col items-center mb-8 relative">
            <Avatar
              :image="localProfile.avatar"
              :label="!localProfile.avatar ? initials : undefined"
              size="xlarge"
              shape="square"
              :pt="{
                root: {
                  class:
                    'w-40 h-40 text-4xl rounded-2xl shadow-md bg-surface-200 dark:bg-surface-800 text-surface-600 dark:text-surface-400',
                },
                image: {
                  class: 'rounded-2xl object-cover',
                },
              }"
            />
            <!-- Edit Avatar Button Overlay (Only visible when editing) -->
            <button
              v-if="isEditing"
              type="button"
              class="absolute bottom-0 right-1/2 translate-x-20 translate-y-1 w-10 h-10 rounded-full bg-primary-600 hover:bg-primary-700 text-white flex items-center justify-center shadow-lg transition-colors border-4 border-surface-0 dark:border-surface-900"
            >
              <Icon name="solar:camera-minimalistic-line-duotone" class="text-lg" />
            </button>
          </div>

          <!-- Contact Info Section -->
          <ContactInfoSection
            :user="{
              email: localProfile.email,
              phone: localProfile.phone,
              location: localProfile.location,
              institution: localProfile.institution,
              memberSince: localProfile.memberSince,
              learningLanguage: localProfile.learningLanguages[0],
            }"
            :editable="isEditing"
            @update:user="updateLocalProfile"
          />
        </div>

        <!-- Security Section -->
        <SecuritySection
          :user="{ twoFactorEnabled: localProfile.twoFactorEnabled }"
          @change-password="openPasswordModal"
        />
      </div>

      <!-- Right Column (Main Content) - Spans 8 columns -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Personal Info Card -->
        <PersonalInfoSection
          :user="{
            firstName: localProfile.firstName,
            lastName: localProfile.lastName,
            email: localProfile.email,
            nativeLanguage: localProfile.nativeLanguage,
            learningLanguages: localProfile.learningLanguages,
            bio: localProfile.bio,
          }"
          :editable="isEditing"
          @edit="startEditing"
          @update:user="updateLocalProfile"
        />

        <!-- Academic Info Card -->
        <AcademicInfoSection
          :user="{
            id: localProfile.id,
            grade: localProfile.grade,
            classrooms: localProfile.classrooms,
          }"
        />

        <!-- Role-specific content slot -->
        <slot name="role-specific" />

        <!-- Action Buttons (Only visible when editing) -->
        <div v-if="isEditing" class="flex justify-end gap-3 pt-4">
          <Button
            :label="$t('profile.cancel')"
            severity="secondary"
            class="!bg-surface-200 dark:!bg-surface-700 !text-surface-700 dark:!text-surface-200 !border-0 !rounded-xl !px-6 !py-3 !font-bold hover:!bg-surface-300"
            @click="cancelEditing"
          />
          <Button
            :label="$t('profile.save')"
            class="!bg-primary-600 !border-primary-600 !text-white !rounded-xl !px-6 !py-3 !font-bold hover:!bg-primary-700"
            @click="saveProfile"
          />
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <ChangePasswordModal v-model:visible="showPasswordModal" @submit="handlePasswordChange" />
  </div>
</template>
