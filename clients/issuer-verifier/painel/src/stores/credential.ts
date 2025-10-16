import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/lib/axios'
import { useAppStore } from './app'

export interface Credential {
  id: string
  name: string
  version: string
  attributes: string[]
  seqNo?: number
}

export interface CredentialFormData {
  name: string
  version: string
  attributes: string[]
}

export interface IssuedCredential {
  credential_exchange_id: string
  credential_name: string
  credential_definition_id: string
  issued_at: string
  holder_did: string | null
  holder_alias: string | null
  status: string
  attributes: Record<string, string>
}

export interface CredentialOfferData {
  connection_id: string
  schema_id: string
  attributes: Array<{ name: string; value: string }>
}

export const useCredentialStore = defineStore('credential', () => {
  const appStore = useAppStore()
  
  // State
  const credentials = ref<Credential[]>([])
  const currentCredential = ref<Credential | null>(null)
  const issuedCredentials = ref<IssuedCredential[]>([])

  // Actions
  async function fetchCredentials() {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.get('/credential')
      
      if (response.data.code === 'SUCCESS' && response.data.data) {
        credentials.value = response.data.data.map((cred: any) => ({
          id: cred.id,
          name: cred.name,
          version: cred.version,
          attributes: cred.attributes,
          seqNo: cred.seqNo
        }))
        return credentials.value
      }
      
      credentials.value = []
      return []
    })
    
    return result
  }

  async function fetchCredentialDetails(schemaId: string) {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.post('/credential/details', {
        schema_id: schemaId
      })
      
      if (response.data.code === 'SUCCESS' && response.data.data) {
        const data = response.data.data
        currentCredential.value = {
          id: data.id,
          name: data.name,
          version: data.version,
          attributes: data.attributes || data.attrNames || [],
          seqNo: data.seqNo
        }
        return currentCredential.value
      }
      
      throw new Error(response.data.data || 'Erro ao buscar detalhes da credencial')
    })
    
    return result
  }

  async function createCredential(data: CredentialFormData) {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.post('/credential/create', data)
      
      if (response.data.code === 'SUCCESS') {
        appStore.addNotification('Credencial criada com sucesso!', 'success')
        await fetchCredentials()
        return response.data.data
      }
      
      throw new Error(response.data.data || 'Erro ao criar credencial')
    })
    
    return result
  }

  async function updateCredential(data: CredentialFormData) {
    // Incrementa a versão
    const versionParts = data.version.split('.')
    const majorVersion = parseInt(versionParts[0] || '0') || 0
    const newVersion = `${majorVersion + 1}.0`
    
    const updatedData = {
      ...data,
      version: newVersion
    }
    
    const result = await createCredential(updatedData)
    
    if (result) {
      appStore.addNotification('Credencial atualizada com sucesso! Nova versão: ' + newVersion, 'success')
    }
    
    return result
  }

  function clearCurrentCredential() {
    currentCredential.value = null
  }

  async function fetchIssuedCredentials() {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.get('/credential/issued')
      
      if (response.data.code === 'SUCCESS') {
        issuedCredentials.value = response.data.data
        return response.data.data
      }
      
      throw new Error(response.data.data || 'Erro ao buscar credenciais emitidas')
    })
    
    return result
  }

  async function sendCredentialOffer(data: CredentialOfferData) {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.post('/credential/offer', data)
      
      if (response.data.code === 'SUCCESS') {
        appStore.addNotification('Oferta de credencial enviada com sucesso!', 'success')
        await fetchIssuedCredentials()
        return response.data.data
      }
      
      throw new Error(response.data.data || 'Erro ao enviar oferta de credencial')
    })
    
    return result
  }

  async function issueCredential(credentialExchangeId: string) {
    const result = await appStore.makeApiCall(async () => {
      const response = await axios.post(`/credential/issue/${credentialExchangeId}/`)
      
      if (response.data.code === 'SUCCESS') {
        appStore.addNotification('Credencial emitida com sucesso!', 'success')
        await fetchIssuedCredentials()
        return response.data.data
      }
      
      throw new Error(response.data.data || 'Erro ao emitir credencial')
    })
    
    return result
  }

  return {
    // State
    credentials,
    currentCredential,
    issuedCredentials,
    // Actions
    fetchCredentials,
    fetchCredentialDetails,
    createCredential,
    updateCredential,
    clearCurrentCredential,
    fetchIssuedCredentials,
    sendCredentialOffer,
    issueCredential,
  }
})
