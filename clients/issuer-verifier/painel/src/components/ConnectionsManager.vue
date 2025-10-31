<template>
   <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4 pr-2">
         <div class="flex-1">
            <h2 class="text-2xl font-bold text-white mb-2">Conexões SSI</h2>
            <p class="text-blue-100">Gerencie suas conexões de identidade auto-soberana</p>
         </div>
         <div class="flex-shrink-0">
            <Button @click="showGenerateUrlModal = true" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">
               <Plus class="w-4 h-4 mr-2" />
               Gerar URL de Convite
            </Button>
         </div>
      </div>
      <!-- Filters and Search -->
      <div class="flex gap-4 pr-2">
         <div class="flex-1 min-w-0">
            <Input
               v-model="searchTerm"
               placeholder="Buscar conexões..."
               class="bg-white/20 border-white/30 text-white placeholder:text-blue-100"
            />
         </div>
         <div class="w-48 flex-shrink-0">
            <Select v-model="statusFilter" default-value="all">
               <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-blue-600/50 data-[placeholder]:text-blue-100">
                  <SelectValue placeholder="Filtrar por status" />
               </SelectTrigger>
               <SelectContent class="bg-blue-900/95 backdrop-blur-md border-white/30 shadow-xl">
                  <SelectGroup>
                     <SelectItem
                        v-for="option in statusOptions"
                        :key="option.value"
                        :value="option.value"
                        class="!text-white hover:!bg-blue-600/60 focus:!bg-blue-600/70 focus:!text-white data-[highlighted]:bg-blue-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
                     >
                        {{ option.label }}
                     </SelectItem>
                  </SelectGroup>
               </SelectContent>
            </Select>
         </div>
      </div>
      <!-- Connections List -->
      <div class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-blue-600 scrollbar-track-white/10">
         <!-- Loading State -->
         <div v-if="appStore.isLoading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
         </div>

         <!-- Empty State -->
         <div 
            v-else-if="filteredConnections.length === 0" 
            class="p-12 text-center"
         >
            <div class="w-20 h-20 bg-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
               <Network class="w-10 h-10 text-white" />
            </div>
            <h3 class="text-xl font-semibold text-white mb-2">Nenhuma conexão encontrada</h3>
            <p class="text-blue-100 mb-4">
               {{ searchTerm || (statusFilter && statusFilter !== 'all') ? 'Nenhuma conexão encontrada com os filtros aplicados' : 'Comece criando sua primeira conexão SSI' }}
            </p>
            <Button 
               v-if="!searchTerm && (!statusFilter || statusFilter === 'all')"
               @click="showGenerateUrlModal = true" 
               class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
            >
               <Plus class="w-4 h-4 mr-2" />
               Criar Primeira Conexão
            </Button>
         </div>

         <!-- Actual Connections -->
         <div v-else>
            <div
               v-for="connection in filteredConnections"
               :key="connection.connection_id"
               class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200"
            >
               <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-4 flex-1">
                     <!-- Connection Icon -->
                     <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                        <Network class="w-6 h-6 text-white" />
                     </div>
                     <!-- Connection Info -->
                     <div class="flex-1">
                        <div class="flex items-center space-x-3 mb-2">
                           <h3 class="text-lg font-semibold text-white">{{ connection.alias }}</h3>
                           <span
                              :class="[
                              'px-2 py-1 rounded-full text-xs font-medium',
                              getStatusClass(connection.state)
                              ]"
                              >
                           {{ getStatusLabel(connection.state) }}
                           </span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                           <div>
                              <span class="text-blue-200">ID: </span>
                              <span class="text-white font-mono text-xs">{{ connection.connection_id?.substring(0, 20) || 'N/A' }}...</span>
                           </div>
                           <div>
                              <span class="text-blue-200">Criado em: </span>
                              <span class="text-white">{{ formatDate(connection.created_at) }}</span>
                           </div>
                        </div>
                        <div class="mt-2" v-if="connection.their_label">
                           <span class="text-blue-200">Label: </span>
                           <span class="text-white">{{ connection.their_label }}</span>
                        </div>
                        <div class="mt-2" v-if="connection.their_did">
                           <span class="text-blue-200">Their DID: </span>
                           <span class="text-white font-mono text-xs">{{ connection.their_did }}</span>
                        </div>
                        <div class="mt-2" v-else>
                           <span class="text-blue-200">Their DID: </span>
                           <span class="text-gray-400 text-xs italic">Aguardando estabelecimento da conexão</span>
                        </div>
                     </div>
                  </div>
                  <!-- Actions -->
                  <div class="flex items-center space-x-2">
                     <Button
                        @click="viewConnectionDetails(connection)"
                        variant="ghost"
                        size="sm"
                        class="text-blue-100 hover:text-white hover:bg-white/10 cursor-pointer"
                        title="Ver Detalhes"
                        >
                        <Eye class="w-4 h-4" />
                     </Button>
                  </div>
               </div>
            </div>
         </div>
      </div>
      
      <!-- DID Document Modal -->
         <div
            v-if="showDidModal"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            @click="showDidModal = false"
            >
            <div
               class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-8 max-w-4xl w-full max-h-[80vh] min-h-[60vh] overflow-y-auto"
               @click.stop
               >
               <div class="flex justify-between items-center mb-6">
                  <h3 class="text-2xl font-bold text-white">DID Document</h3>
                  <Button @click="showDidModal = false" variant="ghost" size="sm" class="cursor-pointer">
                     <X class="w-5 h-5" />
                  </Button>
               </div>
               <div class="bg-black/30 rounded-lg p-6 min-h-[400px]">
                  <pre class="text-blue-100 text-sm overflow-x-auto whitespace-pre-wrap">{{ selectedDidDocument }}</pre>
               </div>
            </div>
         </div>
         <!-- Generate URL Modal -->
         <div
            v-if="showGenerateUrlModal"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            @click="showGenerateUrlModal = false"
            >
            <div
               class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-8 max-w-2xl w-full"
               @click.stop
               >
               <div class="flex justify-between items-center mb-6">
                  <h3 class="text-2xl font-bold text-white">Gerar URL de Convite</h3>
                  <Button @click="showGenerateUrlModal = false" variant="ghost" size="sm" class="cursor-pointer">
                     <X class="w-5 h-5" />
                  </Button>
               </div>
               <form @submit.prevent="handleGenerateUrl" class="space-y-6">
                  <div class="space-y-2">
                     <label class="text-sm font-medium text-white">Nome da Conexão (Alias)</label>
                     <Input
                        v-model="generateUrlForm.alias"
                        type="text"
                        placeholder="Ex: holder@example.com"
                        required
                        :disabled="generatedUrl !== ''"
                        class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                        />
                  </div>
                  <div v-if="generatedUrl" class="space-y-3">
                     <label class="text-sm font-medium text-white">URL Gerada</label>
                     <div class="bg-black/30 rounded-lg p-4">
                        <p class="text-blue-100 text-sm break-all font-mono">{{ generatedUrl }}</p>
                     </div>
                     <Button
                        @click="copyUrlToClipboard"
                        type="button"
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer"
                        >
                        {{ urlCopied ? '✓ Copiado!' : 'Copiar URL' }}
                     </Button>
                  </div>
                  <div class="flex justify-end space-x-3 pt-4">
                     <Button @click="closeGenerateUrlModal" variant="ghost" class="text-blue-100 cursor-pointer">
                     {{ generatedUrl ? 'Fechar' : 'Cancelar' }}
                     </Button>
                     <Button 
                        v-if="!generatedUrl"
                        type="submit" 
                        :disabled="appStore.isLoading || !generateUrlForm.alias"
                        class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                     {{ appStore.isLoading ? 'Gerando...' : 'Gerar URL' }}
                     </Button>
                  </div>
               </form>
            </div>
         </div>
         <!-- Connection Details Modal -->
         <div
            v-if="showDetailsModal && selectedConnection"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            @click.self="closeDetailsModal"
            >
            <div class="bg-gradient-to-br from-blue-900/90 to-blue-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
               <div class="flex justify-between items-center mb-6">
                  <h3 class="text-2xl font-bold text-white">Detalhes da Conexão</h3>
                  <button
                     @click="closeDetailsModal"
                     class="text-white hover:text-blue-200 transition-colors cursor-pointer"
                     >
                     <X class="w-6 h-6" />
                  </button>
               </div>
               <div class="space-y-4">
                  <div class="bg-white/10 rounded-lg p-4 space-y-3">
                     <div class="flex justify-between items-start">
                        <span class="text-blue-200 font-medium">Alias:</span>
                        <span class="text-white text-right">{{ selectedConnection.alias }}</span>
                     </div>
                     <div class="flex justify-between items-start">
                        <span class="text-blue-200 font-medium">Status:</span>
                        <span :class="getStatusClass(selectedConnection.state)" class="px-2 py-1 text-xs rounded-full">
                        {{ getStatusLabel(selectedConnection.state) }}
                        </span>
                     </div>
                     <div class="flex justify-between items-start">
                        <span class="text-blue-200 font-medium">Criado em:</span>
                        <span class="text-white">{{ formatDate(selectedConnection.created_at) }}</span>
                     </div>
                     <div class="flex justify-between items-start">
                        <span class="text-blue-200 font-medium">Atualizado em:</span>
                        <span class="text-white">{{ formatDate(selectedConnection.updated_at) }}</span>
                     </div>
                     <div v-if="selectedConnection.their_label" class="flex justify-between items-start">
                        <span class="text-blue-200 font-medium">Their Label:</span>
                        <span class="text-white">{{ selectedConnection.their_label }}</span>
                     </div>
                  </div>
                  <div class="bg-white/10 rounded-lg p-4">
                     <h4 class="text-blue-200 font-medium mb-2">Connection ID:</h4>
                     <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
                     {{ selectedConnection.connection_id }}
                     </code>
                  </div>
                  <div class="bg-white/10 rounded-lg p-4">
                     <h4 class="text-blue-200 font-medium mb-2">Invitation Key:</h4>
                     <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
                     {{ selectedConnection.invitation_key }}
                     </code>
                  </div>
                  <div class="bg-white/10 rounded-lg p-4">
                     <h4 class="text-blue-200 font-medium mb-2">My DID:</h4>
                     <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
                     {{ selectedConnection.my_did }}
                     </code>
                  </div>
                  <div v-if="selectedConnection.their_did" class="bg-white/10 rounded-lg p-4">
                     <h4 class="text-blue-200 font-medium mb-2">Their DID:</h4>
                     <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
                     {{ selectedConnection.their_did }}
                     </code>
                  </div>
                  <div v-else class="bg-white/10 rounded-lg p-4">
                     <h4 class="text-blue-200 font-medium mb-2">Their DID:</h4>
                     <p class="text-gray-400 text-sm italic">Aguardando estabelecimento da conexão</p>
                  </div>
               </div>
            </div>
         </div>
   </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Network, Eye, X } from 'lucide-vue-next'
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
import { useConnectionStore, useInvitationStore, useAppStore } from '@/stores'

