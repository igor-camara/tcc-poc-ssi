<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-white mb-2">Ofertas de Credenciais</h2>
        <p class="text-purple-200">Gerencie as ofertas de credenciais recebidas</p>
      </div>
      <div class="flex-shrink-0">
        <Button 
          @click="loadOffers" 
          :disabled="appStore.isLoading"
          class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
        >
          <RefreshCw :class="['w-4 h-4 mr-2', { 'animate-spin': appStore.isLoading }]" />
          Atualizar
        </Button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="flex gap-4 pr-2">
      <div class="flex-1 min-w-0">
        <Input
          v-model="searchTerm"
          placeholder="Buscar por nome da credencial..."
          class="bg-white/20 border-white/30 text-white placeholder:text-purple-200"
        />
      </div>
      <div class="w-48 flex-shrink-0">
        <Select v-model="statusFilter" default-value="all">
          <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-purple-600/50 data-[placeholder]:text-purple-200">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent class="bg-purple-900/95 backdrop-blur-md border-white/30 shadow-xl">
            <SelectGroup>
              <SelectItem
                v-for="option in statusOptions"
                :key="option.value"
                :value="option.value"
                class="!text-white hover:!bg-purple-600/60 focus:!bg-purple-600/70 focus:!text-white data-[highlighted]:bg-purple-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
              >
                {{ option.label }}
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Offers List -->
    <div class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-purple-600 scrollbar-track-white/10">
      <!-- Loading State -->
      <div v-if="appStore.isLoading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600"></div>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredOffers.length === 0" 
        class="p-12 text-center"
      >
        <div class="w-20 h-20 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Award class="w-10 h-10 text-purple-600" />
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Nenhuma oferta encontrada</h3>
        <p class="text-purple-200 mb-4">
          {{ searchTerm || (statusFilter && statusFilter !== 'all') ? 'Nenhuma oferta encontrada com os filtros aplicados' : 'Você não tem ofertas de credenciais pendentes no momento' }}
        </p>
        <Button 
          v-if="!searchTerm && (!statusFilter || statusFilter === 'all')"
          @click="loadOffers" 
          class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
        >
          <RefreshCw class="w-4 h-4 mr-2" />
          Verificar novamente
        </Button>
      </div>

      <!-- Actual Offers -->
      <div v-if="!appStore.isLoading && filteredOffers.length > 0">
        <div
          v-for="offer in filteredOffers"
          :key="offer.cred_ex_id"
          class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4 flex-1">
              <!-- Offer Icon -->
              <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                <Award class="w-6 h-6 text-white" />
              </div>
              
              <!-- Offer Info -->
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-semibold text-white">Oferta de Credencial</h3>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      getStatusClass(offer.state)
                    ]"
                  >
                    {{ getStatusLabel(offer.state) }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 gap-2 text-sm">
                  <div>
                    <span class="text-purple-300">Exchange ID: </span>
                    <span class="text-white font-mono text-xs">{{ offer.cred_ex_id.substring(0, 20) }}...</span>
                  </div>
                  <div>
                    <span class="text-purple-300">Connection ID: </span>
                    <span class="text-white font-mono text-xs">{{ offer.connection_id.substring(0, 20) }}...</span>
                  </div>
                  <div>
                    <span class="text-purple-300">Nome da Credencial: </span>
                    <span class="text-white font-mono text-xs break-all">{{ getSchemaName(offer.schema_id) }}</span>
                  </div>
                  <div>
                    <span class="text-purple-300">Recebido em: </span>
                    <span class="text-white">{{ formatDate(offer.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center space-x-2 ml-4">
              <Button
                v-if="offer.state === 'offer-received'"
                @click="acceptOfferConfirm(offer)"
                :disabled="acceptingOffer === offer.cred_ex_id"
                class="bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer"
                title="Aceitar Oferta"
              >
                <CheckCircle v-if="acceptingOffer !== offer.cred_ex_id" class="w-4 h-4 mr-2" />
                <div v-else class="w-4 h-4 mr-2 animate-spin rounded-full border-t-2 border-b-2 border-white"></div>
                Aceitar
              </Button>
              <Button
                @click="viewOfferDetails(offer)"
                variant="ghost"
                size="sm"
                class="text-purple-200 hover:text-white hover:bg-white/10 cursor-pointer"
                title="Ver Detalhes"
              >
                <Eye class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Offer Details Modal -->
    <div
      v-if="showDetailsModal && selectedOffer"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeDetailsModal"
    >
      <div class="bg-gradient-to-br from-purple-900/90 to-purple-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-white">Detalhes da Oferta</h3>
          <button
            @click="closeDetailsModal"
            class="text-white hover:text-purple-300 transition-colors cursor-pointer"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="space-y-4">
          <div class="bg-white/10 rounded-lg p-4 space-y-3">
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Status:</span>
              <span :class="getStatusClass(selectedOffer.state)" class="px-2 py-1 text-xs rounded-full">
                {{ getStatusLabel(selectedOffer.state) }}
              </span>
            </div>
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Criado em:</span>
              <span class="text-white">{{ formatDate(selectedOffer.created_at) }}</span>
            </div>
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Atualizado em:</span>
              <span class="text-white">{{ formatDate(selectedOffer.updated_at) }}</span>
            </div>
          </div>
          
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Exchange ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedOffer.cred_ex_id }}
            </code>
          </div>
          
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Connection ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedOffer.connection_id }}
            </code>
          </div>
          
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Schema ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedOffer.schema_id }}
            </code>
          </div>
          
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Credential Definition ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedOffer.cred_def_id }}
            </code>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end space-x-3">
          <Button
            @click="closeDetailsModal"
            variant="ghost"
            class="text-white hover:bg-white/10 hover:text-white cursor-pointer"
          >
            Fechar
          </Button>
          <Button
            v-if="selectedOffer.state === 'offer-received'"
            @click="acceptOfferFromModal"
            :disabled="acceptingOffer === selectedOffer.cred_ex_id"
            class="bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer"
          >
            <CheckCircle v-if="acceptingOffer !== selectedOffer.cred_ex_id" class="w-4 h-4 mr-2" />
            <div v-else class="w-4 h-4 mr-2 animate-spin rounded-full border-t-2 border-b-2 border-white"></div>
            Aceitar Oferta
          </Button>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div
      v-if="showConfirmModal && offerToAccept"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeConfirmModal"
    >
      <div class="bg-gradient-to-br from-purple-900/90 to-purple-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-md">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-12 h-12 bg-indigo-600/20 rounded-full flex items-center justify-center">
            <CheckCircle class="w-6 h-6 text-indigo-400" />
          </div>
          <h3 class="text-xl font-bold text-white">Aceitar Oferta de Credencial</h3>
        </div>
        
        <p class="text-purple-200 mb-6">
          Tem certeza de que deseja aceitar esta oferta de credencial? Esta ação não pode ser desfeita.
        </p>
        
        <div class="bg-white/10 rounded-lg p-3 mb-6">
          <div class="text-sm">
            <span class="text-purple-300">Schema: </span>
            <span class="text-white">{{ getSchemaName(offerToAccept.schema_id) }}</span>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3">
          <Button
            @click="closeConfirmModal"
            variant="ghost"
            class="text-white hover:bg-white/10 hover:text-white cursor-pointer"
            :disabled="acceptingOffer !== null"
          >
            Cancelar
          </Button>
          <Button
            @click="acceptOfferAction"
            :disabled="acceptingOffer !== null"
            class="bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer"
          >
            <CheckCircle v-if="acceptingOffer === null" class="w-4 h-4 mr-2" />
            <div v-else class="w-4 h-4 mr-2 animate-spin rounded-full border-t-2 border-b-2 border-white"></div>
            Confirmar
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeMount } from 'vue'
import { useCredentialStore, type CredentialOffer } from '@/stores/credential'
import { useAppStore } from '@/stores/app'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { RefreshCw, Award, Eye, CheckCircle, X } from 'lucide-vue-next'

