<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
    <Card class="w-full max-w-2xl shadow-2xl bg-slate-800/90 backdrop-blur-sm border-slate-700">
      <CardHeader class="space-y-1 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-lg pb-4 pt-5 mx-5">
        <CardTitle class="text-2xl font-bold tracking-tight">
          Consultar Chave de API
        </CardTitle>
        <CardDescription class="text-slate-300 text-sm">
          Informe o CNPJ da sua empresa para consultar a chave de API
        </CardDescription>
      </CardHeader>
      
      <CardContent class="pt-6 pb-4 px-6">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- CNPJ -->
          <div class="space-y-2">
            <Label for="cnpj" class="text-slate-200 font-medium text-sm">
              CNPJ *
            </Label>
            <Input
              id="cnpj"
              v-model="cnpjDisplay"
              type="text"
              placeholder="00.000.000/0000-00"
              required
              maxlength="18"
              class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
            />
          </div>

          <!-- Resultado da Consulta -->
          <div v-if="clientData" class="space-y-4 p-5 bg-slate-700/30 rounded-lg border border-slate-600">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-white mb-3">
                  Dados do Cliente
                </h3>
                
                <div class="space-y-3">
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">Nome:</span>
                    <span class="text-slate-200 text-sm font-medium">{{ clientData.company_name }}</span>
                  </div>
                  
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">CNPJ:</span>
                    <span class="text-slate-200 text-sm font-medium">{{ formatCNPJ(clientData.cnpj) }}</span>
                  </div>
                  
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">E-mail:</span>
                    <span class="text-slate-200 text-sm font-medium">{{ clientData.email }}</span>
                  </div>
                  
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">Telefone:</span>
                    <span class="text-slate-200 text-sm font-medium">{{ formatPhone(clientData.phone) }}</span>
                  </div>
                  
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">Status:</span>
                    <span 
                      class="text-sm font-semibold inline-flex items-center gap-1"
                      :class="getStatusClass(clientData.status)"
                    >
                      <span class="w-2 h-2 rounded-full" :class="getStatusDotClass(clientData.status)"></span>
                      {{ getStatusLabel(clientData.status) }}
                    </span>
                  </div>
                  
                  <div class="grid grid-cols-[140px_1fr] gap-2">
                    <span class="text-slate-400 text-sm">Tipo:</span>
                    <span class="text-slate-200 text-sm font-medium">{{ getClientTypeLabel(clientData.client_type) }}</span>
                  </div>
                  
                  <div class="pt-3 border-t border-slate-600">
                    <div class="space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-slate-400 text-sm">Chave de API:</span>
                        <Button
                          v-if="clientData.api_key"
                          type="button"
                          @click="copyApiKey"
                          size="sm"
                          variant="outline"
                          class="shrink-0 bg-slate-600 hover:bg-slate-500 text-white border-slate-500 cursor-pointer"
                        >
                          {{ copied ? '✓ Copiado' : 'Copiar' }}
                        </Button>
                      </div>
                      <div v-if="clientData.api_key">
                        <code class="text-green-400 text-sm font-mono bg-slate-900/50 px-3 py-2 rounded block break-all">
                          {{ clientData.api_key }}
                        </code>
                      </div>
                      <div v-else class="flex items-center gap-2">
                        <span class="text-red-400 text-sm">Não disponível</span>
                        <span class="text-slate-500 text-xs">(Cliente precisa ser aprovado)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Mensagem de Erro -->
          <div v-if="errorMessage" class="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p class="text-red-400 text-sm">{{ errorMessage }}</p>
          </div>

          <!-- Botão de Consulta -->
          <div class="flex gap-3 pt-2">
            <Button
              type="submit"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium cursor-pointer"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Consultando...
              </span>
              <span v-else>Consultar</span>
            </Button>
            
            <Button
              v-if="clientData"
              type="button"
              @click="resetForm"
              variant="outline"
              class="bg-slate-700 hover:bg-slate-600 text-white border-slate-600 cursor-pointer"
            >
              Nova Consulta
            </Button>
          </div>
        </form>
      </CardContent>

      <CardFooter class="bg-slate-700/30 border-t border-slate-700 text-center text-slate-400 text-xs py-3">
        <p class="w-full">
          Não tem cadastro? 
          <router-link to="/form" class="text-blue-400 hover:text-blue-300 underline">
            Solicite aqui
          </router-link>
        </p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Button } from './ui/button'
