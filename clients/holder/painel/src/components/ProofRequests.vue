<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-white mb-2">Pedidos de Prova</h2>
        <p class="text-purple-200">Responda solicitações de prova de credenciais</p>
      </div>
      <div class="flex-shrink-0">
        <Button 
          @click="loadProofRequests" 
          :disabled="appStore.isLoading"
          class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
        >
          <RefreshCw :class="['w-4 h-4 mr-2', { 'animate-spin': appStore.isLoading }]" />
          Atualizar
        </Button>
      </div>
    </div>

    <!-- Proof Requests List -->
    <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-purple-600 scrollbar-track-white/10">
      <!-- Loading State -->
      <div v-if="appStore.isLoading && !selectedRequest" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600"></div>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="proofStore.proofRequests.length === 0" 
        class="p-12 text-center"
      >
        <div class="w-20 h-20 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShieldCheck class="w-10 h-10 text-purple-600" />
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Nenhum pedido de prova</h3>
        <p class="text-purple-200 mb-4">
          Você não tem pedidos de prova pendentes no momento
        </p>
        <Button 
          @click="loadProofRequests" 
          class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
        >
          <RefreshCw class="w-4 h-4 mr-2" />
          Verificar novamente
        </Button>
      </div>

      <!-- Actual Proof Requests -->
      <div v-if="!appStore.isLoading && proofStore.proofRequests.length > 0 && !selectedRequest">
        <div
          v-for="request in proofStore.proofRequests"
          :key="request.id"
          class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200 cursor-pointer"
          @click="selectProofRequest(request)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4 flex-1">
              <!-- Request Icon -->
              <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                <ShieldCheck class="w-6 h-6 text-white" />
              </div>
              
              <!-- Request Info -->
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-semibold text-white">{{ request.name }}</h3>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      getStateColor(request.state)
                    ]"
                  >
                    {{ getStateLabel(request.state) }}
                  </span>
                </div>
                
                <!-- Error Message Preview -->
                <div 
                  v-if="request.state === 'abandoned' && request.error_msg"
                  class="mb-2 p-2 bg-red-500/20 border border-red-500/30 rounded flex items-start gap-2"
                >
                  <AlertCircle class="w-4 h-4 text-red-300 shrink-0 mt-0.5" />
                  <p class="text-red-200 text-xs">{{ request.error_msg }}</p>
                </div>
                
                <div class="space-y-1 text-sm text-purple-200">
                  <div class="flex items-center space-x-2">
                    <span class="font-medium">Versão:</span>
                    <span>{{ request.version }}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="font-medium">Atributos solicitados:</span>
                    <span>{{ Object.keys(request.requested_attributes).length }}</span>
                  </div>
                  <div v-if="Object.keys(request.requested_predicates).length > 0" class="flex items-center space-x-2">
                    <span class="font-medium">Predicados:</span>
                    <span>{{ Object.keys(request.requested_predicates).length }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Button -->
            <div class="flex-shrink-0 ml-4">
              <Button 
                @click.stop="selectProofRequest(request)"
                class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer"
              >
                <Eye class="w-4 h-4 mr-2" />
                Ver Detalhes
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed View -->
      <div v-if="selectedRequest" class="space-y-6">
        <!-- Back Button -->
        <div>
          <Button 
            @click="closeDetailView"
            variant="outline"
            class="border-purple-400/50 text-purple-200 hover:text-purple-200 bg-purple-600/20 hover:bg-purple-600/30 hover:border-purple-400 cursor-pointer"
          >
            <ChevronLeft class="w-4 h-4 mr-2" />
            Voltar
          </Button>
        </div>

        <!-- Request Details Card -->
        <div class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-6">
          <div class="flex items-center space-x-4 mb-6">
            <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
              <ShieldCheck class="w-6 h-6 text-white" />
            </div>
            <div class="flex-1">
              <h3 class="text-xl font-bold text-white">{{ selectedRequest.name }}</h3>
              <p class="text-purple-200 text-sm">{{ selectedRequest.version }}</p>
            </div>
            <span
              :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                getStateColor(selectedRequest.state)
              ]"
            >
              {{ getStateLabel(selectedRequest.state) }}
            </span>
          </div>

          <!-- Error Message for Abandoned State -->
          <div 
            v-if="selectedRequest.state === 'abandoned' && selectedRequest.error_msg"
            class="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg"
          >
            <div class="flex items-start gap-3">
              <AlertCircle class="w-5 h-5 text-red-300 flex-shrink-0 mt-0.5" />
              <div class="flex-1">
                <h4 class="text-red-200 font-semibold mb-1">Erro ao gerar apresentação</h4>
                <p class="text-red-200/90 text-sm">{{ selectedRequest.error_msg }}</p>
              </div>
            </div>
          </div>

          <!-- Loading Credentials -->
          <div v-if="loadingCredentials" class="flex justify-center items-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-600"></div>
          </div>

          <!-- Requested Attributes -->
          <div v-else class="space-y-6">
            <div v-for="group in groupedAttributes" :key="group.groupKey">
              <div class="bg-white/5 rounded-lg p-4 border border-white/10">
                <h4 class="text-white font-semibold mb-4 flex items-center">
                  <FileText class="w-4 h-4 mr-2" />
                  {{ group.isGroup ? 'Grupo' : 'Atributo' }}: {{ group.displayName }}
                </h4>

                <!-- Restrictions Info -->
                  <div v-if="group.attributes[0]?.restrictions && group.attributes[0].restrictions.length > 0" class="mb-4">
                    <p class="text-purple-200 text-xs mb-1">Restrições:</p>
                    <div class="flex flex-col gap-1">
                      <span 
                        v-for="(restriction, idx) in group.attributes[0].restrictions" 
                        :key="idx"
                        class="text-xs text-purple-300"
                      >
                        <span v-if="restriction.schema_id">
                          <b>Schema:</b> {{ restriction.schema_id }}
                        </span>
                        <span v-if="restriction.cred_def_id">
                          <b>Cred Def:</b> {{ restriction.cred_def_id }}
                        </span>
                        <span v-if="restriction.issuer_did">
                          <b>Issuer DID:</b> {{ restriction.issuer_did }}
                        </span>
                      </span>
                    </div>
                  </div>
                      <!-- Toggle de revelação para grupo -->
                      <div v-if="group.isGroup && group.attributes.length > 1" class="mb-4 flex items-center gap-2">
                        <label class="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox"
                            :checked="getGroupRevealedForGroup(group)"
                            @change="(e: any) => setGroupRevealedForGroup(group, (e.target as HTMLInputElement).checked)"
                            :disabled="selectedRequest?.state !== 'request-received'"
                            class="sr-only peer"
                          >
                          <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600 peer-disabled:opacity-50 peer-disabled:cursor-not-allowed"></div>
                          <span class="ml-2 text-xs text-purple-200">Revelar todo o grupo</span>
                        </label>
                      </div>

                <!-- Attribute by Attribute Selection -->
                <div class="space-y-4">
                  <div 
                    v-for="attr in group.attributes"
                    :key="attr.referent + '-' + attr.name"
                    class="bg-white/5 rounded p-3 border border-white/5"
                  >
                    <div class="grid grid-cols-[200px_1fr_auto] gap-4 items-center">
                      <!-- Attribute Name -->
                      <div class="flex items-center">
                        <span class="text-white font-medium text-sm">{{ attr.name }}</span>
                      </div>

                      <!-- Value Selection -->
                      <div>
                          <Select 
                            :model-value="attributeSelections[attr.referent]?.[attr.name]?.credentialReferent || ''"
                            @update:modelValue="(value: any) => value && selectAttributeValue(attr.referent, attr.name, String(value), group)"
                            :disabled="selectedRequest?.state !== 'request-received'"
                          >
                            <SelectTrigger 
                              class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-purple-600/50 h-9"
                              :disabled="selectedRequest?.state !== 'request-received'"
                            >
                              <SelectValue placeholder="Selecione o valor">
                                <template v-if="attributeSelections[attr.referent]?.[attr.name]?.value">
                                  <span class="text-sm">{{ attributeSelections[attr.referent]?.[attr.name]?.value }}</span>
                                </template>
                              </SelectValue>
                            </SelectTrigger>
                            <SelectContent class="bg-purple-900/95 backdrop-blur-md border-white/30 shadow-xl max-h-64">
                              <SelectGroup>
                                <SelectItem
                                  v-for="option in getAvailableValuesForAttribute(attr.referent, attr.name, attr.restrictions)"
                                  :key="option.credReferent + '-' + option.value"
                                  :value="option.credReferent"
                                  class="!text-white hover:!bg-purple-600/60 focus:!bg-purple-600/70 focus:!text-white data-[highlighted]:bg-purple-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
                                >
                                  <div class="flex flex-col gap-0.5">
                                    <span class="font-medium text-sm">{{ option.value }}</span>
                                    <span class="text-xs text-purple-300">{{ option.schemaName }}</span>
                                  </div>
                                </SelectItem>
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                      </div>

                      <!-- Revealed Toggle -->
                            <div v-if="!(group.isGroup && group.attributes.length > 1)" class="flex items-center gap-2">
                              <label class="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  :checked="attributeSelections[attr.referent]?.[attr.name]?.revealed ? true : true"
                                  @change="(e: any) => toggleRevealed(attr.referent, attr.name, (e.target as HTMLInputElement).checked)"
                                   :disabled="!attributeSelections[attr.referent]?.[attr.name]?.value || selectedRequest?.state !== 'request-received'"
                                  class="sr-only peer"
                                >
                                <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600 peer-disabled:opacity-50 peer-disabled:cursor-not-allowed"></div>
                                <span class="ml-2 text-xs text-purple-200">Revelar</span>
                              </label>
                            </div>
                    </div>

                    <!-- No values available -->
                    <div 
                      v-if="getAvailableValuesForAttribute(attr.referent, attr.name, attr.restrictions).length === 0"
                      class="mt-2 p-2 bg-red-500/20 border border-red-500/30 rounded text-red-200 text-xs flex items-center gap-2"
                    >
                      <AlertCircle class="w-3 h-3" />
                      <span>Nenhuma credencial disponível com o atributo "{{ attr.name }}"</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Requested Predicates -->
            <div v-if="selectedRequest && Object.keys(selectedRequest.requested_predicates).length > 0">
              <h4 class="text-white font-semibold mb-3 flex items-center">
                <Calculator class="w-4 h-4 mr-2" />
                Predicados Solicitados
              </h4>
              
              <div v-for="(predConfig, referent) in selectedRequest.requested_predicates" :key="referent">
                <div class="bg-white/5 rounded-lg p-4 border border-white/10 mb-3">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-white font-medium">{{ referent }}</span>
                    <span class="px-2 py-1 bg-blue-600/30 rounded text-white text-xs">
                      {{ predConfig.name }} {{ predConfig.p_type }} {{ predConfig.p_value }}
                    </span>
                  </div>

                  <!-- Credential Selection for Predicate -->
                  <div class="mt-4">
                    <p class="text-purple-200 text-sm mb-2">Selecione a credencial que satisfaz o predicado:</p>
                    
                    <!-- Alerta quando não há credenciais válidas -->
                    <div 
                      v-if="getMatchingCredentialsForReferent(referent, predConfig.restrictions).length === 0"
                      class="mb-3 p-3 bg-red-500/20 border border-red-500/30 rounded text-red-200 text-sm flex items-center gap-2"
                    >
                      <AlertCircle class="w-4 h-4 flex-shrink-0" />
                      <div>
                        <p class="font-semibold">Nenhuma credencial satisfaz este predicado</p>
                        <p class="text-xs mt-1">O predicado exige: {{ predConfig.name }} {{ predConfig.p_type }} {{ predConfig.p_value }}</p>
                      </div>
                    </div>
                    
                    <Select 
                      v-model="predicateSelections[referent]"
                      @update:modelValue="(value: any) => value && updatePredicateSelection(referent, String(value))"
                      :disabled="getMatchingCredentialsForReferent(referent, predConfig.restrictions).length === 0"
                    >
                      <SelectTrigger 
                        class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-purple-600/50"
                        :disabled="getMatchingCredentialsForReferent(referent, predConfig.restrictions).length === 0"
                      >
                        <SelectValue placeholder="Escolha uma credencial">
                          <template v-if="predicateSelections[referent]">
                            <span class="text-sm">{{ getPredicateCredentialDisplayName(referent) }}</span>
                          </template>
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent class="bg-purple-900/95 backdrop-blur-md border-white/30 shadow-xl max-h-64">
                        <SelectGroup>
                          <SelectItem
                            v-for="cred in getMatchingCredentialsForReferent(referent, predConfig.restrictions)"
                            :key="cred.referent"
                            :value="cred.referent"
                            class="!text-white hover:!bg-purple-600/60 focus:!bg-purple-600/70 focus:!text-white data-[highlighted]:bg-purple-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors py-3"
                          >
                            <div class="flex flex-col gap-1">
                              <span class="font-medium text-sm">{{ formatCredentialLabel(cred) }}</span>
                              <span class="text-xs text-purple-300">Schema: {{ cred.schema_id.split(':').slice(-2).join(':') }}</span>
                            </div>
                          </SelectItem>
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-3 pt-4 border-t border-white/20">
                <Button 
                  @click="closeDetailView"
                  variant="outline"
                  class="border-purple-400/50 text-purple-200 hover:text-purple-200 bg-purple-600/20 hover:bg-purple-600/30 hover:border-purple-400 cursor-pointer"
                >
                  Cancelar
                </Button>
                <Button 
                  @click="submitProof"
                  :disabled="!canSubmitProof || appStore.isLoading || selectedRequest?.state !== 'request-received'"
                  class="bg-purple-600 hover:bg-purple-700 text-white cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send class="w-4 h-4 mr-2" />
                  Enviar Prova
                </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  RefreshCw, 
  ShieldCheck, 
  Eye, 
  ChevronLeft, 
  FileText, 
  AlertCircle,
  Calculator,
  Send
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { 
  Select, 
  SelectContent, 
  SelectGroup, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { useAppStore } from '@/stores/app'
import { useProofStore } from '@/stores/proof'
import type { ProofRequest, AvailableCredential, Restriction } from '@/stores/proof'

// Stores
const appStore = useAppStore()
const proofStore = useProofStore()

// Types for attribute selection
interface AttributeSelection {
  attrName: string
  credentialReferent: string | null
  value: string | null
  revealed: boolean
}

interface GroupedAttribute {
  groupKey: string
  displayName: string
  attributes: Array<{
    referent: string
    name: string
    restrictions?: Restriction[]
  }>
  isGroup: boolean
}

// State
const selectedRequest = ref<ProofRequest | null>(null)
const loadingCredentials = ref(false)
// Nova estrutura: Record<referent, Record<attrName, AttributeSelection>>
const attributeSelections = ref<Record<string, Record<string, AttributeSelection>>>({})
const predicateSelections = ref<Record<string, string>>({})

// Computed para agrupar atributos por prefixo
const groupedAttributes = computed(() => {
  if (!selectedRequest.value) return []
  
  const groups: GroupedAttribute[] = []
  const processedReferents = new Set<string>()
  const requestedAttrs = selectedRequest.value.requested_attributes
  
  // Primeiro, identifica grupos com 'names'
  Object.keys(requestedAttrs).forEach(referent => {
    const attrConfig = requestedAttrs[referent]
    if (attrConfig?.names && attrConfig.names.length > 0) {
      groups.push({
        groupKey: referent,
        displayName: referent,
        attributes: attrConfig.names.map((name: string) => ({
          referent,
          name,
          restrictions: attrConfig.restrictions
        })),
        isGroup: true
      })
      processedReferents.add(referent)
    }
  })
  
  // Agrupa atributos com mesmo prefixo (ex: dados_aluno_RA, dados_aluno_NomeAluno)
  const ungroupedReferents = Object.keys(requestedAttrs).filter(r => !processedReferents.has(r))
  const prefixMap = new Map<string, string[]>()
  
  ungroupedReferents.forEach(referent => {
    // Tenta encontrar um prefixo (parte antes do último underscore)
    const parts = referent.split('_')
    if (parts.length > 1) {
      const potentialPrefix = parts.slice(0, -1).join('_')
      // Verifica se existe outro atributo com o mesmo prefixo
      const hasSamePrefix = ungroupedReferents.some(r => 
        r !== referent && r.startsWith(potentialPrefix + '_')
      )
      
      if (hasSamePrefix) {
        if (!prefixMap.has(potentialPrefix)) {
          prefixMap.set(potentialPrefix, [])
        }
        prefixMap.get(potentialPrefix)!.push(referent)
      }
    }
  })
  
  // Cria grupos para os prefixos encontrados
  prefixMap.forEach((referents: string[], prefix: string) => {
    const attributes = referents.map((ref: string) => {
      const attrConfig = requestedAttrs[ref]
      const attrName = attrConfig?.name || ref.replace(prefix + '_', '')
      return {
        referent: ref,
        name: attrName,
        restrictions: attrConfig?.restrictions
      }
    })
    
    groups.push({
      groupKey: prefix,
      displayName: prefix,
      attributes,
      isGroup: true
    })
    
    referents.forEach((r: string) => processedReferents.add(r))
  })
  
  // Adiciona atributos individuais que não foram agrupados
  ungroupedReferents.forEach(referent => {
    if (!processedReferents.has(referent)) {
      const attrConfig = requestedAttrs[referent]
      if (attrConfig?.name) {
        groups.push({
          groupKey: referent,
          displayName: referent,
          attributes: [{
            referent,
            name: attrConfig.name,
            restrictions: attrConfig.restrictions
          }],
          isGroup: false
        })
      }
    }
  })
  
  return groups
})

// Computed
const canSubmitProof = computed(() => {
  if (!selectedRequest.value) return false
  
  // Verifica se todos os atributos de todos os grupos têm valor selecionado
  const allAttributesSelected = groupedAttributes.value.every((group: GroupedAttribute) => {
    return group.attributes.every((attr: any) => {
      const selection = attributeSelections.value[attr.referent]?.[attr.name]
      return selection?.credentialReferent && selection?.value
    })
  })
  
  // Verifica se todos os predicados têm uma credencial selecionada
  const allPredicatesSelected = Object.keys(selectedRequest.value.requested_predicates).every(
    referent => predicateSelections.value[referent]
  )
  
  return allAttributesSelected && allPredicatesSelected
})

// Methods
// Toggle de revelação para grupo
function getGroupRevealedForGroup(group: GroupedAttribute): boolean {
  return group.attributes.every(attr => {
    const selection = attributeSelections.value[attr.referent]?.[attr.name]
    return selection?.revealed !== false
  })
}

function setGroupRevealedForGroup(group: GroupedAttribute, revealed: boolean) {
  group.attributes.forEach(attr => {
    const attrSelection = attributeSelections.value[attr.referent]?.[attr.name]
    if (attrSelection) {
      attrSelection.revealed = revealed
    }
  })
}
async function loadProofRequests() {
  await proofStore.fetchProofRequests()
}

async function selectProofRequest(request: ProofRequest) {
  selectedRequest.value = request
  attributeSelections.value = {}
  predicateSelections.value = {}
  
  loadingCredentials.value = true
  await proofStore.fetchAvailableCredentials(request.pres_ex_id)
  loadingCredentials.value = false
  
  // Inicializa a estrutura de seleções usando os grupos
  groupedAttributes.value.forEach((group: GroupedAttribute) => {
    group.attributes.forEach((attr: any) => {
      if (!attributeSelections.value[attr.referent]) {
        attributeSelections.value[attr.referent] = {}
      }
      const selections = attributeSelections.value[attr.referent]
      if (selections) {
        selections[attr.name] = {
          attrName: attr.name,
          credentialReferent: null,
          value: null,
          revealed: true
        }
      }
    })
  })
}

function closeDetailView() {
  selectedRequest.value = null
  attributeSelections.value = {}
  predicateSelections.value = {}
}

// Nova função: retorna todas as opções disponíveis para um atributo específico
function getAvailableValuesForAttribute(
  referent: string,
  attrName: string,
  restrictions?: Restriction[]
): Array<{ credReferent: string; value: string; schemaName: string }> {
  if (!selectedRequest.value) return []
  
  const allCredentials = proofStore.availableCredentials[selectedRequest.value.pres_ex_id] || []
  
  // Filtra credenciais que têm o atributo solicitado e satisfazem as restrições
  const matchingCreds = allCredentials.filter((cred: AvailableCredential) => {
    // Verifica se tem o atributo
    if (!(attrName in cred.attrs)) return false
    
    // Verifica se tem o referent correto
    const hasReferent = cred.presentation_referents.includes(referent)
    if (!hasReferent) return false
    
    // Verifica restrições
    if (restrictions && restrictions.length > 0) {
      return restrictions.some((restriction: Restriction) => {
        if (restriction.schema_id && cred.schema_id !== restriction.schema_id) return false
        if (restriction.cred_def_id && cred.cred_def_id !== restriction.cred_def_id) return false
        return true
      })
    }
    
    return true
  })
  
  // Mapeia para o formato de opção
  return matchingCreds.map((cred: AvailableCredential) => ({
    credReferent: cred.referent,
    value: cred.attrs[attrName] || '',
    schemaName: cred.schema_id.split(':').slice(-2).join(':')
  }))
}

// Seleciona um valor para um atributo específico
function selectAttributeValue(referent: string, attrName: string, credReferent: string, group: GroupedAttribute) {
  if (!selectedRequest.value) return
  
  const credentials = proofStore.availableCredentials[selectedRequest.value.pres_ex_id] || []
  const selectedCred = credentials.find((c: AvailableCredential) => c.referent === credReferent)
  
  if (!selectedCred) return
  
  if (group.isGroup && group.attributes.length > 1) {
    group.attributes.forEach((attr: any) => {
      if (!attributeSelections.value[attr.referent]) {
        attributeSelections.value[attr.referent] = {}
      }
      
      if (attr.name in selectedCred.attrs) {
        const existingSelection = attributeSelections.value[attr.referent]?.[attr.name]
        const attrValue = selectedCred.attrs[attr.name]
        const selections = attributeSelections.value[attr.referent]
        if (selections) {
          selections[attr.name] = {
            attrName: attr.name,
            credentialReferent: credReferent,
            value: attrValue || null,
            revealed: existingSelection?.revealed ?? true
          }
        }
      }
    })
  } else {
    if (attrName in selectedCred.attrs) {
      if (!attributeSelections.value[referent]) {
        attributeSelections.value[referent] = {}
      }
      
      attributeSelections.value[referent][attrName] = {
        attrName,
        credentialReferent: credReferent,
        value: selectedCred.attrs[attrName] || null,
        revealed: attributeSelections.value[referent][attrName]?.revealed ?? true
      }
    }
  }
}

// Toggle revealed status
function toggleRevealed(referent: string, attrName: string, revealed: boolean) {
  if (attributeSelections.value[referent]?.[attrName]) {
    attributeSelections.value[referent][attrName].revealed = revealed
  }
}

function getMatchingCredentialsForReferent(
  referent: string, 
  restrictions?: Restriction[]
): AvailableCredential[] {
  if (!selectedRequest.value) return []
  
  let credentials = proofStore.getMatchingCredentials(
    selectedRequest.value.pres_ex_id,
    referent,
    restrictions
  )
  
  // Se for um predicado, filtra apenas credenciais que satisfazem o predicado
  const predConfig = selectedRequest.value.requested_predicates[referent]
  if (predConfig) {
    credentials = credentials.filter((cred: AvailableCredential) => 
      credentialSatisfiesPredicate(
        cred,
        predConfig.name,
        predConfig.p_type,
        predConfig.p_value
      )
    )
  }
  
  return credentials
}

function formatCredentialLabel(cred: AvailableCredential): string {
  // Tenta criar um label legível com base nos atributos
  const attrs: string[] = []
  for (const key in cred.attrs) {
    attrs.push(`${key}: ${cred.attrs[key]}`)
  }
  
  if (attrs.length === 0) {
    return cred.referent.substring(0, 8) + '...'
  }
  
  // Pega até 3 atributos para não ficar muito longo
  const maxAttrs = 3
  const displayAttrs = attrs.slice(0, maxAttrs).join(' | ')
  
  // Se tiver mais atributos, adiciona indicador
  const moreCount = attrs.length - maxAttrs
  if (moreCount > 0) {
    return `${displayAttrs} (+${moreCount})`
  }
  
  return displayAttrs
}

// Função para verificar se uma credencial satisfaz um predicado
function credentialSatisfiesPredicate(
  credential: AvailableCredential,
  predicateName: string,
  predicateType: string,
  predicateValue: number
): boolean {
  // Verifica se a credencial tem o atributo do predicado
  if (!(predicateName in credential.attrs)) {
    return false
  }
  
  const attrValue = credential.attrs[predicateName]
  if (!attrValue) {
    return false
  }
  
  // Converte o valor do atributo para número
  const numValue = parseInt(attrValue)
  
  if (isNaN(numValue)) {
    return false
  }
  
  // Verifica o predicado
  switch (predicateType) {
    case '>=':
      return numValue >= predicateValue
    case '>':
      return numValue > predicateValue
    case '<=':
      return numValue <= predicateValue
    case '<':
      return numValue < predicateValue
    default:
      return false
  }
}

function getPredicateCredentialDisplayName(referent: string): string {
  if (!selectedRequest.value || !predicateSelections.value[referent]) {
    return ''
  }
  
  const credentials = proofStore.availableCredentials[selectedRequest.value.pres_ex_id] || []
  const selectedCred = credentials.find((c: AvailableCredential) => c.referent === predicateSelections.value[referent])
  
  if (selectedCred) {
    return formatCredentialLabel(selectedCred)
  }
  
  return ''
}

function updatePredicateSelection(referent: string, credReferent: string) {
  predicateSelections.value[referent] = credReferent
}

async function submitProof() {
  if (!selectedRequest.value || !canSubmitProof.value) {
    console.warn('Cannot submit proof:', {
      hasRequest: !!selectedRequest.value,
      canSubmit: canSubmitProof.value
    })
    return
  }

  const requestedAttributes: Record<string, { cred_id: string; revealed: boolean }> = {}
  const requestedPredicates: Record<string, { cred_id: string; timestamp?: number }> = {}

  // Itera pelos grupos para construir a resposta correta
  groupedAttributes.value.forEach((group: GroupedAttribute) => {
    // Pega a primeira credencial selecionada do grupo (todas devem ser da mesma credencial)
    const firstAttr = group.attributes[0]
    if (!firstAttr) {
      console.warn(`Grupo ${group.groupKey} não tem atributos`)
      return
    }
    
    const firstSelection = attributeSelections.value[firstAttr.referent]?.[firstAttr.name]
    
    if (!firstSelection?.credentialReferent) {
      console.warn(`Grupo ${group.groupKey} não tem credencial selecionada`)
      return
    }

    const credId = firstSelection.credentialReferent

    // Para cada atributo do grupo, adiciona ao requestedAttributes
    group.attributes.forEach((attr: any) => {
      const selection = attributeSelections.value[attr.referent]?.[attr.name]
      if (selection) {
        requestedAttributes[attr.referent] = {
          cred_id: credId,
          revealed: selection.revealed ?? true
        }
        console.log(`Atributo ${attr.referent} adicionado:`, requestedAttributes[attr.referent])
      }
    })
  })

  for (const referent of Object.keys(selectedRequest.value.requested_predicates)) {
    const credId = predicateSelections.value[referent]
    if (credId) {
      requestedPredicates[referent] = { cred_id: credId }
      console.log(`Predicado ${referent} adicionado:`, requestedPredicates[referent])
    } else {
      console.error(`Predicado ${referent} não tem credencial selecionada!`)
    }
  }

  console.log('Enviando apresentação:', {
    requestedAttributes,
    requestedPredicates
  })

  const success = await proofStore.sendPresentation({
    pres_ex_id: selectedRequest.value.pres_ex_id,
    indy: {
      requested_attributes: requestedAttributes,
      requested_predicates: requestedPredicates,
      self_attested_attributes: {},
      trace: false
    },
    auto_remove: false
  })

  if (success) {
    closeDetailView()
    await loadProofRequests()
  } else {
    await loadProofRequests()
    const updatedRequest = proofStore.proofRequests.find(
      (pr: ProofRequest) => pr.pres_ex_id === selectedRequest.value?.pres_ex_id
    )
    if (updatedRequest) {
      selectedRequest.value = updatedRequest
    }
  }
}


function getStateColor(state: string): string {
  const stateColors: Record<string, string> = {
    'request-received': 'bg-blue-500/20 text-blue-200',
    'presentation-sent': 'bg-green-500/20 text-green-200',
    'verified': 'bg-green-500/20 text-green-200',
    'abandoned': 'bg-red-500/20 text-red-200',
    'done': 'bg-green-500/20 text-green-200'
  }
  return stateColors[state] || 'bg-gray-500/20 text-gray-200'
}

function getStateLabel(state: string): string {
  const stateLabels: Record<string, string> = {
    'request-received': 'Recebido',
    'presentation-sent': 'Enviado',
    'verified': 'Verificado',
    'abandoned': 'Abandonado',
    'done': 'Concluído'
  }
  return stateLabels[state] || state
}

// Lifecycle
onMounted(() => {
  loadProofRequests()
})
</script>

<style scoped>
/* Scrollbar customization */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgb(147, 51, 234);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgb(126, 34, 206);
}
</style>