const credentialStore = useCredentialStore()
const appStore = useAppStore()

const showDetailsModal = ref(false)
const selectedOffer = ref<CredentialOffer | null>(null)
const showConfirmModal = ref(false)
const offerToAccept = ref<CredentialOffer | null>(null)
const acceptingOffer = ref<string | null>(null)
const searchTerm = ref('')
const statusFilter = ref('all')

// Status options for the filter
const statusOptions = [
  { value: 'all', label: 'Todos os status' },
  { value: 'offer-received', label: 'Oferta Recebida' },
  { value: 'request-sent', label: 'Requisição Enviada' },
  { value: 'credential-received', label: 'Credencial Recebida' },
  { value: 'done', label: 'Concluído' },
]

// Computed property to filter offers by credential name and status
const filteredOffers = computed(() => {
  let filtered = credentialStore.offers
  
  // Filter by status
  if (statusFilter.value && statusFilter.value !== 'all') {
    filtered = filtered.filter(offer => offer.state === statusFilter.value)
  }
  
  // Filter by search term
  if (searchTerm.value.trim()) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(offer => {
      const schemaName = getSchemaName(offer.schema_id).toLowerCase()
      return schemaName.includes(search)
    })
  }
  
  return filtered
})

onBeforeMount(() => {
  loadOffers()
})