import axiosInstance from '../lib/axios'

interface ClientData {
  id: string
  company_name: string
  cnpj: string
  email: string
  phone: string
  address: string
  client_type: string
  description: string
  status: string
  api_key: string | null
  created_at: string
  updated_at: string
}

const cnpjDisplay = ref('')
const clientData = ref<ClientData | null>(null)
const errorMessage = ref('')
const isLoading = ref(false)
const copied = ref(false)

// Computed para CNPJ limpo (apenas números)
const cnpjClean = computed(() => {
  return cnpjDisplay.value.replace(/\D/g, '')
})

// Função para formatar CNPJ
const formatCNPJInput = (value: string) => {
  const clean = value.replace(/\D/g, '')
  if (clean.length <= 14) {
    return clean
      .replace(/(\d{2})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1/$2')
      .replace(/(\d{4})(\d)/, '$1-$2')
  }
  return value.substring(0, 18)
}

// Watch para formatar CNPJ automaticamente
watch(cnpjDisplay, (newValue) => {
  const formatted = formatCNPJInput(newValue)
  if (formatted !== newValue) {
    cnpjDisplay.value = formatted
  }
})

const handleSubmit = async () => {
  if (cnpjClean.value.length !== 14) {
    errorMessage.value = 'CNPJ inválido. Digite um CNPJ com 14 dígitos.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  clientData.value = null

  try {
    const response = await axiosInstance.get(`/clients/cnpj/${cnpjClean.value}`)
    
    if (response.data.code === 'SUCCESS') {
      clientData.value = response.data.data
    } else {
      errorMessage.value = 'Erro ao consultar cliente.'
    }
  } catch (error: any) {
    if (error.response?.status === 404) {
      errorMessage.value = 'Cliente não encontrado com este CNPJ.'
    } else {
      errorMessage.value = 'Erro ao consultar cliente. Tente novamente.'
    }
    console.error('Erro ao consultar cliente:', error)
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  cnpjDisplay.value = ''
  clientData.value = null
  errorMessage.value = ''
  copied.value = false
}

const copyApiKey = async () => {
  if (clientData.value?.api_key) {
    try {
      await navigator.clipboard.writeText(clientData.value.api_key)
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    } catch (error) {
      console.error('Erro ao copiar API key:', error)
    }
  }
}

const formatCNPJ = (cnpj: string) => {
  return cnpj
    .replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
}

const formatPhone = (phone: string) => {
  const clean = phone.replace(/\D/g, '')
  if (clean.length === 11) {
    return clean.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
  }
  return phone
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'pendente': 'Pendente',
    'aprovado': 'Aprovado',
    'rejeitado': 'Rejeitado'
  }
  return labels[status] || status
}

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'pendente': 'text-yellow-400',
    'aprovado': 'text-green-400',
    'rejeitado': 'text-red-400'
  }
  return classes[status] || 'text-slate-400'
}

const getStatusDotClass = (status: string) => {
  const classes: Record<string, string> = {
    'pendente': 'bg-yellow-400',
    'aprovado': 'bg-green-400',
    'rejeitado': 'bg-red-400'
  }
  return classes[status] || 'bg-slate-400'
}

const getClientTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'issuer': 'Emissor',
    'verifier': 'Verificador',
    'both': 'Ambos (Emissor e Verificador)'
  }
  return labels[type] || type
}
</script>
