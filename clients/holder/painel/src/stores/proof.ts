import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

// Tipos para restrições
export interface Restriction {
  schema_id?: string
  cred_def_id?: string
  issuer_did?: string
  [key: string]: any
}

// Tipos para atributos solicitados
export interface RequestedAttribute {
  names?: string[]
  name?: string
  restrictions?: Restriction[]
}

// Tipos para predicados solicitados
export interface RequestedPredicate {
  name: string
  p_type: string // '>=' | '>' | '<=' | '<'
  p_value: number
  restrictions?: Restriction[]
}

// Tipo para pedido de prova
export interface ProofRequest {
  id: string
  pres_ex_id: string
  state: string
  name: string
  version: string
  requested_attributes: Record<string, RequestedAttribute>
  requested_predicates: Record<string, RequestedPredicate>
  error_msg?: string
  created_at?: string
  updated_at?: string
}

// Tipo para credencial disponível
export interface AvailableCredential {
  referent: string
  schema_id: string
  cred_def_id: string
  attrs: Record<string, string>
  presentation_referents: string[]
}

// Tipo para seleção de credencial
export interface CredentialSelection {
  referent: string
  cred_id: string
  revealed: boolean
}

// Tipo para envio de apresentação
export interface SendPresentationRequest {
  pres_ex_id: string
  indy: {
    requested_attributes: Record<string, {
      cred_id: string
      revealed: boolean
    }>
    requested_predicates: Record<string, {
      cred_id: string
      timestamp?: number
    }>
    self_attested_attributes?: Record<string, string>
    trace?: boolean
  }
  auto_remove?: boolean
}


export const useProofStore = defineStore('proof', () => {
  // State
  const proofRequests = ref<ProofRequest[]>([])
  const availableCredentials = ref<Record<string, AvailableCredential[]>>({})

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Actions
  async function fetchProofRequests(): Promise<ProofRequest[] | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get('/proof/requests')
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        if (!data || (Array.isArray(data) && data.length === 0)) {
          return []
        }
        
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar pedidos de prova')
      }
    })

    if (result !== null) {
      proofRequests.value = result
    }

    return result
  }

  async function fetchAvailableCredentials(proofRequestId: string): Promise<AvailableCredential[] | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get(`/proof/requests/${proofRequestId}/credentials`)
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        if (!data || (Array.isArray(data) && data.length === 0)) {
          return []
        }
        
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar credenciais disponíveis')
      }
    })

    if (result !== null) {
      availableCredentials.value[proofRequestId] = result
    }

    return result
  }

  async function sendPresentation(request: SendPresentationRequest): Promise<boolean> {
    const result = await appStore.makeApiCall(async () => {
      console.log('Enviando apresentação:', request)
      const response = await axiosInstance.post(`/proof/requests/${request.pres_ex_id}/send-presentation`, request)
      console.log('Resposta da apresentação:', response.data)

      if (response.data.code === 'SUCCESS') {
        // Remove o pedido de prova da lista após envio bem-sucedido
        proofRequests.value = proofRequests.value.filter(
          pr => pr.pres_ex_id !== request.pres_ex_id
        )
        
        // Remove as credenciais disponíveis do cache
        const proofRequest = proofRequests.value.find(pr => pr.pres_ex_id === request.pres_ex_id)
        if (proofRequest) {
          delete availableCredentials.value[proofRequest.id]
        }
        
        appStore.addNotification('Prova enviada com sucesso!', 'success')
        return true
      } else {
        console.error('Erro na resposta:', response.data)
        throw new Error(response.data.data || 'Erro ao enviar prova')
      }
    })

    return result !== null ? result : false
  }

  // Função auxiliar para verificar se uma credencial satisfaz as restrições
  function credentialMatchesRestrictions(
    credential: AvailableCredential, 
    restrictions?: Restriction[]
  ): boolean {
    if (!restrictions || restrictions.length === 0) {
      return true
    }

    // A credencial deve satisfazer pelo menos uma das restrições
    return restrictions.some(restriction => {
      // Verifica cada campo da restrição
      for (const [key, value] of Object.entries(restriction)) {
        if (key === 'schema_id' && credential.schema_id !== value) {
          return false
        }
        if (key === 'cred_def_id' && credential.cred_def_id !== value) {
          return false
        }
        // Adicione outras verificações conforme necessário
      }
      return true
    })
  }

  // Função auxiliar para obter credenciais que satisfazem um atributo solicitado
  function getMatchingCredentials(
    proofRequestId: string,
    referent: string,
    restrictions?: Restriction[]
  ): AvailableCredential[] {
    const allCredentials = availableCredentials.value[proofRequestId] || []
    
    return allCredentials.filter(cred => {
      // Verifica se a credencial tem o referent correto
      const hasReferent = cred.presentation_referents.includes(referent)
      
      // Verifica se satisfaz as restrições
      const matchesRestrictions = credentialMatchesRestrictions(cred, restrictions)
      
      return hasReferent && matchesRestrictions
    })
  }

  function clearProofRequests() {
    proofRequests.value = []
  }

  function clearAvailableCredentials() {
    availableCredentials.value = {}
  }

  return {
    proofRequests,
    availableCredentials,
    fetchProofRequests,
    fetchAvailableCredentials,
    sendPresentation,
    getMatchingCredentials,
    clearProofRequests,
    clearAvailableCredentials
  }
})
