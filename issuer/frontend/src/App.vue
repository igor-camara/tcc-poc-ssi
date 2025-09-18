<template>
  <div id="app" class="bg-white">
    <div v-if="isInitializing" class="min-h-screen flex items-center justify-center bg-gray-50">
      <div class="flex flex-col items-center">
        <svg class="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-gray-600">Carregando...</p>
      </div>
    </div>
    
    
    <transition name="fade" mode="out-in">
      <AuthLayout 
        v-if="!isInitializing && !isAuthenticated" 
        @auth-success="handleAuthSuccess"
      />
      <Dashboard 
        v-else-if="!isInitializing && isAuthenticated"
      />
    </transition>
    
    <!-- Global Loading Spinner -->
    <LoadingSpinner />
    
    <!-- Global Alert Container -->
    <AlertContainer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from './composables/useAuth'
import { useTheme } from './composables/useTheme'
import AuthLayout from './components/AuthLayout.vue'
import Dashboard from './components/Dashboard.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'
import AlertContainer from './components/AlertContainer.vue'

// Composables
const { isAuthenticated, checkAuth } = useAuth()
const { initTheme } = useTheme()

// Estado da aplicação
const isInitializing = ref(true)

// Lifecycle
onMounted(async () => {
  // Inicializar tema
  initTheme()
  
  // Verificar se o usuário já está autenticado
  await checkAuth()
  isInitializing.value = false
})

// Métodos
const handleAuthSuccess = () => {
  // Já está sendo gerenciado pelo estado reativo do useAuth
  console.log('Usuário autenticado com sucesso!')
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
