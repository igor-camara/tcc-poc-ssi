<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4 pr-2">
      <div class="flex-1">
        <h2 class="text-2xl font-bold text-white mb-2">Proof Requests</h2>
        <p class="text-blue-100">Gerencie e envie solicitações de prova para holders</p>
      </div>
      <div class="flex-shrink-0">
        <Button @click="toggleFormVisibility" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
          <Plus v-if="!showForm" class="w-4 h-4 mr-2" />
          <X v-else class="w-4 h-4 mr-2" />
          {{ showForm ? 'Cancelar' : 'Nova Solicitação' }}
        </Button>
      </div>
    </div>

    <!-- Novo Formulário (Colapsável) -->
    <div v-if="showForm" class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-6">
      <h3 class="text-xl font-semibold text-white mb-4">Nova Solicitação de Prova</h3>
      
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <!-- Informações Básicas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Conexão *</label>
            <Select v-model="form.connection_id" class="w-full cursor-pointer">
              <SelectTrigger class="w-full bg-blue-900/40 border border-blue-700 text-white focus:ring-blue-500">
                <SelectValue class="text-blue-200 cursor-pointer" placeholder="Selecione uma conexão ativa" />
              </SelectTrigger>
              <SelectContent class="bg-blue-950 border-blue-700">
                <SelectGroup>
                  <SelectItem v-for="conn in activeConnections" :key="conn.connection_id" :value="conn.connection_id" class="cursor-pointer hover:bg-blue-800/60 focus:bg-blue-700/80 focus:text-white hover:text-white text-white">
                    {{ conn.alias || conn.connection_id }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Nome da Solicitação *</label>
            <Input v-model="form.name" type="text" placeholder="Ex: Verificação KYC" required class="bg-blue-900/40 border border-blue-700 text-white placeholder:text-blue-300 focus:ring-blue-500" />
          </div>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-white">Versão</label>
          <Input v-model="form.version" type="text" placeholder="1.0" class="bg-blue-900/40 border border-blue-700 text-white placeholder:text-blue-300 focus:ring-blue-500 max-w-xs" />
        </div>

        <!-- Tabs para Atributos e Predicados -->
        <Tabs default-value="attributes" class="w-full">
          <TabsList class="grid w-full grid-cols-2 bg-blue-900/40">
            <TabsTrigger value="attributes" class="data-[state=active]:bg-blue-700 data-[state=active]:text-white cursor-pointer">
              Atributos Solicitados
            </TabsTrigger>
            <TabsTrigger value="predicates" class="data-[state=active]:bg-blue-700 data-[state=active]:text-white cursor-pointer">
              Predicados
            </TabsTrigger>
          </TabsList>

          <!-- Tab de Atributos -->
          <TabsContent value="attributes" class="space-y-4 mt-4">
            <div class="flex justify-between items-center">
              <p class="text-sm text-blue-200">Defina quais atributos você deseja solicitar do holder</p>
              <Button type="button" @click="addAttributeKey" size="sm" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                <Plus class="w-4 h-4 mr-1" /> Adicionar Grupo
              </Button>
            </div>

            <div v-if="form.requested_attributes.length === 0" class="text-center py-8 text-blue-300">
              Nenhum atributo adicionado. Clique em "Adicionar Grupo" para começar.
            </div>

            <div v-for="(attrKey, idx) in form.requested_attributes" :key="idx" class="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <div class="flex gap-3 items-start mb-3">
                <div class="flex-1">
                  <label class="text-xs text-blue-200 mb-1 block">Chave do Grupo</label>
                  <Input v-model="attrKey.key" placeholder="Ex: dados_pessoais" class="bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500" />
                </div>
                <div class="flex gap-2 pt-6">
                  <Button type="button" @click="openSchemaModal(idx, 'attribute')" size="sm" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">
                    <FileSearch class="w-4 h-4 mr-1" /> Schema
                  </Button>
                  <Button type="button" @click="removeAttributeKey(idx)" size="sm" variant="ghost" class="text-red-400 hover:text-white hover:bg-red-700/30 cursor-pointer">
                    <Trash2 class="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div v-if="attrKey.restrictions && attrKey.restrictions.length" class="mb-3">
                <div class="text-xs text-blue-300 bg-blue-900/60 rounded px-3 py-2 border border-blue-700 font-mono">
                  Schema: {{ attrKey.restrictions[0]?.schema_id }}
                </div>
              </div>

              <div class="space-y-2 ml-2">
                <label class="text-xs text-blue-200">Nomes dos Atributos</label>
                <div v-for="(_, nIdx) in attrKey.names" :key="nIdx" class="flex gap-2 items-center">
                  <Input v-model="attrKey.names[nIdx]" placeholder="Ex: nome, cpf, data_nascimento" class="bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500" />
                  <Button type="button" @click="removeAttributeName(idx, nIdx)" size="sm" variant="ghost" class="text-red-400 hover:text-white hover:bg-red-700/30 cursor-pointer">
                    <X class="w-4 h-4" />
                  </Button>
                </div>
                <Button type="button" @click="addAttributeName(idx)" size="sm" variant="ghost" class="text-blue-300 hover:text-white hover:bg-blue-700/40 cursor-pointer">
                  <Plus class="w-3 h-3 mr-1" /> Adicionar Atributo
                </Button>
              </div>
            </div>
          </TabsContent>

          <!-- Tab de Predicados -->
          <TabsContent value="predicates" class="space-y-4 mt-4">
            <div class="flex justify-between items-center">
              <p class="text-sm text-blue-200">Defina condições lógicas sobre os atributos (ex: idade >= 18)</p>
              <Button type="button" @click="addPredicateKey" size="sm" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                <Plus class="w-4 h-4 mr-1" /> Adicionar Grupo
              </Button>
            </div>

            <div v-if="form.requested_predicates.length === 0" class="text-center py-8 text-blue-300">
              Nenhum predicado adicionado. Clique em "Adicionar Grupo" para começar.
            </div>

            <div v-for="(predKey, idx) in form.requested_predicates" :key="idx" class="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <div class="flex gap-3 items-start mb-3">
                <div class="flex-1">
                  <label class="text-xs text-blue-200 mb-1 block">Chave do Grupo</label>
                  <Input v-model="predKey.key" placeholder="Ex: verificacao_idade" class="bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500" />
                </div>
                <div class="flex gap-2 pt-6">
                  <Button type="button" @click="openSchemaModal(idx, 'predicate')" size="sm" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">
                    <FileSearch class="w-4 h-4 mr-1" /> Schema
                  </Button>
                  <Button type="button" @click="removePredicateKey(idx)" size="sm" variant="ghost" class="text-red-400 hover:text-white hover:bg-red-700/30 cursor-pointer">
                    <Trash2 class="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div v-if="predKey.restrictions && predKey.restrictions.length" class="mb-3">
                <div class="text-xs text-blue-300 bg-blue-900/60 rounded px-3 py-2 border border-blue-700 font-mono">
                  Schema: {{ predKey.restrictions[0]?.schema_id }}
                </div>
              </div>

              <div class="space-y-2 ml-2">
                <label class="text-xs text-blue-200">Predicados</label>
                <div v-for="(pred, pIdx) in predKey.predicates" :key="pIdx" class="flex gap-2 items-center">
                  <Input v-model="pred.name" placeholder="Atributo" class="bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500 flex-1" />
                  <Select v-model="pred.p_type" class="w-24">
                    <SelectTrigger class="bg-blue-900/60 border border-blue-700 text-white">
                      <SelectValue class="text-blue-200" placeholder="Op" />
                    </SelectTrigger>
                    <SelectContent class="bg-blue-950 border-blue-700">
                      <SelectGroup>
                        <SelectItem class="cursor-pointer text-white" value=">=">&ge;</SelectItem>
                        <SelectItem class="cursor-pointer text-white" value=">">&gt;</SelectItem>
                        <SelectItem class="cursor-pointer text-white" value="<=">&le;</SelectItem>
                        <SelectItem class="cursor-pointer text-white" value="<">&lt;</SelectItem>
                        <SelectItem class="cursor-pointer text-white" value="==">=</SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                  <Input v-model="pred.p_value" placeholder="Valor" type="number" class="bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500 w-24" />
                  <Button type="button" @click="removePredicate(idx, pIdx)" size="sm" variant="ghost" class="text-red-400 hover:text-white hover:bg-red-700/30 cursor-pointer">
                    <X class="w-4 h-4" />
                  </Button>
                </div>
                <Button type="button" @click="addPredicate(idx)" size="sm" variant="ghost" class="text-blue-300 hover:text-white hover:bg-blue-700/40 cursor-pointer">
                  <Plus class="w-3 h-3 mr-1" /> Adicionar Predicado
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <!-- Botões -->
        <div class="flex justify-end gap-3 pt-4 border-t border-blue-700/30">
          <Button type="button" @click="resetForm" class="bg-blue-600 border-blue-600 text-white hover:bg-blue-700 cursor-pointer">
            Limpar
          </Button>
          <Button type="submit" :disabled="!isFormValid" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white disabled:opacity-50 disabled:cursor-not-allowed">
            <Send class="w-4 h-4 mr-2" />
            Enviar Solicitação
          </Button>
        </div>
      </form>
    </div>

    <!-- Filtros e Busca -->
    <div v-if="!showForm" class="flex gap-4 pr-2">
      <div class="flex-1 min-w-0">
        <Input v-model="searchTerm" placeholder="Buscar por nome ou connection..." class="bg-white/20 border-white/30 text-white placeholder:text-blue-100" />
      </div>
      <div class="w-40 flex-shrink-0">
        <Select v-model="stateFilter" default-value="all">
          <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-blue-600/50 data-[placeholder]:text-blue-100">
            <SelectValue placeholder="Filtrar por estado" />
          </SelectTrigger>
          <SelectContent class="bg-blue-900/95 backdrop-blur-md border-white/30 shadow-xl">
            <SelectGroup>
              <SelectItem value="all" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Todos</SelectItem>
              <SelectItem value="request-sent" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Enviado</SelectItem>
              <SelectItem value="presentation-received" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Recebido</SelectItem>
              <SelectItem value="done" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Concluído</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Lista de Proof Requests Existentes -->
    <div v-if="!showForm" class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-blue-600 scrollbar-track-white/10">
      <div v-if="filteredProofExchanges.length === 0 && !appStore.isLoading" class="text-center py-12 text-blue-300">
        <FileSearch class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Nenhum proof request encontrado</p>
      </div>

      <div v-for="exchange in filteredProofExchanges" :key="exchange.pres_ex_id" class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-5 hover:bg-white/15 transition-all duration-200">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-white">{{ exchange.pres_request.name }}</h3>
              <span :class="getStateBadgeClass(exchange.state)" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ getStateLabel(exchange.state) }}
              </span>
              <span v-if="exchange.verified !== null" :class="exchange.verified === 'true' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ exchange.verified === 'true' ? '✓ Verificado' : '✗ Não Verificado' }}
              </span>
            </div>
            <div class="text-sm space-y-1">
              <div class="text-blue-200">
                <span class="font-medium">Conexão:</span>
                <span class="ml-2 text-white">{{ getConnectionAlias(exchange.connection_id) }}</span>
              </div>
              <div class="text-blue-200">
                <span class="font-medium">Criado em:</span>
                <span class="ml-2 text-white">{{ formatDate(exchange.created_at) }}</span>
              </div>
              <div v-if="exchange.updated_at !== exchange.created_at" class="text-blue-200">
                <span class="font-medium">Atualizado em:</span>
                <span class="ml-2 text-white">{{ formatDate(exchange.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Mensagens de Erro de Verificação -->
        <div v-if="exchange.verified === 'false' && exchange.verified_msgs && exchange.verified_msgs.length > 0" class="mb-4 bg-red-900/20 border border-red-500/40 rounded-lg p-4">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h4 class="text-sm font-semibold text-red-300 mb-2">Falha na Verificação</h4>
              <p class="text-xs text-red-200/80 mb-3">A prova apresentada pelo holder não atende aos requisitos solicitados:</p>
              <ul class="space-y-2">
                <li v-for="(msg, idx) in exchange.verified_msgs" :key="idx" class="text-xs text-red-200 bg-red-900/30 rounded px-3 py-2 flex items-start gap-2">
                  <span class="text-red-400 flex-shrink-0 font-bold">→</span>
                  <span class="flex-1">{{ formatErrorMessage(msg) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Atributos e Predicados Solicitados -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-blue-700/30">
          <div v-if="Object.keys(exchange.pres_request.requested_attributes).length > 0">
            <h4 class="text-sm font-medium text-blue-200 mb-2">Atributos Solicitados:</h4>
            <div class="space-y-1">
              <div v-for="(attr, key) in exchange.pres_request.requested_attributes" :key="key" class="text-xs bg-blue-900/40 rounded px-2 py-1 text-white">
                <span class="font-medium text-blue-300">{{ key }}:</span>
                <span v-if="attr.name" class="ml-1">{{ attr.name }}</span>
                <span v-else-if="attr.names" class="ml-1">{{ attr.names.join(', ') }}</span>
              </div>
            </div>
          </div>
          <div v-if="Object.keys(exchange.pres_request.requested_predicates).length > 0">
            <h4 class="text-sm font-medium text-blue-200 mb-2">Predicados:</h4>
            <div class="space-y-1">
              <div v-for="(pred, key) in exchange.pres_request.requested_predicates" :key="key" class="text-xs bg-blue-900/40 rounded px-2 py-1 text-white">
                <span class="font-medium text-blue-300">{{ key }}:</span>
                <span class="ml-1">{{ pred.name }} {{ pred.p_type }} {{ pred.p_value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Atributos Revelados pelo Holder -->
        <div v-if="exchange.pres && exchange.pres.revealed_attrs && Object.keys(exchange.pres.revealed_attrs).length > 0" class="mt-4">
          <h4 class="text-base font-bold text-green-400 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            Atributos Revelados
          </h4>
          <ul class="space-y-2">
            <li v-for="(attr, key) in exchange.pres.revealed_attrs" :key="key" class="flex items-center gap-3 bg-green-900/30 border border-green-700/40 rounded-lg px-4 py-2">
              <span class="font-semibold text-green-300">{{ key }}:</span>
              <span class="text-white text-sm">{{ attr.raw }}</span>
            </li>
          </ul>
        </div>

        <!-- Atributos Não Revelados pelo Holder -->
        <div v-if="exchange.pres && exchange.pres.unrevealed_attrs && Object.keys(exchange.pres.unrevealed_attrs).length > 0" class="mt-4">
          <h4 class="text-base font-bold text-yellow-400 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01" /></svg>
            Atributos Não Revelados
          </h4>
          <ul class="space-y-2">
            <li v-for="(_, key) in exchange.pres.unrevealed_attrs" :key="key" class="flex items-center gap-3 bg-yellow-900/30 border border-yellow-700/40 rounded-lg px-4 py-2">
              <span class="font-semibold text-yellow-300">{{ key }}:</span>
              <span class="text-white text-sm">Não revelado pelo holder</span>
            </li>
          </ul>
        </div>

        <!-- Predicados Apresentados -->
        <div v-if="exchange.pres && exchange.pres.predicates && Object.keys(exchange.pres.predicates).length > 0 && exchange.pres_request && exchange.pres_request.requested_predicates" class="mt-4">
          <h4 class="text-base font-bold text-blue-400 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 17l-4 4m0 0l-4-4m4 4V3" /></svg>
            Predicados Apresentados
          </h4>
          <ul class="space-y-2">
            <li v-for="(_, key) in exchange.pres.predicates" :key="key" class="bg-blue-900/30 border border-blue-700/40 rounded-lg px-4 py-2">
              <span class="text-blue-300 font-semibold">{{ key }}:</span>
              <span class="text-white text-sm">
                <template v-if="exchange.pres_request.requested_predicates[key]">
                  <!-- Monta frase explicativa -->
                  O atributo <b>{{ exchange.pres_request.requested_predicates[key].name }}</b> foi apresentado conforme solicitado:
                  <b>{{ exchange.pres_request.requested_predicates[key].name }}</b>
                  <b>{{ exchange.pres_request.requested_predicates[key].p_type }}</b>
                  <b>{{ exchange.pres_request.requested_predicates[key].p_value }}</b>
                </template>
                <template v-else>
                  Predicado apresentado
                </template>
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Modal de busca de schemas -->
    <SchemaSearchModal v-if="showSchemaModal" :onSelect="handleSchemaSelect" :onClose="closeSchemaModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Trash2, X, Send, FileSearch } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useConnectionStore, useProofStore, useAppStore } from '@/stores'
import SchemaSearchModal from '@/components/SchemaSearchModal.vue'

const proofStore = useProofStore()
const connectionStore = useConnectionStore()
const appStore = useAppStore()

// UI State
const showForm = ref(false)
const searchTerm = ref('')
const stateFilter = ref('all')

// Interfaces
interface RequestedAttribute {
  key: string
  names: string[]
  restrictions?: Array<{ schema_id: string }>
}

interface RequestedPredicate {
  key: string
  predicates: Array<{
    name: string
    p_type: string
    p_value: string | number
  }>
  restrictions?: Array<{ schema_id: string }>
}

interface ProofRequestForm {
  connection_id: string
  name: string
  version: string
  requested_attributes: RequestedAttribute[]
  requested_predicates: RequestedPredicate[]
}

// Form State
const form = ref<ProofRequestForm>({
  connection_id: '',
  name: '',
  version: '1.0',
  requested_attributes: [],
  requested_predicates: []
})

// Schema Modal State
const showSchemaModal = ref(false)
const schemaModalIndex = ref(-1)
const schemaModalType = ref('attribute')

// Computed
const activeConnections = computed(() =>
  connectionStore.connections.filter(c => c.state === 'active' || c.state === 'response')
)

const isFormValid = computed(() => {
  return form.value.connection_id && form.value.name.trim() !== ''
})

const filteredProofExchanges = computed(() => {
  let filtered = proofStore.proofExchanges

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(
      ex =>
        ex.pres_request.name.toLowerCase().includes(search) ||
        ex.connection_id.toLowerCase().includes(search) ||
        getConnectionAlias(ex.connection_id).toLowerCase().includes(search)
    )
  }

  // Filter by state
  if (stateFilter.value !== 'all') {
    filtered = filtered.filter(ex => ex.state === stateFilter.value)
  }

  return filtered
})

// UI Actions
function toggleFormVisibility() {
  showForm.value = !showForm.value
  if (!showForm.value) {
    resetForm()
  }
}

function resetForm() {
  form.value = {
    connection_id: '',
    name: '',
    version: '1.0',
    requested_attributes: [],
    requested_predicates: []
  }
}

// Attribute Actions
function addAttributeKey() {
  form.value.requested_attributes.push({ key: '', names: [''], restrictions: [] })
}

function removeAttributeKey(idx: number) {
  form.value.requested_attributes.splice(idx, 1)
}

function addAttributeName(attrIdx: number) {
  const attr = form.value.requested_attributes[attrIdx]
  if (attr) {
    attr.names.push('')
  }
}

function removeAttributeName(attrIdx: number, nameIdx: number) {
  const attr = form.value.requested_attributes[attrIdx]
  if (attr) {
    attr.names.splice(nameIdx, 1)
  }
}

// Predicate Actions
function addPredicateKey() {
  form.value.requested_predicates.push({ key: '', predicates: [{ name: '', p_type: '>=', p_value: '' }], restrictions: [] })
}

function removePredicateKey(idx: number) {
  form.value.requested_predicates.splice(idx, 1)
}

function addPredicate(idx: number) {
  const predKey = form.value.requested_predicates[idx]
  if (predKey) {
    predKey.predicates.push({ name: '', p_type: '>=', p_value: '' })
  }
}

function removePredicate(idx: number, pIdx: number) {
  const predKey = form.value.requested_predicates[idx]
  if (predKey) {
    predKey.predicates.splice(pIdx, 1)
  }
}

// Schema Modal Actions
function openSchemaModal(idx: number, type: string) {
  schemaModalIndex.value = idx
  schemaModalType.value = type
  showSchemaModal.value = true
}

function closeSchemaModal() {
  showSchemaModal.value = false
}

function handleSchemaSelect(schema: any) {
  if (schemaModalType.value === 'attribute') {
    const attr = form.value.requested_attributes[schemaModalIndex.value]
    if (attr) attr.restrictions = [{ schema_id: schema.id }]
  } else {
    const pred = form.value.requested_predicates[schemaModalIndex.value]
    if (pred) pred.restrictions = [{ schema_id: schema.id }]
  }
  closeSchemaModal()
}

// Form Submit
async function handleSubmit() {
  const requested_attributes: Record<string, any> = {}
  for (const attr of form.value.requested_attributes) {
    if (attr.key && attr.names.length) {
      const filteredNames = attr.names.filter(n => n && n.trim())
      if (filteredNames.length === 0) continue

      if (filteredNames.length === 1) {
        requested_attributes[attr.key] = {
          name: filteredNames[0],
          restrictions: attr.restrictions && attr.restrictions.length ? attr.restrictions : undefined
        }
      } else {
        requested_attributes[attr.key] = {
          names: filteredNames,
          restrictions: attr.restrictions && attr.restrictions.length ? attr.restrictions : undefined
        }
      }
    }
  }

  const requested_predicates: Record<string, any> = {}
  for (const pred of form.value.requested_predicates) {
    if (pred.key && pred.predicates.length) {
      const filteredPredicates = pred.predicates.filter(p => p.name && p.p_type && p.p_value !== '')
      if (filteredPredicates.length === 0) continue

      if (filteredPredicates.length === 1) {
        const p = filteredPredicates[0]
        if (p) {
          requested_predicates[pred.key] = {
            name: p.name,
            p_type: p.p_type,
            p_value: Number(p.p_value),
            restrictions: pred.restrictions && pred.restrictions.length ? pred.restrictions : undefined
          }
        }
      } else {
        requested_predicates[pred.key] = filteredPredicates.map(p => {
          if (!p) return null
          return {
            name: p.name,
            p_type: p.p_type,
            p_value: Number(p.p_value),
            restrictions: pred.restrictions && pred.restrictions.length ? pred.restrictions : undefined
          }
        }).filter(p => p !== null)
      }
    }
  }

  const payload = {
    connection_id: form.value.connection_id,
    proof_request: {
      name: form.value.name,
      version: form.value.version,
      requested_attributes,
      requested_predicates
    }
  }

  const result = await proofStore.sendProofRequest(payload)

  if (result !== null) {
    resetForm()
    showForm.value = false
  }
}

// Helper Functions
function getConnectionAlias(connectionId: string): string {
  const conn = connectionStore.connections.find(c => c.connection_id === connectionId)
  return conn?.alias || connectionId
}

function getStateBadgeClass(state: string): string {
  const classes: Record<string, string> = {
    'request-sent': 'bg-blue-500/20 text-blue-300',
    'presentation-received': 'bg-yellow-500/20 text-yellow-300',
    'done': 'bg-green-500/20 text-green-300',
    'abandoned': 'bg-gray-500/20 text-gray-300'
  }
  return classes[state] || 'bg-gray-500/20 text-gray-300'
}

function getStateLabel(state: string): string {
  const labels: Record<string, string> = {
    'request-sent': 'Enviado',
    'presentation-received': 'Recebido',
    'done': 'Concluído',
    'abandoned': 'Abandonado'
  }
  return labels[state] || state
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

function formatErrorMessage(msg: string): string {
  // Formata mensagens de erro técnicas para português
  const translations: Record<string, string> = {
    'VALUE_ERROR': 'Erro de Valor',
    'Missing requested attribute group': 'Grupo de atributos não fornecido',
    'RMV_GLB_NRI': 'Falha na validação da prova',
    'ENCODING_ERROR': 'Erro de codificação',
    'MISSING_ESSENTIAL_ATTRIBUTES': 'Atributos essenciais faltando',
    'INVALID_PREDICATE': 'Predicado inválido',
    'SCHEMA_MISMATCH': 'Schema incompatível',
    'CREDENTIAL_REVOKED': 'Credencial revogada'
  }
  
  let formatted = msg
  for (const [key, value] of Object.entries(translations)) {
    formatted = formatted.replace(new RegExp(key, 'gi'), value)
  }
  
  // Remove :: e substitui por :
  formatted = formatted.replace('::', ': ')
  
  return formatted
}

// Lifecycle
onMounted(async () => {
  await connectionStore.fetchAll()
  await proofStore.fetchAll({ descending: true, limit: 100, offset: 0 })
})
</script>
