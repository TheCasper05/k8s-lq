<script setup lang="ts">
  import { LqAvatar } from "@lq/ui";

  defineOptions({
    name: "UserAvatarButton",
  });

  interface Props {
    /**
     * Avatar image URL
     */
    avatarUrl?: string;
    /**
     * User name for alt text
     * @default 'User'
     */
    userName?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    userName: "John Doe",
    avatarUrl: undefined,
  });

  const emit = defineEmits<{
    click: [];
  }>();

  const handleClick = () => {
    emit("click");
  };

  // Default avatar if none provided
  const finalAvatarUrl = computed(() => {
    return props.avatarUrl || "https://i.pravatar.cc/150?u=default";
  });
</script>

<template>
  <button
    type="button"
    class="focus:outline-none rounded-full"
    :aria-label="`${userName} profile`"
    @click="handleClick"
  >
    <LqAvatar :src="finalAvatarUrl" size="md" shape="circle" class="cursor-pointer mt-1" />
  </button>
</template>
