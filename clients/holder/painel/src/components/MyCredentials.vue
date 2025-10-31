<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-white mb-2">Minhas Credenciais</h2>
        <p class="text-purple-200">Visualize todas as suas credenciais verificáveis</p>
      </div>
      <div class="flex-shrink-0">
        <Button 
          @click="loadCredentials" 
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
          placeholder="Buscar por nome da credencial ou emissor..."
          class="bg-white/20 border-white/30 text-white placeholder:text-purple-200"
        />
      </div>
    </div>

    <!-- Credentials List -->
    <div class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-purple-600 scrollbar-track-white/10">
      <!-- Loading State -->
      <div v-if="appStore.isLoading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600"></div>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredCredentials.length === 0" 
        class="p-12 text-center"
      >
        <div class="w-20 h-20 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Award class="w-10 h-10 text-purple-600" />
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Nenhuma credencial encontrada</h3>
        <p class="text-purple-200 mb-4">
          {{ searchTerm ? 'Nenhuma credencial encontrada com os filtros aplicados' : 'Você ainda não possui credenciais verificáveis' }}
        </p>
        <Button 
          v-if="!searchTerm"
          @click="loadCredentials" 
          class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
        >
          <RefreshCw class="w-4 h-4 mr-2" />
          Verificar novamente
        </Button>
      </div>

      <!-- Actual Credentials -->
      <div v-if="!appStore.isLoading && filteredCredentials.length > 0">
        <div
          v-for="(credential, index) in filteredCredentials"
          :key="`${credential.cred_def_id}-${index}`"
          class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-4 flex-1">
              <!-- Credential Icon -->
              <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Award class="w-6 h-6 text-white" />
              </div>
              
              <!-- Credential Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-3 mb-3">
                  <h3 class="text-lg font-semibold text-white">{{ getSchemaName(credential.schema_id) }}</h3>
                  <span class="px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-300">
                    Emitida
                  </span>
                </div>
                
                <div class="space-y-2 text-sm">
                  <div>
                    <span class="text-purple-300">Emissor: </span>
                    <span class="text-white">{{ credential.issuer_name || 'Emissor não identificado' }}</span>
                  </div>
                  <div>
                    <span class="text-purple-300">Issuer DID: </span>
                    <span class="text-white font-mono text-xs">{{ credential.issuer_did }}</span>
                  </div>
                  
                  <!-- Attributes -->
                  <div class="pt-2 mt-2 border-t border-white/10">
                    <div
                      v-for="(value, key) in credential.attrs"
                      :key="key"
                      class="py-1"
                    >
                      <span class="text-purple-300">{{ key }}: </span>
                      <span class="text-white">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center space-x-2 ml-4">
              <Button
                @click="viewCredentialDetails(credential)"
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

    <!-- Credential Details Modal -->
    <div
      v-if="showDetailsModal && selectedCredential"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeDetailsModal"
    >
      <div class="bg-gradient-to-br from-purple-900/90 to-purple-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-white">Detalhes da Credencial</h3>
          <button
            @click="closeDetailsModal"
            class="text-white hover:text-purple-300 transition-colors cursor-pointer"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- General Info -->
          <div class="bg-white/10 rounded-lg p-4 space-y-3">
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Nome da Credencial:</span>
              <span class="text-white text-right">{{ getSchemaName(selectedCredential.schema_id) }}</span>
            </div>
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Emissor:</span>
              <span class="text-white text-right">{{ selectedCredential.issuer_name || 'Não identificado' }}</span>
            </div>
            <div class="flex justify-between items-start">
              <span class="text-purple-300 font-medium">Status:</span>
              <span class="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-300">
                Emitida e Válida
              </span>
            </div>
          </div>
          
          <!-- Issuer DID -->
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Issuer DID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.issuer_did }}
            </code>
          </div>
          
          <!-- Connection ID -->
          <div v-if="selectedCredential.connection_id" class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Connection ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.connection_id }}
            </code>
          </div>
          
          <!-- Schema ID -->
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Schema ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.schema_id }}
            </code>
          </div>
          
          <!-- Credential Definition ID -->
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-2">Credential Definition ID:</h4>
            <code class="text-xs text-white break-all bg-black/30 p-2 rounded block">
              {{ selectedCredential.cred_def_id }}
            </code>
          </div>
          
          <!-- Attributes -->
          <div class="bg-white/10 rounded-lg p-4">
            <h4 class="text-purple-300 font-medium mb-3 flex items-center">
              <FileText class="w-4 h-4 mr-2" />
              Atributos da Credencial
            </h4>
            <div class="space-y-3">
              <div
                v-for="(value, key) in selectedCredential.attrs"
                :key="key"
                class="bg-black/30 rounded p-3"
              >
                <span class="text-purple-300 text-sm font-medium block mb-1">{{ key }}</span>
                <span class="text-white font-medium">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Award, RefreshCw, Eye, X, FileText } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useCredentialStore, type Credential } from '@/stores/credential'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

// Stores
const credentialStore = useCredentialStore()
const appStore = useAppStore()
const authStore = useAuthStore()

// State
const searchTerm = ref('')
const showDetailsModal = ref(false)
const selectedCredential = ref<Credential | null>(null)

// Computed
const filteredCredentials = computed(() => {
  let result = credentialStore.credentials
  
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    result = result.filter(cred => {
      const schemaName = getSchemaName(cred.schema_id).toLowerCase()
      const issuerName = (cred.issuer_name || '').toLowerCase()
      const issuerDid = cred.issuer_did.toLowerCase()
      
      return schemaName.includes(search) || 
             issuerName.includes(search) || 
             issuerDid.includes(search) ||
             Object.values(cred.attrs).some(value => 
               value.toLowerCase().includes(search)
             )
    })
  }
  
  return result
})

// Methods
async function loadCredentials() {
  await credentialStore.fetchCredentials(authStore.userDid)
}

function getSchemaName(schemaId: string): string {
  // Schema ID format: <did>:2:<name>:<version>
  const parts = schemaId.split(':')
  if (parts.length >= 3 && parts[2]) {
    return parts[2]
  }
  return schemaId
}

function viewCredentialDetails(credential: Credential) {
  selectedCredential.value = credential
  showDetailsModal.value = true
}

function closeDetailsModal() {
  showDetailsModal.value = false
  setTimeout(() => {
    selectedCredential.value = null
  }, 300)
}

// Lifecycle
onMounted(() => {
  loadCredentials()
})
</script>
