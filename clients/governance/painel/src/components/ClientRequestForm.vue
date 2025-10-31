<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
    <Card class="w-full max-w-5xl shadow-2xl bg-slate-800/90 backdrop-blur-sm border-slate-700">
      <CardHeader class="space-y-1 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-lg pb-4 pt-5 mx-5">
        <CardTitle class="text-2xl font-bold tracking-tight">
          Solicitação de Novo Cliente
        </CardTitle>
        <CardDescription class="text-slate-300 text-sm">
          Preencha o formulário para solicitar a aprovação de um novo cliente confiável no sistema SSI
        </CardDescription>
      </CardHeader>
      
      <CardContent class="pt-6 pb-4 px-6">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- Grid de 2 colunas para campos principais -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Nome da Empresa -->
            <div class="space-y-2">
              <Label for="company_name" class="text-slate-200 font-medium text-sm">
                Nome da Empresa *
              </Label>
              <Input
                id="company_name"
                v-model="formData.company_name"
                type="text"
                placeholder="Ex: Universidade do Reginaldo"
                required
                class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

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

            <!-- Email -->
            <div class="space-y-2">
              <Label for="email" class="text-slate-200 font-medium text-sm">
                E-mail *
              </Label>
              <Input
                id="email"
                v-model="formData.email"
                type="email"
                placeholder="exemplo@empresa.com"
                required
                class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            <!-- Telefone -->
            <div class="space-y-2">
              <Label for="phone" class="text-slate-200 font-medium text-sm">
                Telefone *
              </Label>
              <Input
                id="phone"
                v-model="phoneDisplay"
                type="tel"
                placeholder="(11) 12345-6789"
                required
                maxlength="15"
                class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            <!-- Endereço -->
            <div class="space-y-2">
              <Label for="address" class="text-slate-200 font-medium text-sm">
                Endereço *
              </Label>
              <Input
                id="address"
                v-model="formData.address"
                type="text"
                placeholder="Rua, número - Bairro"
                required
                class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            <!-- Tipo de Cliente -->
            <div class="space-y-2">
              <Label for="client_type" class="text-slate-200 font-medium text-sm">
                Tipo de Cliente *
              </Label>
              <Select v-model="formData.client_type">
                <SelectTrigger class="bg-slate-700/50 border-slate-600 text-white focus:border-blue-500 focus:ring-blue-500/20 cursor-pointer">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent class="bg-slate-700 border-slate-600 text-white">
                  <SelectItem value="issuer" class="focus:bg-slate-600 focus:text-white cursor-pointer">
                    Emissor (Issuer)
                  </SelectItem>
                  <SelectItem value="verifier" class="focus:bg-slate-600 focus:text-white cursor-pointer">
                    Verificador (Verifier)
                  </SelectItem>
                  <SelectItem value="both" class="focus:bg-slate-600 focus:text-white cursor-pointer">
                    Ambos (Issuer + Verifier)
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <!-- Descrição - linha completa -->
          <div class="space-y-2">
            <Label for="description" class="text-slate-200 font-medium text-sm">
              Descrição *
            </Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="Descreva brevemente a empresa e o motivo da solicitação..."
              required
              rows="3"
              class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500/20 resize-none"
            />
          </div>

          <!-- Botões -->
          <div class="flex gap-3 pt-3">
            <Button
              type="submit"
              :disabled="isSubmitting"
              class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium shadow-lg shadow-blue-900/50 transition-all cursor-pointer"
            >
              <span v-if="!isSubmitting">Enviar Solicitação</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Enviando...
              </span>
            </Button>
            <Button
              type="button"
              variant="outline"
              @click="handleReset"
              :disabled="isSubmitting"
              class="bg-slate-700/50 border-slate-500 text-slate-100 hover:bg-slate-600 hover:text-white hover:border-slate-400 transition-all cursor-pointer"
            >
              Limpar
            </Button>
          </div>
        </form>
      </CardContent>

      <CardFooter class="bg-slate-900/50 border-t border-slate-700 py-3">
        <div class="w-full space-y-2">
          <p class="text-xs text-slate-400 text-center">
            <span class="inline-flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              A solicitação será avaliada pela equipe de governança
            </span>
          </p>
          <p class="text-xs text-slate-400 text-center">
            Já tem cadastro? 
            <router-link to="/api-key" class="text-blue-400 hover:text-blue-300 underline">
              Consulte sua chave de API
            </router-link>
          </p>
        </div>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useClientsStore, type ClientRequest } from '../stores/clients'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'

const clientsStore = useClientsStore()

const isSubmitting = ref(false)

const formData = reactive<ClientRequest>({
  company_name: '',
  cnpj: '',
  email: '',
  phone: '',
  address: '',
  client_type: 'issuer',
  description: ''
})

// Computed para CNPJ formatado
const cnpjDisplay = computed({
  get: () => formatCNPJ(formData.cnpj),
  set: (value: string) => {
    formData.cnpj = value.replace(/\D/g, '')
  }
})

// Computed para telefone formatado
const phoneDisplay = computed({
  get: () => formatPhone(formData.phone),
  set: (value: string) => {
    formData.phone = value.replace(/\D/g, '')
  }
})

// Formatar CNPJ: 00.000.000/0000-00
const formatCNPJ = (value: string): string => {
  const numbers = value.replace(/\D/g, '').slice(0, 14) // Limita a 14 dígitos
  if (numbers.length <= 2) return numbers
  if (numbers.length <= 5) return `${numbers.slice(0, 2)}.${numbers.slice(2)}`
  if (numbers.length <= 8) return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(5)}`
  if (numbers.length <= 12) return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(5, 8)}/${numbers.slice(8)}`
  return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(5, 8)}/${numbers.slice(8, 12)}-${numbers.slice(12)}`
}

// Formatar Telefone: (00) 00000-0000 ou (00) 0000-0000
const formatPhone = (value: string): string => {
  const numbers = value.replace(/\D/g, '').slice(0, 11) // Limita a 11 dígitos
  if (numbers.length <= 2) return numbers
  if (numbers.length <= 6) return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`
  if (numbers.length <= 10) return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 6)}-${numbers.slice(6)}`
  return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7)}`
}

const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  
  try {
    const result = await clientsStore.createClient(formData)
    
    if (result) {
      handleReset()
    }
  } finally {
    isSubmitting.value = false
  }
}

const handleReset = () => {
  formData.company_name = ''
  formData.cnpj = ''
  formData.email = ''
  formData.phone = ''
  formData.address = ''
  formData.client_type = 'issuer'
  formData.description = ''
}
</script>

<style scoped>
/* Animações sutis e melhorias visuais */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.space-y-5 > * {
  animation: fadeIn 0.3s ease-out;
}

/* Melhorar o foco dos inputs */
:deep(input:focus),
:deep(textarea:focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Estilizar o select dropdown */
:deep([data-radix-popper-content-wrapper]) {
  z-index: 50;
}
</style>
