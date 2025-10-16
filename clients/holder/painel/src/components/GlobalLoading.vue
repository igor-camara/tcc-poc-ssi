<template>
   <Teleport to="body">
      <Transition name="loading" appear>
         <div 
            v-if="appStore.isLoading"
            class="fixed inset-0 z-[9998] flex items-center justify-center bg-black/50 backdrop-blur-sm"
            >
            <div class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-8 flex flex-col items-center space-y-4">
               <!-- Spinner -->
               <div class="relative">
                  <div class="w-16 h-16 border-4 border-purple-600/30 rounded-full"></div>
                  <div class="absolute inset-0 w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
               </div>
               <!-- Loading Text -->
               <div class="text-center">
                  <h3 class="text-lg font-semibold text-white mb-1">Carregando...</h3>
                  <p class="text-purple-200 text-sm">Aguarde um momento</p>
               </div>
               <!-- Animated dots -->
               <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                  <div class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                  <div class="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
               </div>
            </div>
         </div>
      </Transition>
   </Teleport>
</template>


<script setup lang="ts">
import { useAppStore } from '@/stores'

const appStore = useAppStore()
</script>

<style scoped>
.loading-enter-active,
.loading-leave-active {
  transition: all 0.3s ease;
}

.loading-enter-from,
.loading-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}

.loading-enter-to,
.loading-leave-from {
  opacity: 1;
  backdrop-filter: blur(4px);
}

/* Custom bounce animation with different delays */
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}
</style>