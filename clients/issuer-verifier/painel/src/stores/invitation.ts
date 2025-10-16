import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface CreateConnectionRequest {
  alias: string
  url: string
}

export interface InvitationResponse {
  connection_id: string
  invitation_url: string
  invitation: any
}

export const useInvitationStore = defineStore('invitation', () => {
  // State
  const pendingInvitations = ref<InvitationResponse[]>([])

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Actions
  async function receiveByUrl(request: CreateConnectionRequest): Promise<InvitationResponse | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post('/invitation/receive-url', request)

      if (response.data.code === 'SUCCESS') {
        const invitation = response.data.data
        
        // Add to pending invitations
        pendingInvitations.value.push(invitation)
        
        appStore.addNotification('Conexão criada com sucesso!', 'success')
        return invitation
      } else {
        throw new Error(response.data.data || 'Erro ao criar conexão')
      }
    })

    return result
  }

  async function create(alias: string): Promise<InvitationResponse | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post('/invitation/create-url', null, {
        params: { alias }
      })

      if (response.data.code === 'SUCCESS') {
        const invitation = response.data.data
        
        // Add to pending invitations
        pendingInvitations.value.push(invitation)
        
        appStore.addNotification('URL de convite gerada com sucesso!', 'success')
        return invitation
      } else {
        throw new Error(response.data.data || 'Erro ao gerar URL de convite')
      }
    })

    return result
  }

  function clearPendingInvitations() {
    pendingInvitations.value = []
  }

  return {
    // State
    pendingInvitations,
    // Actions
    receiveByUrl,
    create,
    clearPendingInvitations,
  }
})