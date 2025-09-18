<template>
  <div 
    v-if="appStore.isLoading"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-all duration-300"
  >
    <!-- Loading Container -->
    <div class="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-2xl rounded-2xl border border-white/20 dark:border-slate-700/20 p-8 mx-4 max-w-sm w-full">
      <div class="flex flex-col items-center space-y-6">
        <!-- Spinner -->
        <div class="relative">
          <div class="w-16 h-16 border-4 border-slate-200 dark:border-slate-600 rounded-full animate-pulse"></div>
          <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
          
          <!-- Inner accent -->
          <div class="absolute inset-2 w-12 h-12 border-2 border-transparent border-t-indigo-400 dark:border-t-indigo-300 rounded-full animate-spin" style="animation-duration: 1.5s; animation-direction: reverse;"></div>
        </div>
        
        <!-- Loading Text -->
        <div class="text-center">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            {{ loadingText }}
          </h3>
          <p class="text-sm text-slate-500 dark:text-slate-400">
            Aguarde um momento...
          </p>
        </div>
        
        <!-- Progress dots -->
        <div class="flex space-x-1">
          <div 
            v-for="i in 3" 
            :key="i"
            class="w-2 h-2 bg-blue-500 dark:bg-blue-400 rounded-full animate-bounce"
            :style="{ animationDelay: `${(i - 1) * 0.2}s` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../composables/useAppStore'

// Store
const appStore = useAppStore()

// Props
const props = defineProps({
  text: {
    type: String,
    default: 'Carregando'
  }
})

// Computed
const loadingText = computed(() => props.text)
</script>

<style scoped>
/* Animação personalizada para os pontos */
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.animate-bounce {
  animation: bounce 1.4s ease-in-out infinite both;
}

/* Fade in animation */
.v-enter-active, .v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from, .v-leave-to {
  opacity: 0;
}
</style>