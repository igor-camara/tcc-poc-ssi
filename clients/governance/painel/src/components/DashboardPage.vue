<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="bg-slate-800/90 backdrop-blur-sm border border-slate-700 rounded-lg p-6 mb-6 shadow-xl">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold text-white mb-2">Painel de Governança</h1>
            <p class="text-slate-300">Gerenciamento de clientes e stewards</p>
          </div>
          <Button 
            @click="handleLogout"
            variant="outline"
            class="bg-slate-700 hover:bg-slate-600 text-white hover:text-white border-slate-600 cursor-pointer"
          >
            Sair
          </Button>
        </div>
      </div>

      <!-- Steward Selection -->
      <div class="bg-slate-800/90 backdrop-blur-sm border border-slate-700 rounded-lg p-6 mb-6 shadow-xl">
        <Label class="text-slate-200 font-medium text-sm mb-3 block">
          Selecionar Steward (Administrador)
        </Label>
        <Select v-model="selectedStewardId" @update:model-value="handleStewardChange">
          <SelectTrigger class="bg-slate-700/50 border-slate-600 text-white h-11 cursor-pointer">
            <SelectValue placeholder="Selecione um steward..." />
          </SelectTrigger>
          <SelectContent class="bg-slate-800 border-slate-700">
            <SelectItem 
              v-for="steward in stewardsStore.stewards" 
              :key="steward.id" 
              :value="steward.id"
              class="text-white hover:bg-slate-700 hover:text-white focus:bg-slate-700 focus:text-white cursor-pointer"
            >
              {{ steward.name }} - {{ steward.email }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Steward Information -->
      <div v-if="selectedSteward" class="bg-slate-800/90 backdrop-blur-sm border border-slate-700 rounded-lg p-6 mb-6 shadow-xl">
        <h2 class="text-xl font-bold text-white mb-4">Informações do Steward</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-slate-400 text-sm mb-1">Nome</p>
            <p class="text-white font-medium">{{ selectedSteward.name }}</p>
          </div>
          <div>
            <p class="text-slate-400 text-sm mb-1">Email</p>
            <p class="text-white font-medium">{{ selectedSteward.email }}</p>
          </div>
          <div>
            <p class="text-slate-400 text-sm mb-1">Organização</p>
            <p class="text-white font-medium">{{ selectedSteward.organization }}</p>
          </div>
          <div>
            <p class="text-slate-400 text-sm mb-1">Status</p>
            <span 
              class="inline-block px-3 py-1 rounded-full text-xs font-medium"
              :class="selectedSteward.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'"
            >
              {{ selectedSteward.status === 'active' ? 'Ativo' : 'Inativo' }}
            </span>
          </div>
          <div>
            <p class="text-slate-400 text-sm mb-1">Data de Criação</p>
            <p class="text-white font-medium">{{ formatDate(selectedSteward.created_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Clients List -->
      <div class="bg-slate-800/90 backdrop-blur-sm border border-slate-700 rounded-lg p-6 shadow-xl">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-white">Lista de Clientes</h2>
          <Button 
            @click="fetchClients"
            variant="outline"
            class="bg-slate-700 hover:bg-slate-600 text-white hover:text-white border-slate-600 cursor-pointer"
            :disabled="isLoadingClients"
          >
            <svg v-if="isLoadingClients" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Atualizar
          </Button>
        </div>

        <!-- Status Filter -->
        <div class="mb-6">
          <Label class="text-slate-200 font-medium text-sm mb-3 block">
            Filtrar por Status
          </Label>
          <Select v-model="statusFilter">
            <SelectTrigger class="bg-slate-700/50 border-slate-600 text-white h-11 max-w-xs cursor-pointer">
              <SelectValue placeholder="Todos os status" />
            </SelectTrigger>
            <SelectContent class="bg-slate-800 border-slate-700">
              <SelectItem value="all" class="text-white hover:text-white focus:text-white hover:bg-slate-700 focus:bg-slate-700 cursor-pointer">
                Todos os status
              </SelectItem>
              <SelectItem value="em_votacao" class="text-white hover:text-white focus:text-white hover:bg-slate-700 focus:bg-slate-700 cursor-pointer">
                Em Votação
              </SelectItem>
              <SelectItem value="aprovado" class="text-white hover:text-white focus:text-white hover:bg-slate-700 focus:bg-slate-700 cursor-pointer">
                Aprovado
              </SelectItem>
              <SelectItem value="rejeitado" class="text-white hover:text-white focus:text-white hover:bg-slate-700 focus:bg-slate-700 cursor-pointer">
                Rejeitado
              </SelectItem>
              <SelectItem value="pendente" class="text-white hover:text-white focus:text-white hover:bg-slate-700 focus:bg-slate-700 cursor-pointer">
                Pendente
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Clients Table -->
        <div v-if="isLoadingClients" class="text-center py-12">
          <svg class="animate-spin h-12 w-12 mx-auto text-slate-400 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-slate-400">Carregando clientes...</p>
        </div>

        <div v-else-if="filteredClients.length === 0" class="text-center py-12">
          <svg class="mx-auto h-16 w-16 text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="text-slate-400">Nenhum cliente encontrado</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-700">
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">Empresa</th>
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">CNPJ</th>
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">Email</th>
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">Tipo</th>
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">Status</th>
                <th class="text-left py-3 px-4 text-slate-300 font-medium text-sm">Data</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="client in filteredClients" 
                :key="client.id"
                @click="openVoteModal(client)"
                class="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors cursor-pointer"
              >
                <td class="py-3 px-4 text-white">{{ client.company_name }}</td>
                <td class="py-3 px-4 text-slate-300">{{ formatCNPJ(client.cnpj) }}</td>
                <td class="py-3 px-4 text-slate-300">{{ client.email }}</td>
                <td class="py-3 px-4">
                  <span class="inline-block px-2 py-1 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
                    {{ formatClientType(client.client_type) }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <span 
                    class="inline-block px-2 py-1 rounded text-xs font-medium"
                    :class="getStatusClass(client.status)"
                  >
                    {{ formatStatus(client.status) }}
                  </span>
                </td>
                <td class="py-3 px-4 text-slate-300 text-sm">{{ formatDate(client.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Vote Modal -->
    <Dialog v-model:open="isVoteModalOpen">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogTitle>Detalhes da Votação</DialogTitle>
        <DialogDescription>
          {{ selectedClient?.company_name }}
        </DialogDescription>

        <div v-if="isLoadingVotes" class="text-center py-8">
          <svg class="animate-spin h-10 w-10 mx-auto text-slate-400 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-slate-400">Carregando informações...</p>
        </div>

        <div v-else-if="voteData">
          <div class="bg-slate-700/50 rounded-lg p-4 mb-4">
            <h3 class="text-white font-semibold mb-3">Resumo da Votação</h3>
            <div class="grid grid-cols-4 gap-4 mb-4">
              <div>
                <p class="text-slate-400 text-xs mb-1">Total de Votos</p>
                <p class="text-white text-xl font-bold">{{ voteData.total_votes }}</p>
              </div>
              <div>
                <p class="text-slate-400 text-xs mb-1">Aprovações</p>
                <p class="text-green-400 text-xl font-bold">{{ voteData.approve_votes }}</p>
              </div>
              <div>
                <p class="text-slate-400 text-xs mb-1">Rejeições</p>
                <p class="text-red-400 text-xl font-bold">{{ voteData.reject_votes }}</p>
              </div>
              <div>
                <p class="text-slate-400 text-xs mb-1">Abstenções</p>
                <p class="text-gray-400 text-xl font-bold">{{ voteData.abstain_votes || 0 }}</p>
              </div>
            </div>
            
            <div v-if="voteData.first_vote_at || voteData.voting_deadline" class="grid grid-cols-2 gap-4 pt-4 border-t border-slate-600">
              <div v-if="voteData.first_vote_at">
                <p class="text-slate-400 text-xs mb-1">Início da Votação</p>
                <p class="text-white text-sm">{{ formatDate(voteData.first_vote_at) }}</p>
              </div>
              <div v-if="voteData.voting_deadline">
                <p class="text-slate-400 text-xs mb-1">Prazo Final</p>
                <p class="text-white text-sm" :class="votesStore.isVotingExpired(voteData.voting_deadline) ? 'text-red-400' : ''">
                  {{ formatDate(voteData.voting_deadline) }}
                  <span v-if="votesStore.isVotingExpired(voteData.voting_deadline)" class="text-red-400 text-xs ml-1">(Expirado)</span>
                </p>
              </div>
            </div>
          </div>

          <div v-if="voteData.votes.length > 0" class="mb-4">
            <h3 class="text-white font-semibold mb-3">Votos Registrados</h3>
            <div class="space-y-2">
              <div v-for="vote in voteData.votes" :key="vote.id" class="bg-slate-700/30 rounded p-3">
                <div class="flex justify-between items-start mb-2">
                  <span class="text-white font-medium">{{ vote.steward_name || stewardsStore.getStewardName(vote.steward_id) }}</span>
                  <span 
                    class="px-2 py-1 rounded text-xs font-medium"
                    :class="votesStore.getVoteBadgeClass(vote.vote)"
                  >
                    {{ votesStore.getVoteLabel(vote.vote) }}
                  </span>
                </div>
                <p v-if="vote.comment" class="text-slate-400 text-sm">{{ vote.comment }}</p>
                <p class="text-slate-500 text-xs mt-1">{{ formatDate(vote.created_at) }}</p>
              </div>
            </div>
          </div>

          <div v-if="stewardVote" class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-4">
            <h3 class="text-blue-400 font-semibold mb-2">Seu Voto</h3>
            <div class="flex items-center gap-2 mb-2">
              <span 
                class="px-2 py-1 rounded text-xs font-medium"
                :class="votesStore.getVoteBadgeClass(stewardVote.vote)"
              >
                {{ votesStore.getVoteLabel(stewardVote.vote) }}
              </span>
              <span class="text-slate-400 text-sm">em {{ formatDate(stewardVote.created_at) }}</span>
            </div>
            <p v-if="stewardVote.comment" class="text-slate-300 text-sm">{{ stewardVote.comment }}</p>
          </div>

          <div v-if="selectedClient?.status === 'em_votacao' && !stewardVote" class="border-t border-slate-700 pt-4">
            <h3 class="text-white font-semibold mb-3">Registrar seu Voto</h3>
            <div class="mb-4">
              <Label class="text-slate-200 text-sm mb-2 block">Comentário (opcional)</Label>
              <Textarea
                v-model="voteComment"
                placeholder="Adicione um comentário sobre sua decisão..."
                class="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 min-h-[80px]"
              />
            </div>
            <div class="flex gap-3">
              <Button
                @click="submitVote('approve')"
                :disabled="isSubmittingVote"
                class="flex-1 bg-green-600 hover:bg-green-700 text-white cursor-pointer"
              >
                <svg v-if="isSubmittingVote && voteAction === 'approve'" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Aprovar
              </Button>
              <Button
                @click="submitVote('abstain')"
                :disabled="isSubmittingVote"
                class="flex-1 bg-gray-600 hover:bg-gray-700 text-white cursor-pointer"
              >
                <svg v-if="isSubmittingVote && voteAction === 'abstain'" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Abster
              </Button>
              <Button
                @click="submitVote('reject')"
                :disabled="isSubmittingVote"
                class="flex-1 bg-red-600 hover:bg-red-700 text-white cursor-pointer"
              >
                <svg v-if="isSubmittingVote && voteAction === 'reject'" class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Rejeitar
              </Button>
            </div>
          </div>

          <div v-else-if="selectedClient?.status !== 'em_votacao'" class="text-center py-4">
            <p class="text-slate-400 text-sm">
              Este cliente não está mais em votação
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useStewardsStore } from '@/stores/stewards'
import { useVotesStore } from '@/stores/votes'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog'
import axiosInstance from '@/lib/axios'

const authStore = useAuthStore()
const stewardsStore = useStewardsStore()
const votesStore = useVotesStore()

const emit = defineEmits<{
  logout: []
}>()

// Types
interface Client {
  id: string
  company_name: string
  cnpj: string
  email: string
  client_type: string
  status: string
  created_at: string
}

// State
const selectedStewardId = ref<string>('')
const clients = ref<Client[]>([])
const statusFilter = ref<string>('all')
const isLoadingClients = ref(false)

const isVoteModalOpen = ref(false)
const selectedClient = ref<Client | null>(null)
const voteComment = ref('')
const voteAction = ref<'approve' | 'reject' | 'abstain' | null>(null)

// Computed
const selectedSteward = computed(() => {
  return stewardsStore.getStewardById(selectedStewardId.value)
})

const filteredClients = computed(() => {
  if (statusFilter.value === 'all') {
    return clients.value
  }
  return clients.value.filter(client => client.status === statusFilter.value)
})

const voteData = computed(() => votesStore.clientVotes)
const stewardVote = computed(() => {
  if (!selectedClient.value) return null
  return votesStore.getStewardVoteForClient(selectedClient.value.id)
})
const isLoadingVotes = computed(() => votesStore.isLoadingClientVotes || votesStore.isLoadingStewardVotes)
const isSubmittingVote = computed(() => votesStore.isSubmittingVote)

// Methods
async function fetchClients() {
  try {
    isLoadingClients.value = true
    const response = await axiosInstance.get('/clients')
    if (response.data.code === 'SUCCESS') {
      clients.value = response.data.data
    }
  } catch (error) {
    console.error('Erro ao buscar clientes:', error)
  } finally {
    isLoadingClients.value = false
  }
}

function handleStewardChange(stewardId: any) {
  if (stewardId && typeof stewardId === 'string') {
    selectedStewardId.value = stewardId
  }
}

function handleLogout() {
  authStore.logout()
  emit('logout')
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatCNPJ(cnpj: string): string {
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}

function formatClientType(type: string): string {
  const types: Record<string, string> = {
    'issuer': 'Emissor',
    'verifier': 'Verificador',
    'both': 'Emissor/Verificador'
  }
  return types[type] || type
}

function formatStatus(status: string): string {
  const statuses: Record<string, string> = {
    'em_votacao': 'Em Votação',
    'aprovado': 'Aprovado',
    'rejeitado': 'Rejeitado',
    'pendente': 'Pendente'
  }
  return statuses[status] || status
}

function getStatusClass(status: string): string {
  const classes: Record<string, string> = {
    'em_votacao': 'bg-yellow-500/20 text-yellow-400',
    'aprovado': 'bg-green-500/20 text-green-400',
    'rejeitado': 'bg-red-500/20 text-red-400',
    'pendente': 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || 'bg-gray-500/20 text-gray-400'
}

async function openVoteModal(client: Client) {
  selectedClient.value = client
  isVoteModalOpen.value = true
  voteComment.value = ''
  await loadVoteData()
}

async function loadVoteData() {
  if (!selectedClient.value || !selectedStewardId.value) return
  
  await Promise.all([
    votesStore.fetchClientVotes(selectedClient.value.id),
    votesStore.fetchStewardVotes(selectedStewardId.value)
  ])
}

async function submitVote(vote: 'approve' | 'reject' | 'abstain') {
  if (!selectedClient.value || !selectedStewardId.value) return
  
  voteAction.value = vote
  
  const success = await votesStore.submitVote({
    steward_id: selectedStewardId.value,
    client_id: selectedClient.value.id,
    vote: vote,
    comment: voteComment.value
  })
  
  if (success) {
    await loadVoteData()
    await fetchClients()
    voteComment.value = ''
  }
  
  voteAction.value = null
}

// Lifecycle
onMounted(async () => {
  await stewardsStore.fetchStewards()
  if (stewardsStore.stewards.length > 0 && stewardsStore.stewards[0]) {
    selectedStewardId.value = stewardsStore.stewards[0].id
  }
  fetchClients()
})
</script>
