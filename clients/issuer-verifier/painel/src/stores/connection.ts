import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface Connection {
  alias: string
  connection_id: string
  created_at: string
  updated_at: string
  invitation_key: string
  state: string
  my_did: string
  their_did?: string
  their_label?: string
}

export const useConnectionStore = defineStore('connection', () => {
  // State
  const connections = ref<Connection[]>([])

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Actions
  async function fetchAll(params?: { alias?: string; id?: string }): Promise<Connection[] | null> {
    const result = await appStore.makeApiCall(async () => {
      let url = '/connections'
      
      // Adicionar parâmetros de busca se fornecidos (alias OU id, não ambos)
      if (params?.alias) {
        url += `?alias=${encodeURIComponent(params.alias)}`
      } else if (params?.id) {
        url += `?id=${encodeURIComponent(params.id)}`
      }
      
      const response = await axiosInstance.get(url)
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        // Se não há dados, retornar array vazio
        if (!data || (Array.isArray(data) && data.length === 0)) {
          return []
        }
        
        // Se a resposta é um único objeto, retornar como array
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar conexões')
      }
    })
    
    if (result) {
      connections.value = result
    }
    
    return result
  }

  async function getById(connectionId: string): Promise<Connection | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get(`/connections?id=${encodeURIComponent(connectionId)}`)
      
      if (response.data.code === 'SUCCESS') {
        return response.data.data
      } else {
        throw new Error(response.data.data || 'Erro ao carregar conexão')
      }
    })
    
    return result
  }

  async function deleteConnection(connectionId: string): Promise<boolean> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.delete(`/connection/${connectionId}`)
      
      if (response.data.code === 'SUCCESS') {
        // Remove from local state
        const index = connections.value.findIndex(c => c.connection_id === connectionId)
        if (index > -1) {
          connections.value.splice(index, 1)
        }
        
        appStore.addNotification('Conexão excluída com sucesso', 'success')
        return true
      } else {
        throw new Error(response.data.data || 'Erro ao excluir conexão')
      }
    })
    
    return result !== null
  }

  async function getDidDocument(did: string): Promise<any | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get(`/connections/did-document?did=${encodeURIComponent(did)}`)
      
      if (response.data.code === 'SUCCESS') {
        return response.data.data
      } else {
        throw new Error(response.data.data || 'Erro ao carregar DID Document')
      }
    })
    
    return result
  }

  // Helper function to get status class for UI
  function getStatusClass(state: string): string {
    switch (state) {
      case 'active':
      case 'response':
        return 'bg-green-500/20 text-green-300 border border-green-500/30'
      case 'request':
      case 'invitation':
        return 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
      case 'inactive':
      case 'error':
        return 'bg-red-500/20 text-red-300 border border-red-500/30'
      default:
        return 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
    }
  }

  // Helper function to get status label for UI
  function getStatusLabel(state: string): string {
    switch (state) {
      case 'active':
        return 'Ativo'
      case 'response':
        return 'Conectado'
      case 'request':
        return 'Pendente'
      case 'invitation':
        return 'Convite Enviado'
      case 'inactive':
        return 'Inativo'
      case 'error':
        return 'Erro'
      default:
        return 'Desconhecido'
    }
  }

  return {
    // State
    connections,
    // Actions
    fetchAll,
    getById,
    deleteConnection,
    getDidDocument,
    // Helpers
    getStatusClass,
    getStatusLabel,
  }
})
