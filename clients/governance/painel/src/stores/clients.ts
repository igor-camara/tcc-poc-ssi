import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '../lib/axios'
import { useAppStore } from './app'

export interface Client {
  id?: string
  company_name: string
  cnpj: string
  email: string
  phone: string
  address: string
  client_type: 'issuer' | 'verifier' | 'both'
  description: string
  created_at?: string
  updated_at?: string
}

export interface ClientRequest {
  company_name: string
  cnpj: string
  email: string
  phone: string
  address: string
  client_type: 'issuer' | 'verifier' | 'both'
  description: string
}

export const useClientsStore = defineStore('clients', () => {
  const appStore = useAppStore()
  const clients = ref<Client[]>([])
  const currentClient = ref<Client | null>(null)

  async function createClient(clientData: ClientRequest): Promise<Client | null> {
    try {
      appStore.setLoading(true)
      const response = await axiosInstance.post<Client>('/clients', clientData)
      
      if (response.data) {
        clients.value.push(response.data)
        appStore.addNotification('Solicitação de cliente enviada com sucesso!', 'success')
        return response.data
      }
      
      return null
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao criar solicitação de cliente'
      appStore.addNotification(errorMessage, 'error')
      appStore.setError({
        message: errorMessage,
        code: error.response?.status?.toString(),
        details: error.response?.data
      })
      return null
    } finally {
      appStore.setLoading(false)
    }
  }

  async function fetchClients(): Promise<void> {
    try {
      appStore.setLoading(true)
      const response = await axiosInstance.get<Client[]>('/clients')
      clients.value = response.data
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao buscar clientes'
      appStore.addNotification(errorMessage, 'error')
      appStore.setError({
        message: errorMessage,
        code: error.response?.status?.toString(),
        details: error.response?.data
      })
    } finally {
      appStore.setLoading(false)
    }
  }

  async function getClientById(id: string): Promise<Client | null> {
    try {
      appStore.setLoading(true)
      const response = await axiosInstance.get<Client>(`/clients/${id}`)
      currentClient.value = response.data
      return response.data
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao buscar cliente'
      appStore.addNotification(errorMessage, 'error')
      appStore.setError({
        message: errorMessage,
        code: error.response?.status?.toString(),
        details: error.response?.data
      })
      return null
    } finally {
      appStore.setLoading(false)
    }
  }

  return {
    clients,
    currentClient,
    createClient,
    fetchClients,
    getClientById
  }
})
