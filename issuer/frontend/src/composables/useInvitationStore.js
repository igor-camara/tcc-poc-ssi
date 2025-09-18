import { defineStore } from 'pinia'
import { useAppStore } from './useAppStore'
import { apiService } from '../services/api'

export const useInvitationStore = defineStore('invitation', {
  actions: {
    async createInvitation(alias) {
      const appStore = useAppStore()
      appStore.setLoading(true)

      try {
        const response = await apiService.post('/create-invitation', { alias })
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Erro ao criar convite' 
        }
      } finally {
        appStore.setLoading(false)
      }
    }
  }
})
