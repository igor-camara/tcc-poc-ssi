import { defineStore } from 'pinia'
import { ref } from 'vue'
import axiosInstance from '../lib/axios'
import { useAppStore } from './app'

export interface Steward {
  id: string
  name: string
  email: string
  organization: string
  status: string
  created_at: string
}

export const useStewardsStore = defineStore('stewards', () => {
  const appStore = useAppStore()
  const stewards = ref<Steward[]>([])
  const isLoading = ref(false)

  async function fetchStewards(): Promise<void> {
    try {
      isLoading.value = true
      const response = await axiosInstance.get('/stewards')
      if (response.data.code === 'SUCCESS') {
        stewards.value = response.data.data
      }
    } catch (error) {
      console.error('Erro ao buscar stewards:', error)
      appStore.addNotification('Erro ao carregar stewards', 'error')
    } finally {
      isLoading.value = false
    }
  }

  function getStewardById(id: string): Steward | undefined {
    return stewards.value.find(s => s.id === id)
  }

  function getStewardName(id: string): string {
    const steward = getStewardById(id)
    return steward ? steward.name : 'Steward Desconhecido'
  }

  return {
    stewards,
    isLoading,
    fetchStewards,
    getStewardById,
    getStewardName
  }
})
