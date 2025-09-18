import { defineStore } from 'pinia'
import { useAppStore } from './useAppStore'
import { apiService } from '../services/api'

export const useCredentialStore = defineStore('credential', {
    actions: {
        async createCredential(name, version, attributes) {
            const appStore = useAppStore()
            appStore.setLoading(true)
            
            try {
                const response = await apiService.post('/create-credential', {
                schema_name: name,
                schema_version: version,
                attributes: attributes
                })
                return { success: true, data: response.data }
            } catch (error) {
                return { 
                success: false, 
                error: error.response?.data?.detail || 'Erro ao criar esquema' 
                }
            } finally {
                appStore.setLoading(false)
            }
        }
    }
})