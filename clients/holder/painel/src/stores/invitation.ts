import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface CreateConnectionRequest {
  alias: string
  url: string
  user_did: string
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
      const response = await axiosInstance.post('/invitation/create', { alias })

      if (response.data.code === 'SUCCESS') {
        const invitation = response.data.data
        
        // Add to pending invitations
        pendingInvitations.value.push(invitation)
        
        appStore.addNotification('Convite criado com sucesso!', 'success')
        return invitation
      } else {
        throw new Error(response.data.data || 'Erro ao criar convite')
      }
    })

    return result
  }

  async function accept(invitationId: string): Promise<boolean> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post(`/invitation/${invitationId}/accept`)

      if (response.data.code === 'SUCCESS') {
        // Remove from pending invitations
        const index = pendingInvitations.value.findIndex(inv => inv.connection_id === invitationId)
        if (index > -1) {
          pendingInvitations.value.splice(index, 1)
        }
        
        appStore.addNotification('Convite aceito com sucesso!', 'success')
        return true
      } else {
        throw new Error(response.data.data || 'Erro ao aceitar convite')
      }
    })

    return result !== null
  }

  async function reject(invitationId: string): Promise<boolean> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post(`/invitation/${invitationId}/reject`)

      if (response.data.code === 'SUCCESS') {
        // Remove from pending invitations
        const index = pendingInvitations.value.findIndex(inv => inv.connection_id === invitationId)
        if (index > -1) {
          pendingInvitations.value.splice(index, 1)
        }
        
        appStore.addNotification('Convite rejeitado', 'info')
        return true
      } else {
        throw new Error(response.data.data || 'Erro ao rejeitar convite')
      }
    })

    return result !== null
  }

  async function getQrCode(invitationId: string): Promise<string | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get(`/invitation/${invitationId}/qr-code`)

      if (response.data.code === 'SUCCESS') {
        return response.data.data.qr_code_base64
      } else {
        throw new Error(response.data.data || 'Erro ao gerar QR Code')
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
    accept,
    reject,
    getQrCode,
    clearPendingInvitations,
  }
})