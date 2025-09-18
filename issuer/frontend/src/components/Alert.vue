<template>
  <div
    :class="alertClasses"
    class="relative flex w-full rounded-lg border px-4 py-3 text-sm shadow-sm transition-all duration-300 ease-in-out"
    :style="{ opacity: isVisible ? 1 : 0, transform: isVisible ? 'translateY(0)' : 'translateY(-10px)' }"
  >
    <!-- Ícone -->
    <div class="flex-shrink-0 pr-3">
      <!-- Success Icon -->
      <svg v-if="variant === 'success'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
      </svg>
      
      <!-- Warning Icon -->
      <svg v-else-if="variant === 'warning'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
      </svg>
      
      <!-- Error Icon -->
      <svg v-else-if="variant === 'error'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
      
      <!-- Info Icon (default) -->
      <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    </div>
    
    <!-- Conteúdo -->
    <div class="flex-1">
      <h5 v-if="title" :class="titleClasses" class="mb-1 font-medium leading-none tracking-tight">
        {{ title }}
      </h5>
      <div :class="descriptionClasses" class="text-sm opacity-90">
        {{ description }}
      </div>
    </div>
    
    <!-- Botão de fechar (opcional) -->
    <button
      v-if="closable"
      @click="handleClose"
      class="flex-shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity hover:cursor-pointer"
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  variant: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'warning', 'error', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    required: true
  },
  closable: {
    type: Boolean,
    default: true
  },
  autoClose: {
    type: Boolean,
    default: true
  },
  duration: {
    type: Number,
    default: 3000 // 3 segundos
  }
})

// Emits
const emit = defineEmits(['close'])

// Estado local
const isVisible = ref(true)
let autoCloseTimer = null

// Computed
const alertClasses = computed(() => {
  const baseClasses = {
    success: 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-300',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-300',
    error: 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-300',
    info: 'border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300'
  }
  
  return baseClasses[props.variant] || baseClasses.info
})

const titleClasses = computed(() => {
  const titleColors = {
    success: 'text-green-800 dark:text-green-300',
    warning: 'text-yellow-800 dark:text-yellow-300',
    error: 'text-red-800 dark:text-red-300',
    info: 'text-blue-800 dark:text-blue-300'
  }
  
  return titleColors[props.variant] || titleColors.info
})

const descriptionClasses = computed(() => {
  const descriptionColors = {
    success: 'text-green-700 dark:text-green-400',
    warning: 'text-yellow-700 dark:text-yellow-400',
    error: 'text-red-700 dark:text-red-400',
    info: 'text-blue-700 dark:text-blue-400'
  }
  
  return descriptionColors[props.variant] || descriptionColors.info
})

// Métodos
const handleClose = () => {
  isVisible.value = false
  setTimeout(() => {
    emit('close')
  }, 300) // Aguarda a animação de fade-out
}

const setupAutoClose = () => {
  if (props.autoClose && props.duration > 0) {
    autoCloseTimer = setTimeout(() => {
      handleClose()
    }, props.duration)
  }
}

// Lifecycle
onMounted(() => {
  setupAutoClose()
})

onUnmounted(() => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
  }
})
</script>

<style scoped>
/* Animações personalizadas para entrada/saída */
.v-enter-active, .v-leave-active {
  transition: all 0.3s ease;
}

.v-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.v-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>