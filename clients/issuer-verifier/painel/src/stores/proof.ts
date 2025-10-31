import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface ProofRequest {
  connection_id: string
  proof_request: {
    name: string
    version: string
    requested_attributes: Record<string, any>
    requested_predicates: Record<string, any>
  }
}

export interface ProofExchange {
  pres_ex_id: string
  connection_id: string
  state: string
  role: string
  initiator: string
  verified: string | null
  verified_msgs: string[] | null
  created_at: string
  updated_at: string
  pres_request: {
    name: string
    version: string
    requested_attributes: Record<string, any>
    requested_predicates: Record<string, any>
  }
  pres?: any
}

export const useProofStore = defineStore('proof', () => {
  // State
  const proofExchanges = ref<ProofExchange[]>([])

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Actions
  async function sendProofRequest(payload: ProofRequest): Promise<any | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post('/proof', payload)
      
      if (response.data.code === 'SUCCESS') {
        return response.data.data
      } else {
        throw new Error(response.data.data || 'Erro ao enviar proof request')
      }
    })

    if (result !== null) {
      appStore.addNotification('Proof request enviado com sucesso!', 'success')
      // Refresh the list after sending
      await fetchAll()
    }

    return result
  }

  async function fetchAll(params?: { 
    connection_id?: string
    descending?: boolean
    limit?: number
    offset?: number
  }): Promise<ProofExchange[] | null> {
    const result = await appStore.makeApiCall(async () => {
      let url = '/proof'
      
      // Add connection_id if provided
      if (params?.connection_id) {
        url += `/${params.connection_id}`
      }
      
      // Add query params
      const queryParams = new URLSearchParams()
      if (params?.descending !== undefined) {
        queryParams.append('descending', params.descending.toString())
      }
      if (params?.limit) {
        queryParams.append('limit', params.limit.toString())
      }
      if (params?.offset) {
        queryParams.append('offset', params.offset.toString())
      }
      
      const queryString = queryParams.toString()
      if (queryString) {
        url += `?${queryString}`
      }
      
      const response = await axiosInstance.get(url)
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar proof exchanges')
      }
    })

    if (result !== null) {
      proofExchanges.value = result
    }

    return result
  }

  return {
    proofExchanges,
    sendProofRequest,
    fetchAll
  }
})
