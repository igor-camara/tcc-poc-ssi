import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface LoginCredentials {
  username: string
  totp_code: string
}

export interface AuthResponse {
  success: boolean
  message: string
  username: string
  access_token?: string
  token?: string
  user?: {
    id: string
    username: string
    email?: string
  }
}

export const useAuthStore = defineStore('auth', () => {
  const appStore = useAppStore()
  
  // State
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<AuthResponse['user'] | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    try {
      appStore.setLoading(true)
      
      const response = await axiosInstance.post<AuthResponse>('/auth/login', {
        username: credentials.username,
        totp_code: credentials.totp_code
      })

      // Verificar se o login foi bem-sucedido
      if (response.data.success) {
        // Usar um token fictício ou o username como identificador
        // já que a API não retorna um token JWT
        const authToken = response.data.access_token || 
                         response.data.token || 
                         `session_${response.data.username}_${Date.now()}`
        
        token.value = authToken
        localStorage.setItem('auth_token', authToken)
        
        // Salvar informações do usuário
        user.value = response.data.user || {
          id: response.data.username,
          username: response.data.username
        }
        
        appStore.addNotification(
          response.data.message || 'Login realizado com sucesso!', 
          'success'
        )
        return true
      } else {
        throw new Error(response.data.message || 'Falha no login')
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail || 
                          error.message ||
                          'Erro ao realizar login. Verifique suas credenciais.'
      
      appStore.addNotification(errorMessage, 'error')
      return false
    } finally {
      appStore.setLoading(false)
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    appStore.addNotification('Logout realizado com sucesso', 'info')
  }

  function checkAuth(): boolean {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      token.value = storedToken
      return true
    }
    return false
  }

  return {
    // State
    token,
    user,
    isAuthenticated,
    
    // Actions
    login,
    logout,
    checkAuth
  }
})
