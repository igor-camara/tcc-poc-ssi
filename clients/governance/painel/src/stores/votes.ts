import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '../lib/axios'
import { useAppStore } from './app'

export interface Vote {
  id: string
  steward_id: string
  steward_name?: string
  client_id: string
  vote: string
  comment: string
  created_at: string
}

export interface VoteData {
  client_id: string
  client_name: string
  status: string
  total_votes: number
  approve_votes: number
  reject_votes: number
  abstain_votes?: number
  first_vote_at?: string
  voting_deadline?: string
  votes: Vote[]
}

export interface VoteRequest {
  steward_id: string
  client_id: string
  vote: 'approve' | 'reject' | 'abstain'
  comment?: string
}

export const useVotesStore = defineStore('votes', () => {
  const appStore = useAppStore()
  const clientVotes = ref<VoteData | null>(null)
  const stewardVotes = ref<Vote[]>([])
  const isLoadingClientVotes = ref(false)
  const isLoadingStewardVotes = ref(false)
  const isSubmittingVote = ref(false)

  async function fetchClientVotes(clientId: string): Promise<VoteData | null> {
    try {
      isLoadingClientVotes.value = true
      const response = await axiosInstance.get(`/clients/${clientId}/votes`)
      if (response.data.code === 'SUCCESS') {
        clientVotes.value = response.data.data
        return response.data.data
      }
      return null
    } catch (error) {
      console.error('Erro ao buscar votos do cliente:', error)
      appStore.addNotification('Erro ao carregar votos do cliente', 'error')
      return null
    } finally {
      isLoadingClientVotes.value = false
    }
  }

  async function fetchStewardVotes(stewardId: string): Promise<Vote[]> {
    try {
      isLoadingStewardVotes.value = true
      const response = await axiosInstance.get(`/stewards/${stewardId}/votes`)
      if (response.data.code === 'SUCCESS') {
        stewardVotes.value = response.data.data
        return response.data.data
      }
      return []
    } catch (error) {
      console.error('Erro ao buscar votos do steward:', error)
      appStore.addNotification('Erro ao carregar votos do steward', 'error')
      return []
    } finally {
      isLoadingStewardVotes.value = false
    }
  }

  async function submitVote(voteRequest: VoteRequest): Promise<boolean> {
    try {
      isSubmittingVote.value = true
      const response = await axiosInstance.post('/stewards/votes', voteRequest)
      
      if (response.data.code === 'SUCCESS') {
        appStore.addNotification('Voto registrado com sucesso!', 'success')
        return true
      }
      return false
    } catch (error: any) {
      console.error('Erro ao enviar voto:', error)
      const errorMessage = error.response?.data?.message || 'Erro ao registrar voto'
      appStore.addNotification(errorMessage, 'error')
      return false
    } finally {
      isSubmittingVote.value = false
    }
  }

  function getStewardVoteForClient(clientId: string): Vote | null {
    return stewardVotes.value.find(v => v.client_id === clientId) || null
  }

  function getVoteBadgeClass(vote: string): string {
    const classes: Record<string, string> = {
      'approve': 'bg-green-500/20 text-green-400',
      'reject': 'bg-red-500/20 text-red-400',
      'abstain': 'bg-gray-500/20 text-gray-400'
    }
    return classes[vote] || 'bg-gray-500/20 text-gray-400'
  }

  function getVoteLabel(vote: string): string {
    const labels: Record<string, string> = {
      'approve': 'Aprovado',
      'reject': 'Rejeitado',
      'abstain': 'Abstenção'
    }
    return labels[vote] || vote
  }

  function isVotingExpired(deadline: string): boolean {
    return new Date(deadline) < new Date()
  }

  return {
    clientVotes,
    stewardVotes,
    isLoadingClientVotes,
    isLoadingStewardVotes,
    isSubmittingVote,
    fetchClientVotes,
    fetchStewardVotes,
    submitVote,
    getStewardVoteForClient,
    getVoteBadgeClass,
    getVoteLabel,
    isVotingExpired
  }
})
