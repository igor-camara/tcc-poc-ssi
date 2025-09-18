import { ref, computed } from 'vue'
import { apiService } from '../services/api'
import { useAppStore } from './useAppStore'

// Estado global de autenticação
const user = ref(null)
const token = ref(localStorage.getItem('token'))
const error = ref(null)

export function useAuth() {
  const appStore = useAppStore()
  const isAuthenticated = computed(() => !!token.value)
  
  const login = async (email, password) => {
    try {
      appStore.setLoading(true)
      error.value = null
      
      const response = await apiService.post('/auth/login', {
        email,
        password
      })
      
      const { token: authToken, user: userData } = response.data
      
      token.value = authToken
      user.value = userData

      console.log(user)
      
      // Salvar token no localStorage
      localStorage.setItem('token', authToken)
      localStorage.setItem('did', user.value.did)
      localStorage.setItem('verkey', user.value.verkey)
      
      // Mostrar alerta de sucesso
      appStore.showSuccess('Login realizado com sucesso!', {
        title: 'Bem-vindo de volta!'
      })
      
      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Erro ao fazer login'
      error.value = errorMessage
      
      // Mostrar alerta de erro
      appStore.showError(errorMessage, {
        title: 'Falha no login'
      })
      
      return { success: false, error: error.value }
    } finally {
      appStore.setLoading(false)
    }
  }
  
  const register = async (userData) => {
    try {
      appStore.setLoading(true)
      error.value = null
      
      const response = await apiService.post('/auth/register', userData)
      
      const { token: authToken, user: newUser } = response.data
      
      token.value = authToken
      user.value = newUser
      
      // Salvar token no localStorage
      localStorage.setItem('token', authToken)
      localStorage.setItem('did', user.value.did)
      localStorage.setItem('verkey', user.value.verkey)
      
      // Mostrar alerta de sucesso
      appStore.showSuccess('Conta criada com sucesso!', {
        title: 'Registro concluído'
      })
      
      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Erro ao fazer cadastro'
      error.value = errorMessage
      
      // Mostrar alerta de erro
      appStore.showError(errorMessage, {
        title: 'Falha no registro'
      })
      
      return { success: false, error: error.value }
    } finally {
      appStore.setLoading(false)
    }
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('did')
    localStorage.removeItem('verkey')
    
    // Mostrar alerta informativo
    appStore.showInfo('Você foi desconectado com segurança.', {
      title: 'Logout realizado'
    })
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
    error: computed(() => error.value),
    
    login,
    register,
    logout,
    checkAuth,
    clearError
  }
}