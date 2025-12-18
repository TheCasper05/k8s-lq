<script setup lang="ts">
  import illustrationSrc from "~/assets/images/login-illustration-person.png";

  const features = [
    { icon: "💬", labelKey: "auth.featureAiConversations" },
    { icon: "⚡", labelKey: "auth.featureInstantFeedback" },
    { icon: "🎯", labelKey: "auth.featureGamification" },
  ];

  const stats = [
    { value: "10K+", labelKey: "auth.statsStudents" },
    { value: "500K+", labelKey: "auth.statsConversations" },
    { value: "95%", labelKey: "auth.statsSuccessRate" },
  ];
</script>

<template>
  <div class="flex flex-col items-center justify-center px-8 py-12">
    <!-- Language Selector Badge -->
    <div class="mb-8">
      <Chip
        unstyled
        :label="$t('auth.aiPoweredLearning')"
        pt:root="flex items-center gap-2 px-4 h-10 py-2 bg-secondary-200 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 rounded-full font-semibold border border-secondary-400 dark:border-purple-700/50 backdrop-blur-sm shadow-sm"
      >
        <template #icon>
          <Icon name="lucide:sparkles" />
        </template>
      </Chip>
    </div>

    <!-- Main Heading -->
    <h2 class="text-2xl font-bold text-center dark:text-white mb-3 max-w-md leading-tight">
      {{ $t("auth.welcomeHeading") }}
    </h2>

    <!-- Subheading -->
    <p class="text-center text-gray-500 dark:text-surface-400 mb-12 max-w-sm text-md leading-relaxed">
      {{ $t("auth.welcomeSubheading") }}
    </p>

    <!-- Circular Illustration Container -->
    <div class="relative mb-12">
      <!-- Main Circle with Enhanced Shadow -->
      <div
        class="w-80 h-80 rounded-full bg-gradient-to-br from-purple-50/90 to-white/90 dark:from-surface-800/90 dark:to-surface-700/90 flex items-center justify-center overflow-hidden backdrop-blur-sm"
        style="
          box-shadow:
            0 25px 50px -12px rgba(147, 51, 234, 0.15),
            0 0 0 1px rgba(147, 51, 234, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        "
      >
        <img :src="illustrationSrc" alt="AI Learning Illustration" class="w-64 h-64 object-contain" />
      </div>

      <!-- Decorative Floating Elements Around Circle -->
      <!-- Top Center - Yellow star -->
      <div class="absolute -top-6 left-1/3 text-5xl animate-float">✨</div>

      <!-- Left - Purple heart -->
      <div class="absolute top-1/2 -left-12 text-4xl animate-bounce-slow">💜</div>

      <!-- Right - Red/orange circle -->
      <div class="absolute top-1/2 mt-2 -right-8 text-3xl animate-float">🎯</div>

      <!-- Bottom Center - Star -->
      <div class="absolute bottom-0 left-1/3 text-5xl animate-bounce-slow">⭐</div>
    </div>

    <!-- Feature Chips -->
    <div class="flex flex-wrap justify-center gap-3 mb-12">
      <Chip
        v-for="(feature, index) in features"
        :key="index"
        unstyled
        :label="$t(feature.labelKey)"
        pt:root="flex items-center px-4 h-14 py-2 bg-secondary-200 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300 rounded-full font-semibold border border-secondary-400 dark:border-purple-700/50 backdrop-blur-sm shadow-sm"
      >
        <template #icon>
          <span class="text-2xl -mt-1">{{ feature.icon }}</span>
        </template>
      </Chip>
    </div>

    <div class="grid grid-cols-3 gap-12 w-full max-w-lg">
      <div v-for="(stat, index) in stats" :key="index" class="text-center">
        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400 mb-1">{{ stat.value }}</div>
        <div class="text-sm text-gray-500 dark:text-surface-400 font-medium">{{ $t(stat.labelKey) }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
  @keyframes float {
    0%,
    100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  @keyframes float-delayed {
    0%,
    100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-15px);
    }
  }

  @keyframes bounce-slow {
    0%,
    100% {
      transform: translateY(0px) rotate(0deg);
    }
    50% {
      transform: translateY(-8px) rotate(5deg);
    }
  }

  @keyframes bounce-slow-delayed {
    0%,
    100% {
      transform: translateY(0px) rotate(0deg);
    }
    50% {
      transform: translateY(-12px) rotate(-5deg);
    }
  }

  .animate-float {
    animation: float 3s ease-in-out infinite;
  }

  .animate-float-delayed {
    animation: float-delayed 3s ease-in-out infinite 0.5s;
  }

  .animate-bounce-slow {
    animation: bounce-slow 4s ease-in-out infinite;
  }

  .animate-bounce-slow-delayed {
    animation: bounce-slow-delayed 4s ease-in-out infinite 1s;
  }
</style>
