<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
    <Card class="w-full max-w-md shadow-2xl bg-slate-800/90 backdrop-blur-sm border-slate-700">
      <CardHeader class="space-y-1 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-lg mx-5 pb-6 pt-8">
        <CardTitle class="text-3xl font-bold tracking-tight text-center">
          Bem-vindo
        </CardTitle>
        <CardDescription class="text-slate-300 text-center text-sm">
          Faça login para acessar o painel de governança
        </CardDescription>
      </CardHeader>
      
      <CardContent class="pt-8 pb-6 px-8">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Username -->
          <div class="space-y-2">
            <Label for="username" class="text-slate-200 font-medium text-sm">
              Nome de Usuário
            </Label>
            <Input
              id="username"
              v-model="credentials.username"
              type="text"
              placeholder="Digite seu nome de usuário"
              required
              autocomplete="username"
              class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20 h-11"
            />
          </div>

          <!-- TOTP Code -->
          <div class="space-y-3">
            <Label for="totp_code" class="text-slate-200 font-medium text-sm">
              Código TOTP
            </Label>
            <OTPInput 
              v-model="credentials.totp_code"
              :length="6"
              @complete="handleOTPComplete"
            />
            <p class="text-xs text-slate-400 text-center">
              Digite o código de 6 dígitos do seu aplicativo autenticador
            </p>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-6 text-base transition-all duration-200 shadow-lg hover:shadow-blue-500/20 cursor-pointer"
            :disabled="!isFormValid"
          >
            <span v-if="!isLoading">Entrar</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Autenticando...
            </span>
          </Button>
        </form>
      </CardContent>

      <CardFooter class="flex flex-col space-y-2 text-center text-xs text-slate-400 pb-6">
        <p>Sistema de Identidade Soberana Auto-Soberana (SSI)</p>
        <p>Painel de Governança</p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { OTPInput } from '@/components/ui/otp-input'

// Stores
const authStore = useAuthStore()
const appStore = useAppStore()

// Emit para notificar o componente pai sobre login bem-sucedido
const emit = defineEmits<{
  loginSuccess: []
}>()

// State
const credentials = ref({
  username: '',
  totp_code: ''
})

const isLoading = computed(() => appStore.isLoading)

const isFormValid = computed(() => {
  return credentials.value.username.trim().length > 0 && 
         credentials.value.totp_code.length === 6
})

// Methods
async function handleLogin() {
  if (!isFormValid.value) return

  const success = await authStore.login({
    username: credentials.value.username,
    totp_code: credentials.value.totp_code
  })

  if (success) {
    emit('loginSuccess')
  }
}

function handleOTPComplete(value: string) {
  credentials.value.totp_code = value
  // Opcional: auto-submit quando o código estiver completo
  // handleLogin()
}
</script>

<style scoped>
/* Animações suaves */
input:focus {
  transition: all 0.2s ease-in-out;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
