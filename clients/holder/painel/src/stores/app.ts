import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ApiError {
  message: string
  code?: string
  details?: any
}

export const useAppStore = defineStore('app', () => {
  // State
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)
  const notifications = ref<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }>>([])

  // Actions
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function setError(err: ApiError | null) {
    error.value = err
  }

  function clearError() {
    error.value = null
  }

  function addNotification(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') {
    const id = Date.now().toString()
    notifications.value.push({ id, message, type })
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      removeNotification(id)
    }, 5000)
  }

  function removeNotification(id: string) {
    const index = notifications.value.findIndex((n: { id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  async function makeApiCall<T>(apiCall: () => Promise<T>): Promise<T | null> {
    try {
      setLoading(true)
      clearError()
      const result = await apiCall()
      return result
    } catch (error: any) {
      const apiError: ApiError = {
        message: error.response?.data?.data || error.response?.data?.message || error.message || 'Erro desconhecido',
        code: error.response?.data?.code || error.code,
        details: error.response?.data
      }
      setError(apiError)
      addNotification(apiError.message, 'error')
      return null
    } finally {
      setLoading(false)
    }
  }

  return {
    // State
    isLoading,
    error,
    notifications,
    // Actions
    setLoading,
    setError,
    clearError,
    addNotification,
    removeNotification,
    makeApiCall,
  }
})