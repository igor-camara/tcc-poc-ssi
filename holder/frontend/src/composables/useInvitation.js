import { ref, computed } from 'vue'
import { apiService } from '../services/api'

const token = ref(localStorage.getItem('token'))
const isLoading = ref(false)
const error = ref(null)

export function useInvitation() {
    const isAuthenticated = computed(() => !!token.value)

    const sendInvitation = async (issuer_name, url) => {
        try {
            isLoading.value = true
            error.value = null

            const response = await apiService.post('/receive-invitation', {
                issuer_name,
                url
            })

            return { success: true, data: response.data.detail }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Erro ao enviar confirmação de convite'
            return { success: false, data: error.value }
        } finally {
            isLoading.value = false
        }
    }

    return {
        isAuthenticated,
        isLoading: computed(() => isLoading.value),
        error: computed(() => error.value),

        sendInvitation
    }
}