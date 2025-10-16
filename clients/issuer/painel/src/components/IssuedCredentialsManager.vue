<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4 pr-2">
      <div class="flex-1">
        <h2 class="text-2xl font-bold text-white mb-2">Emissão de Certificados</h2>
        <p class="text-amber-200">Gerencie as credenciais emitidas e envie novas ofertas</p>
      </div>
      <div class="flex-shrink-0">
        <Button 
          @click="openOfferModal" 
          class="bg-amber-600 hover:bg-amber-700 text-white cursor-pointer"
        >
          <Plus class="w-4 h-4 mr-2" />
          Nova Oferta de Credencial
        </Button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="flex gap-4 pr-2">
      <div class="flex-1 min-w-0">
        <Input
          v-model="searchTerm"
          placeholder="Buscar por nome de credencial ou matrícula..."
          class="bg-white/20 border-white/30 text-white placeholder:text-amber-200"
        />
      </div>
      <div class="w-56 flex-shrink-0">
        <Select v-model="statusFilter" default-value="all">
          <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-amber-600/50 data-[placeholder]:text-amber-200">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent class="bg-amber-900/95 backdrop-blur-md border-white/30 shadow-xl">
            <SelectGroup>
              <SelectItem
                v-for="option in statusOptions"
                :key="option.value"
                :value="option.value"
                class="!text-white hover:!bg-amber-600/60 focus:!bg-amber-600/70 focus:!text-white data-[highlighted]:bg-amber-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
              >
                {{ option.label }}
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Issued Credentials List -->
    <div class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-amber-600 scrollbar-track-white/10">
      <!-- Loading State -->
      <div v-if="appStore.isLoading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-600"></div>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredCredentials.length === 0" 
        class="p-12 text-center"
      >
        <div class="w-20 h-20 bg-amber-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText class="w-10 h-10 text-amber-600" />
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Nenhuma credencial emitida</h3>
        <p class="text-amber-200 mb-4">
          {{ searchTerm || (statusFilter && statusFilter !== 'all') ? 'Nenhuma credencial encontrada com os filtros aplicados' : 'Comece enviando uma oferta de credencial' }}
        </p>
      </div>

      <!-- Credentials Cards -->
      <div v-else>
        <div
          v-for="credential in filteredCredentials"
          :key="credential.credential_exchange_id"
          class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4 flex-1">
              <!-- Credential Icon -->
              <div class="w-12 h-12 bg-amber-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Award class="w-6 h-6 text-white" />
              </div>

              <!-- Credential Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-semibold text-white">{{ credential.credential_name }}</h3>
                  <span :class="getStatusClass(credential.status)" class="px-2 py-1 text-xs rounded-full">
                    {{ getStatusLabel(credential.status) }}
                  </span>
                </div>

                <div class="space-y-2">
                  <!-- Holder Info -->
                  <div class="flex items-center text-sm text-amber-200">
                    <User class="w-4 h-4 mr-2" />
                    <span>{{ credential.holder_alias || credential.holder_did || 'Destinatário não identificado' }}</span>
                  </div>

                  <!-- Issue Date -->
                  <div class="flex items-center text-sm text-amber-200">
                    <Calendar class="w-4 h-4 mr-2" />
                    <span>{{ formatDate(credential.issued_at) }}</span>
                  </div>

                  <!-- Attributes -->
                  <div class="mt-3">
                    <button
                      @click="toggleAttributes(credential.credential_exchange_id)"
                      class="flex items-center text-sm text-amber-300 hover:text-amber-200 transition-colors cursor-pointer"
                    >
                      <ChevronDown 
                        :class="{ 'rotate-180': expandedCredentials.has(credential.credential_exchange_id) }"
                        class="w-4 h-4 mr-1 transition-transform cursor-pointer"
                      />
                      {{ expandedCredentials.has(credential.credential_exchange_id) ? 'Ocultar' : 'Ver' }} Atributos
                    </button>
                    
                    <div 
                      v-if="expandedCredentials.has(credential.credential_exchange_id)"
                      class="mt-2 bg-white/5 rounded-lg p-3 space-y-1"
                    >
                      <div 
                        v-for="(value, key) in credential.attributes" 
                        :key="key"
                        class="flex justify-between text-sm"
                      >
                        <span class="text-amber-300 font-medium">{{ key }}:</span>
                        <span class="text-white">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2 ml-4">
              <Button
                v-if="credential.status === 'request-received'"
                size="sm"
                @click="handleIssueCredential(credential)"
                class="bg-amber-600 hover:bg-amber-700 text-white cursor-pointer"
              >
                <Send class="w-4 h-4 mr-2" />
                Emitir
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="viewCredentialDetails(credential)"
                class="text-amber-300 hover:text-amber-200 hover:bg-white/10 cursor-pointer"
              >
                <Eye class="w-4 h-4 cursor-pointer" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for New Credential Offer -->
    <div
      v-if="showOfferModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeOfferModal"
    >
      <div class="bg-gradient-to-br from-amber-900/90 to-amber-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-white">Nova Oferta de Credencial</h3>
          <button
            @click="closeOfferModal"
            class="text-white hover:text-amber-300 transition-colors cursor-pointer"
          >
            <X class="w-6 h-6" />
          </button>
        </div>

        <form @submit.prevent="submitOffer" class="space-y-6">
          <!-- Connection Selection -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Conexão (buscar por email)</label>
            <div class="relative">
              <Input
                v-model="connectionSearch"
                @input="searchConnections"
                :disabled="!!offerForm.connection_id"
                placeholder="Digite o email do destinatário..."
                class="bg-white/20 border-white/30 text-white placeholder:text-amber-200 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <Search class="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-amber-300" />
            </div>
            
            <!-- Connection Results -->
            <div 
              v-if="connectionSearch && filteredConnections.length > 0 && !offerForm.connection_id"
              class="bg-white/10 rounded-lg border border-white/20 mt-2 max-h-40 overflow-y-auto"
            >
              <button
                v-for="conn in filteredConnections"
                :key="conn.connection_id"
                type="button"
                @click="selectConnection(conn)"
                class="w-full text-left px-4 py-2 hover:bg-white/10 transition-colors text-white text-sm cursor-pointer"
              >
                <div class="font-medium">{{ conn.alias }}</div>
                <div class="text-xs text-amber-200">ID: {{ conn.connection_id }}</div>
              </button>
            </div>

            <!-- Selected Connection -->
            <div 
              v-if="offerForm.connection_id"
              class="bg-amber-600/20 border border-amber-600/30 rounded-lg p-3 mt-2"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-white font-medium">{{ selectedConnection?.alias }}</div>
                  <div class="text-xs text-amber-200">{{ offerForm.connection_id }}</div>
                </div>
                <button
                  type="button"
                  @click="clearConnection"
                  class="text-amber-300 hover:text-white transition-colors cursor-pointer"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          <!-- Schema Selection -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Schema da Credencial</label>
            <Select v-model="offerForm.schema_id" @update:model-value="onSchemaChange">
              <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-amber-600/50 data-[placeholder]:text-amber-200">
                <SelectValue placeholder="Selecione um schema" />
              </SelectTrigger>
              <SelectContent class="bg-amber-900/95 backdrop-blur-md border-white/30 shadow-xl">
                <SelectGroup>
                  <SelectLabel class="text-amber-300 font-semibold px-2 py-1.5">
                    Schemas Disponíveis
                  </SelectLabel>
                  <SelectItem
                    v-for="credential in credentialStore.credentials"
                    :key="credential.id"
                    :value="credential.id"
                    class="!text-white hover:!bg-amber-600/60 focus:!bg-amber-600/70 focus:!text-white data-[highlighted]:bg-amber-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
                  >
                    {{ credential.name }} (v{{ credential.version }})
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <!-- Attributes -->
          <div v-if="schemaAttributes.length > 0" class="space-y-4">
            <label class="text-sm font-medium text-white">Atributos da Credencial</label>
            <div 
              v-for="attr in schemaAttributes"
              :key="attr"
              class="space-y-2"
            >
              <label class="text-sm text-amber-200">{{ attr }}</label>
              <Input
                v-model="attributeValues[attr]"
                :placeholder="`Digite o valor para ${attr}`"
                required
                class="bg-white/20 border-white/30 text-white placeholder:text-amber-200"
              />
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-white/20">
            <Button
              type="button"
              @click="closeOfferModal"
              class="bg-white/10 hover:bg-white/20 text-amber-200 hover:text-white border border-white/20 cursor-pointer transition-colors"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              :disabled="!canSubmitOffer"
              class="bg-amber-600 hover:bg-amber-700 text-white cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send class="w-4 h-4 mr-2" />
              Enviar Oferta
            </Button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal for Credential Details -->
    <div
      v-if="showDetailsModal && selectedCredential"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeDetailsModal"
    >
      <div class="bg-gradient-to-br from-amber-900/90 to-amber-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-xl">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-white">Detalhes da Credencial</h3>
          <button
            @click="closeDetailsModal"
            class="text-white hover:text-amber-300 transition-colors cursor-pointer"
          >
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="space-y-4">
          <div class="bg-white/10 rounded-lg p-4 space-y-3">
            <div class="flex justify-between">
              <span class="text-amber-300 font-medium">Nome:</span>
              <span class="text-white">{{ selectedCredential.credential_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-amber-300 font-medium">Status:</span>
              <span :class="getStatusClass(selectedCredential.status)" class="px-2 py-1 text-xs rounded-full">
                {{ getStatusLabel(selectedCredential.status) }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-amber-300 font-medium">Data de Emissão:</span>
              <span class="text-white">{{ formatDate(selectedCredential.issued_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-amber-300 font-medium">Destinatário:</span>
              <span class="text-white">{{ selectedCredential.holder_alias || 'N/A' }}</span>
            </div>
          </div>

          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-amber-300 font-medium mb-3">Atributos:</h4>
            <div class="space-y-2">
              <div 
                v-for="(value, key) in selectedCredential.attributes" 
                :key="key"
                class="flex justify-between"
              >
                <span class="text-amber-200">{{ key }}:</span>
                <span class="text-white font-medium">{{ value }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-amber-300 font-medium mb-2">ID de Troca:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.credential_exchange_id }}
            </code>
          </div>

          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-amber-300 font-medium mb-2">Definition ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.credential_definition_id }}
            </code>
          </div>
        </div>

        <div class="flex justify-end mt-6 pt-4 border-t border-white/20">
          <Button
            @click="closeDetailsModal"
            class="bg-amber-600 hover:bg-amber-700 text-white cursor-pointer"
          >
            Fechar
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCredentialStore, type IssuedCredential } from '@/stores/credential'
import { useConnectionStore, type Connection } from '@/stores/connection'
import { useAppStore } from '@/stores/app'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Plus, 
  Award, 
  User, 
  Calendar, 
  ChevronDown, 
  Eye, 
  X, 
  Search, 
  Send,
  FileText
} from 'lucide-vue-next'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// Stores
const credentialStore = useCredentialStore()
const connectionStore = useConnectionStore()
const appStore = useAppStore()

// State
const searchTerm = ref('')
const statusFilter = ref('all')
const expandedCredentials = ref(new Set<string>())
const showOfferModal = ref(false)
const showDetailsModal = ref(false)
const selectedCredential = ref<IssuedCredential | null>(null)
const connectionSearch = ref('')
const selectedConnection = ref<Connection | null>(null)
const schemaAttributes = ref<string[]>([])
const attributeValues = ref<Record<string, string>>({})

// Status options for filter
const statusOptions = [
  { value: 'all', label: 'Todos os status' },
  { value: 'offer-sent', label: 'Oferta Enviada' },
  { value: 'request-received', label: 'Solicitação Recebida' },
  { value: 'credential-issued', label: 'Credencial Emitida' },
  { value: 'done', label: 'Concluído' }
]

// Offer Form
const offerForm = ref({
  connection_id: '',
  schema_id: '',
  attributes: [] as Array<{ name: string; value: string }>
})

// Computed
const filteredCredentials = computed(() => {
  let result = credentialStore.issuedCredentials

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    result = result.filter(cred => 
      cred.credential_name.toLowerCase().includes(search) ||
      cred.holder_alias?.toLowerCase().includes(search) ||
      Object.values(cred.attributes).some(val => 
        val.toLowerCase().includes(search)
      )
    )
  }

  // Filter by status
  if (statusFilter.value && statusFilter.value !== 'all') {
    result = result.filter(cred => cred.status === statusFilter.value)
  }

  return result
})

const filteredConnections = computed(() => {
  if (!connectionSearch.value) return []
  
  const search = connectionSearch.value.toLowerCase()
  return connectionStore.connections.filter(conn => 
    conn.alias.toLowerCase().includes(search) &&
    conn.state === 'active'
  )
})

const canSubmitOffer = computed(() => {
  return (
    offerForm.value.connection_id &&
    offerForm.value.schema_id &&
    schemaAttributes.value.length > 0 &&
    schemaAttributes.value.every(attr => attributeValues.value[attr]?.trim())
  )
})

// Methods
function getStatusClass(status: string): string {
  switch (status) {
    case 'done':
    case 'credential-issued':
      return 'bg-green-500/20 text-green-300 border border-green-500/30'
    case 'offer-sent':
      return 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
    case 'request-received':
      return 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
    default:
      return 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
  }
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    'offer-sent': 'Oferta Enviada',
    'request-received': 'Solicitação Recebida',
    'credential-issued': 'Credencial Emitida',
    'done': 'Concluído'
  }
  return labels[status] || status
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function toggleAttributes(credentialId: string) {
  if (expandedCredentials.value.has(credentialId)) {
    expandedCredentials.value.delete(credentialId)
  } else {
    expandedCredentials.value.add(credentialId)
  }
}

function viewCredentialDetails(credential: IssuedCredential) {
  selectedCredential.value = credential
  showDetailsModal.value = true
}

function closeDetailsModal() {
  showDetailsModal.value = false
  selectedCredential.value = null
}

async function openOfferModal() {
  showOfferModal.value = true
  
  // Load connections and credentials if not loaded
  if (connectionStore.connections.length === 0) {
    await connectionStore.fetchAll()
  }
  if (credentialStore.credentials.length === 0) {
    await credentialStore.fetchCredentials()
  }
}

function closeOfferModal() {
  showOfferModal.value = false
  resetOfferForm()
}

function resetOfferForm() {
  offerForm.value = {
    connection_id: '',
    schema_id: '',
    attributes: []
  }
  connectionSearch.value = ''
  selectedConnection.value = null
  schemaAttributes.value = []
  attributeValues.value = {}
}

function searchConnections() {
  // Reactive filtering happens in computed property
}

function selectConnection(connection: Connection) {
  selectedConnection.value = connection
  offerForm.value.connection_id = connection.connection_id
  connectionSearch.value = '' // Limpa o campo de busca
}

function clearConnection() {
  selectedConnection.value = null
  offerForm.value.connection_id = ''
  connectionSearch.value = ''
}

async function onSchemaChange() {
  if (!offerForm.value.schema_id) return
  
  // Try to find credential in already loaded list
  const credential = credentialStore.credentials.find(c => c.id === offerForm.value.schema_id)
  
  if (credential) {
    schemaAttributes.value = credential.attributes
    
    // Reset attribute values
    attributeValues.value = {}
    credential.attributes.forEach((attr: string) => {
      attributeValues.value[attr] = ''
    })
  } else {
    // Fallback: fetch schema details if not in list
    const details = await credentialStore.fetchCredentialDetails(offerForm.value.schema_id)
    
    if (details && details.attributes) {
      schemaAttributes.value = details.attributes
      
      // Reset attribute values
      attributeValues.value = {}
      details.attributes.forEach((attr: string) => {
        attributeValues.value[attr] = ''
      })
    }
  }
}

async function submitOffer() {
  if (!canSubmitOffer.value) return

  // Build attributes array
  offerForm.value.attributes = schemaAttributes.value.map(attr => ({
    name: attr,
    value: attributeValues.value[attr] || ''
  }))

  // Send offer
  const result = await credentialStore.sendCredentialOffer(offerForm.value)

  if (result) {
    closeOfferModal()
  }
}

async function handleIssueCredential(credential: IssuedCredential) {
  if (!credential.credential_exchange_id) {
    appStore.addNotification('ID de troca de credencial inválido', 'error')
    return
  }

  const result = await credentialStore.issueCredential(credential.credential_exchange_id)
  
  if (result) {
    // The credential list will be automatically refreshed by the store
  }
}

// Lifecycle
onMounted(async () => {
  await credentialStore.fetchIssuedCredentials()
})
</script>

<style scoped>
/* Custom scrollbar for the credentials list */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgb(217, 119, 6);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgb(180, 83, 9);
}
</style>

<style>
/* Global styles for Select component in this view */
[data-reka-select-content] {
  max-height: 300px;
  overflow-y: auto;
}

[data-reka-select-content]::-webkit-scrollbar {
  width: 6px;
}

[data-reka-select-content]::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

[data-reka-select-content]::-webkit-scrollbar-thumb {
  background: rgb(217, 119, 6);
  border-radius: 3px;
}

[data-reka-select-content]::-webkit-scrollbar-thumb:hover {
  background: rgb(180, 83, 9);
}
</style>
