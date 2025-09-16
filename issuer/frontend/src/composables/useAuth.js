import { ref, computed } from 'vue'
import { apiService } from '../services/api'

// Estado global de autenticação
const user = ref(null)
const token = ref(localStorage.getItem('token'))
const isLoading = ref(false)
const error = ref(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)
  
  const login = async (email, password) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.post('/auth/login', {
        email,
        password
      })
      
      const { token: authToken, user: userData } = response.data
      
      token.value = authToken
      user.value = userData
      
      // Salvar token no localStorage
      localStorage.setItem('token', authToken)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erro ao fazer login'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  const register = async (userData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiService.post('/auth/register', userData)
      
      const { token: authToken, user: newUser } = response.data
      
      token.value = authToken
      user.value = newUser
      
      // Salvar token no localStorage
      localStorage.setItem('token', authToken)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erro ao fazer cadastro'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }
  
  const checkAuth = async () => {
    if (!token.value) return false
    
    try {
      const response = await apiService.get('/auth/me')
      user.value = response.data
      return true
    } catch (err) {
      logout()
      return false
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    user: computed(() => user.value),
    token: computed(() => token.value),
    isAuthenticated,
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    
    login,
    register,
    logout,
    checkAuth,
    clearError
  }
}