<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useLedgerStore } from '@/stores'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Key, CheckCircle2, AlertCircle } from 'lucide-vue-next'

const ledgerStore = useLedgerStore()
const apiKey = ref('')
const error = ref('')
const success = ref('')

onMounted(async () => {
  try {
    await ledgerStore.checkKey()
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Erro ao verificar chave do ledger'
  }
})

const handleRegisterKey = async () => {
  if (!apiKey.value.trim()) {
    error.value = 'Por favor, insira uma API key'
    return
  }

  error.value = ''
  success.value = ''

  try {
    await ledgerStore.registerKey(apiKey.value)
    success.value = 'API Key configurada com sucesso!'
    apiKey.value = ''
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Erro ao registrar API key'
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 bg-blue-600/20 rounded-lg flex items-center justify-center">
            <Key class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-white">Chave de Governança do Ledger</h2>
        </div>
        <p class="text-blue-100">
          {{ ledgerStore.message || 'Configure sua API key de governança para interagir com o ledger' }}
        </p>
      </div>
    </div>

    <!-- Configuration Card -->
    <div class="bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 p-6 space-y-4">
      <!-- Status Badge -->
      <div v-if="ledgerStore.isConfigured" class="flex items-center gap-2 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
        <CheckCircle2 class="w-5 h-5 text-green-400" />
        <span class="text-green-300 font-medium">API Key está configurada e pronta para uso</span>
      </div>

      <!-- Input Section -->
      <div class="space-y-3">
        <label for="api-key" class="text-sm font-medium text-blue-200 block">
          API Key
        </label>
        <div class="flex gap-3">
          <Input
            id="api-key"
            v-model="apiKey"
            type="password"
            placeholder="Insira sua API key de governança"
            :disabled="ledgerStore.isConfigured || ledgerStore.isLoading"
            class="flex-1 bg-white/10 border-white/20 text-white placeholder:text-blue-100 disabled:opacity-50 disabled:cursor-not-allowed focus:border-blue-500 focus:ring-blue-500/50"
            @keyup.enter="handleRegisterKey"
          />
          <Button
            @click="handleRegisterKey"
            :disabled="ledgerStore.isConfigured || ledgerStore.isLoading || !apiKey.trim()"
            class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed px-6"
          >
            {{ ledgerStore.isLoading ? 'Registrando...' : 'Registrar' }}
          </Button>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="success" class="flex items-start gap-2 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
        <CheckCircle2 class="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
        <p class="text-sm text-green-300">{{ success }}</p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="flex items-start gap-2 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
        <AlertCircle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
        <p class="text-sm text-red-300">{{ error }}</p>
      </div>

      <!-- Info Box -->
      <div class="p-4 bg-blue-600/10 border border-blue-500/30 rounded-lg">
        <p class="text-sm text-blue-200">
          <strong class="text-blue-100">Nota:</strong> A API Key de governança é necessária para realizar operações no ledger. 
          Uma vez configurada, ela não poderá ser alterada através desta interface por motivos de segurança.
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="ledgerStore.isLoading && !apiKey" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600"></div>
    </div>
  </div>
</template>