// Stores
const connectionStore = useConnectionStore()
const invitationStore = useInvitationStore()
const appStore = useAppStore()

// Reactive data
const searchTerm = ref('')
const statusFilter = ref('all')

// Status options for filter
const statusOptions = [
   { value: 'all', label: 'Todos os status' },
   { value: 'active', label: 'Ativo' },
   { value: 'response', label: 'Conectado' },
   { value: 'request', label: 'Pendente' },
   { value: 'invitation', label: 'Convite Enviado' },
   { value: 'inactive', label: 'Inativo' },
   { value: 'error', label: 'Erro' }
]
const showDidModal = ref(false)
const selectedDidDocument = ref('')
const showGenerateUrlModal = ref(false)
const generatedUrl = ref('')
const urlCopied = ref(false)
const showDetailsModal = ref(false)
const selectedConnection = ref<any>(null)

// Generate URL form
const generateUrlForm = ref({
  alias: ''
})

const filteredConnections = computed(() => {
  return connectionStore.connections.filter(connection => {
    // Filtrar apenas conexões válidas (com connection_id)
    if (!connection || !connection.connection_id) {
      return false
    }
    
    const matchesSearch = !searchTerm.value || 
      connection.alias?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      connection.connection_id?.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      (connection.their_did && connection.their_did.toLowerCase().includes(searchTerm.value.toLowerCase()))
    
    const matchesStatus = statusFilter.value === 'all' || !statusFilter.value || connection.state === statusFilter.value
    
    return matchesSearch && matchesStatus
  })
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Use connection store methods
const fetchConnections = () => connectionStore.fetchAll()
const getStatusClass = (state: string) => connectionStore.getStatusClass(state)
const getStatusLabel = (state: string) => connectionStore.getStatusLabel(state)

const viewConnectionDetails = (connection: any) => {
  selectedConnection.value = connection
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedConnection.value = null
}

const handleGenerateUrl = async () => {
  const result = await invitationStore.create(generateUrlForm.value.alias)
  
  if (result && result.invitation_url) {
    generatedUrl.value = result.invitation_url
    urlCopied.value = false
    
    // Recarregar lista de conexões
    await fetchConnections()
  }
}

const copyUrlToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedUrl.value)
    urlCopied.value = true
    appStore.addNotification('URL copiada para área de transferência!', 'success')
    setTimeout(() => {
      urlCopied.value = false
    }, 2000)
  } catch (err) {
    appStore.addNotification('Erro ao copiar URL', 'error')
  }
}

const closeGenerateUrlModal = () => {
  showGenerateUrlModal.value = false
  // Limpar formulário após um breve delay para evitar flash
  setTimeout(() => {
    generateUrlForm.value = { alias: '' }
    generatedUrl.value = ''
    urlCopied.value = false
  }, 300)
}

// Carregar conexões ao montar o componente
onMounted(() => {
  fetchConnections()
})
</script>