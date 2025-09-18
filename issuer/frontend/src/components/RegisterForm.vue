<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4">
    <div class="w-full max-w-md lg:max-w-lg xl:max-w-xl">
      <!-- Card Container -->
      <div class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 dark:border-slate-700/20 p-8 lg:p-12">
        <!-- Header -->
        <div class="text-center mb-8 lg:mb-10">
          <div class="mx-auto w-12 h-12 lg:w-16 lg:h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center mb-4 lg:mb-6">
            <svg class="w-6 h-6 lg:w-8 lg:h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
          </div>
          <h2 class="text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white mb-2">
            Criar nova conta
          </h2>
          <p class="text-slate-600 dark:text-slate-300 text-sm lg:text-base">
            Preencha seus dados para começar
          </p>
        </div>
        
        <!-- Form -->
        <form class="space-y-5 lg:space-y-6" @submit.prevent="handleSubmit">
          <!-- Name Field -->
          <div class="space-y-3">
            <label for="name" class="text-sm lg:text-base font-medium text-slate-700 dark:text-slate-300 block">
              Nome completo
            </label>
            <div class="relative">
              <input
                id="name"
                name="name"
                type="text"
                autocomplete="name"
                required
                v-model="form.name"
                class="w-full px-4 lg:px-5 py-3 lg:py-4 text-base lg:text-lg rounded-xl border border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-700/50 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 focus:border-transparent transition-all duration-200 hover:border-slate-300 dark:hover:border-slate-500"
                placeholder="Seu nome completo"
              />
              <div class="absolute inset-y-0 right-0 pr-3 lg:pr-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 lg:h-6 lg:w-6 text-slate-400 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
            </div>
            <span v-if="errors.name" class="text-red-500 dark:text-red-400 text-sm lg:text-base font-medium">{{ errors.name }}</span>
          </div>

          <!-- Email Field -->
          <div class="space-y-3">
            <label for="email" class="text-sm lg:text-base font-medium text-slate-700 dark:text-slate-300 block">
              Email
            </label>
            <div class="relative">
              <input
                id="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                v-model="form.email"
                class="w-full px-4 lg:px-5 py-3 lg:py-4 text-base lg:text-lg rounded-xl border border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-700/50 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 focus:border-transparent transition-all duration-200 hover:border-slate-300 dark:hover:border-slate-500"
                placeholder="seu@email.com"
              />
              <div class="absolute inset-y-0 right-0 pr-3 lg:pr-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 lg:h-6 lg:w-6 text-slate-400 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                </svg>
              </div>
            </div>
            <span v-if="errors.email" class="text-red-500 dark:text-red-400 text-sm lg:text-base font-medium">{{ errors.email }}</span>
          </div>
          
          <!-- Password Field -->
          <div class="space-y-3">
            <label for="password" class="text-sm font-medium text-slate-700 dark:text-slate-300 block">
              Senha
            </label>
            <div class="relative">
              <input
                id="password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                v-model="form.password"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-700/50 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 focus:border-transparent transition-all duration-200 hover:border-slate-300 dark:hover:border-slate-500"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg v-if="!showPassword" class="h-5 w-5 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="h-5 w-5 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
              </button>
            </div>
            <span v-if="errors.password" class="text-red-500 text-sm font-medium">{{ errors.password }}</span>
          </div>

          <!-- Confirm Password Field -->
          <div class="space-y-3">
            <label for="confirmPassword" class="text-sm font-medium text-slate-700 dark:text-slate-300 block">
              Confirmar senha
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                name="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                v-model="form.confirmPassword"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-700/50 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 focus:border-transparent transition-all duration-200 hover:border-slate-300 dark:hover:border-slate-500"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg v-if="!showConfirmPassword" class="h-5 w-5 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="h-5 w-5 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
              </button>
            </div>
            <span v-if="errors.confirmPassword" class="text-red-500 dark:text-red-400 text-sm font-medium">{{ errors.confirmPassword }}</span>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400 dark:text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="text-red-700 dark:text-red-300 text-sm font-medium">{{ error }}</span>
            </div>
          </div>

          <!-- Submit Button -->
                    <button
            type="submit"
            :disabled="appStore.isLoading"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            <div class="flex items-center justify-center">
              <svg v-if="appStore.isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ appStore.isLoading ? 'Criando conta...' : 'Criar conta' }}
            </div>
          </button>
        </form>

        <!-- Footer -->
        <div class="mt-6 text-center">
          <p class="text-slate-600 dark:text-slate-300 text-sm">
            Já tem uma conta?
            <button
              @click="$emit('switch-to-login')"
              class="font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-500 dark:hover:text-purple-300 hover:cursor-pointer transition-colors duration-200 ml-1"
            >
              Entrar
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useAppStore } from '../composables/useAppStore'

const emit = defineEmits(['switch-to-login', 'register-success'])

const { register, error, clearError } = useAuth()
const appStore = useAppStore()

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const validateForm = () => {
  let isValid = true
  
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  
  // Validar nome
  if (!form.name.trim()) {
    errors.name = 'Nome é obrigatório'
    isValid = false
  } else if (form.name.trim().length < 2) {
    errors.name = 'Nome deve ter pelo menos 2 caracteres'
    isValid = false
  }
  
  // Validar email
  if (!form.email) {
    errors.email = 'Email é obrigatório'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Email inválido'
    isValid = false
  }
  
  // Validar senha
  if (!form.password) {
    errors.password = 'Senha é obrigatória'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Senha deve ter pelo menos 6 caracteres'
    isValid = false
  }
  
  // Validar confirmação de senha
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Confirmação de senha é obrigatória'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Senhas não coincidem'
    isValid = false
  }
  
  return isValid
}

const handleSubmit = async () => {
  clearError()
  
  if (!validateForm()) {
    return
  }
  
  const fullName = form.name.trim()
  const spaceIndex = fullName.indexOf(' ')
  const firstName = spaceIndex > -1 ? fullName.substring(0, spaceIndex) : fullName
  const lastName = spaceIndex > -1 ? fullName.substring(spaceIndex + 1) : ''
  
  const userData = {
    first_name: firstName,
    last_name: lastName,
    email: form.email,
    password: form.password
  }

  console.log(userData)
  
  const result = await register(userData)
  
  if (result.success) {
    // Emit evento de sucesso para componente pai
    emit('register-success')
  }
}
</script>