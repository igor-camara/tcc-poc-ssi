import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/axios'

export const useLedgerStore = defineStore('ledger', () => {
  const isConfigured = ref(false)
  const isLoading = ref(false)
  const message = ref('')

  const checkKey = async () => {
    isLoading.value = true
    try {
      const response = await api.get('/ledger/check-key')
      if (response.data.code === 'SUCCESS') {
        isConfigured.value = response.data.data.configured
        message.value = response.data.data.message
      }
      return response.data
    } catch (error: any) {
      console.error('Error checking ledger key:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const registerKey = async (key: string) => {
    isLoading.value = true
    try {
      const response = await api.post('/ledger/register', { key })
      if (response.data.code === 'SUCCESS') {
        isConfigured.value = true
        message.value = 'API Key configured successfully'
      }
      return response.data
    } catch (error: any) {
      console.error('Error registering ledger key:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    isConfigured,
    isLoading,
    message,
    checkKey,
    registerKey,
  }
})
