<template>
  <div class="auth-layout relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50"></div>
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <!-- Floating Elements -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
      <div class="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      <div class="absolute -bottom-20 left-40 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
    </div>
    
    <!-- Content -->
    <div class="relative z-10">
      <transition name="slide-fade" mode="out-in">
        <LoginForm
          v-if="currentView === 'login'"
          @switch-to-register="switchToRegister"
          @login-success="handleAuthSuccess"
        />
        <RegisterForm
          v-else
          @switch-to-login="switchToLogin"
          @register-success="handleAuthSuccess"
        />
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

// Props e emits
const emit = defineEmits(['auth-success'])

// Estado do componente
const currentView = ref('login')

// Métodos
const handleAuthSuccess = () => {
  // Emit evento para o componente pai
  emit('auth-success')
}

const switchToRegister = () => {
  currentView.value = 'register'
}

const switchToLogin = () => {
  currentView.value = 'login'
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
}

/* Grid Pattern Background */
.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

/* Smooth transitions */
.slide-fade-enter-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}

/* Blob animations */
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .slide-fade-enter-from {
    transform: translateY(20px);
  }
  
  .slide-fade-leave-to {
    transform: translateY(-20px);
  }
}
</style>