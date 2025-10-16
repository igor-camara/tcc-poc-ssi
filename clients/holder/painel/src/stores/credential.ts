import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface CredentialOffer {
  state: string
  created_at: string
  updated_at: string
  cred_ex_id: string
  connection_id: string
  schema_id: string
  cred_def_id: string
}

export interface AcceptOfferRequest {
  cred_ex_id: string
}

export interface AcceptOfferResponse {
  state: string
  created_at: string
  updated_at: string
  cred_ex_id: string
  connection_id: string
}

export interface Credential {
  issuer_did: string
  issuer_name: string | null
  connection_id: string | null
  schema_id: string
  cred_def_id: string
  attrs: Record<string, string>
}

export const useCredentialStore = defineStore('credential', () => {
  // State
  const offers = ref<CredentialOffer[]>([])
  const credentials = ref<Credential[]>([])

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Actions
  async function fetchOffers(): Promise<CredentialOffer[] | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get('/credential/offers')
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        if (!data || (Array.isArray(data) && data.length === 0)) {
          return []
        }
        
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar ofertas de credenciais')
      }
    })

    if (result !== null) {
      offers.value = result
    }

    return result
  }

  async function acceptOffer(credExId: string): Promise<AcceptOfferResponse | null> {
    const result = await appStore.makeApiCall(async () => {
      const request: AcceptOfferRequest = { cred_ex_id: credExId }
      const response = await axiosInstance.post('/credential/accept-offer', request)

      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        offers.value = offers.value.filter(offer => offer.cred_ex_id !== credExId)
        
        appStore.addNotification('Oferta de credencial aceita com sucesso!', 'success')
        return data
      } else {
        throw new Error(response.data.data || 'Erro ao aceitar oferta de credencial')
      }
    })

    return result
  }

  async function fetchCredentials(): Promise<Credential[] | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.get('/credential/my-credentials')
      
      if (response.data.code === 'SUCCESS') {
        const data = response.data.data
        
        if (!data || (Array.isArray(data) && data.length === 0)) {
          return []
        }
        
        return Array.isArray(data) ? data : [data]
      } else {
        throw new Error(response.data.data || 'Erro ao carregar credenciais')
      }
    })

    if (result !== null) {
      credentials.value = result
    }

    return result
  }

  function clearOffers() {
    offers.value = []
  }

  function clearCredentials() {
    credentials.value = []
  }

  return {
    offers,
    credentials,
    fetchOffers,
    fetchCredentials,
    acceptOffer,
    clearOffers,
    clearCredentials
  }
})