async function loadOffers() {
  await credentialStore.fetchOffers()
}

function viewOfferDetails(offer: CredentialOffer) {
  selectedOffer.value = offer
  showDetailsModal.value = true
}

function closeDetailsModal() {
  showDetailsModal.value = false
  selectedOffer.value = null
}

function acceptOfferConfirm(offer: CredentialOffer) {
  offerToAccept.value = offer
  showConfirmModal.value = true
}

function closeConfirmModal() {
  showConfirmModal.value = false
  offerToAccept.value = null
}

async function acceptOfferAction() {
  if (!offerToAccept.value) return
  
  acceptingOffer.value = offerToAccept.value.cred_ex_id
  
  try {
    await credentialStore.acceptOffer(offerToAccept.value.cred_ex_id)
    closeConfirmModal()
  } finally {
    acceptingOffer.value = null
  }
}

async function acceptOfferFromModal() {
  if (!selectedOffer.value) return
  
  acceptingOffer.value = selectedOffer.value.cred_ex_id
  
  try {
    await credentialStore.acceptOffer(selectedOffer.value.cred_ex_id)
    closeDetailsModal()
  } finally {
    acceptingOffer.value = null
  }
}

function getStatusClass(state: string): string {
  const statusMap: Record<string, string> = {
    'offer-received': 'bg-blue-600/80 text-white',
    'request-sent': 'bg-yellow-600/80 text-white',
    'credential-received': 'bg-green-600/80 text-white',
    'done': 'bg-green-700/80 text-white',
  }
  return statusMap[state] || 'bg-gray-600/80 text-white'
}

function getStatusLabel(state: string): string {
  const labelMap: Record<string, string> = {
    'offer-received': 'Oferta Recebida',
    'request-sent': 'Requisição Enviada',
    'credential-received': 'Credencial Recebida',
    'done': 'Concluído',
  }
  return labelMap[state] || state
}

function getSchemaName(schemaId: string): string {
  const parts = schemaId.split(':')
  if (parts.length >= 3 && parts[2]) {
    return parts[2]
  }
  return schemaId
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
</script>

<style scoped>
/* Estilo customizado para o scrollbar */
.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgb(147, 51, 234);
  border-radius: 4px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgb(126, 34, 206);
}
</style>
