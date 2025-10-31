import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axiosInstance from '@/lib/axios'
import { useAppStore } from './app'

export interface User {
  user_name: string
  user_surname: string
  user_email: string
  user_did: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  first_name: string
  last_name: string
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)

  // Get app store for loading and notifications
  const appStore = useAppStore()

  // Initialize state from localStorage
  function initializeAuth() {
    try {
      const savedToken = localStorage.getItem('auth_token')
      const savedUser = localStorage.getItem('user_data')
      
      if (savedToken && savedUser) {
        // Try to parse the user data
        let parsedUser
        try {
          parsedUser = JSON.parse(savedUser)
        } catch (parseError) {
          throw new Error('Invalid JSON in user_data')
        }
        
        // Validate that parsed user has required fields
        if (parsedUser && typeof parsedUser === 'object' && (parsedUser.user_email || parsedUser.email)) {
          token.value = savedToken
          user.value = parsedUser
          isAuthenticated.value = true
        } else {
          throw new Error('Invalid user data structure')
        }
      } else {
        token.value = null
        user.value = null
        isAuthenticated.value = false
      }
    } catch (error) {
      
      // Clear ALL auth-related data
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
      
      // Reset state
      token.value = null
      user.value = null
      isAuthenticated.value = false
    }
  }

  // Actions
  async function login(credentials: LoginRequest): Promise<User | null> {
    const result = await appStore.makeApiCall(async () => {      
      const response = await axiosInstance.post('/auth/login', credentials)
      
      if (response.data.code === 'SUCCESS') {
        // A API retorna os dados diretamente em response.data.data
        const apiData = response.data.data
        
        // Verificar se tem token separado ou se está dentro dos dados
        const authToken = apiData.token || apiData.access_token || 'no-token'
        
        // Criar objeto user com os dados da API
        const userData: User = {
          user_name: apiData.user_name,
          user_surname: apiData.user_surname,
          user_email: apiData.user_email,
          user_did: apiData.user_did
        }
        
        // Update state first
        token.value = authToken
        user.value = userData
        isAuthenticated.value = true
        
        // Then store in localStorage with validation
        try {
          localStorage.setItem('auth_token', authToken)
          console.log(userData);
          localStorage.setItem('user_data', JSON.stringify(userData))
        } catch (error) {
          throw new Error('Erro ao salvar dados de autenticação')
        }
        
        appStore.addNotification('Login realizado com sucesso!', 'success')
        return userData
      } else {
        throw new Error(response.data.message || 'Erro ao fazer login')
      }
    })
    
    return result
  }

  async function register(registerData: RegisterRequest): Promise<User | null> {
    const result = await appStore.makeApiCall(async () => {
      const response = await axiosInstance.post('/auth/register', registerData)
      
      if (response.data.code === 'SUCCESS') {
        // A API retorna os dados diretamente em response.data.data
        const apiData = response.data.data
        
        // Verificar se tem token separado ou se está dentro dos dados
        const authToken = apiData.token || apiData.access_token || 'no-token'
        
        // Criar objeto user com os dados da API
        const userData: User = {
          user_name: apiData.user_name,
          user_surname: apiData.user_surname,
          user_email: apiData.user_email,
          user_did: apiData.user_did
        }
        
        // Update state first
        token.value = authToken
        user.value = userData
        isAuthenticated.value = true
        
        // Then store in localStorage with validation
        try {
          localStorage.setItem('auth_token', authToken)
          localStorage.setItem('user_data', JSON.stringify(userData))
        } catch (error) {
          throw new Error('Erro ao salvar dados de autenticação')
        }
        
        appStore.addNotification('Conta criada com sucesso!', 'success')
        return userData
      } else {
        throw new Error(response.data.message || 'Erro ao criar conta')
      }
    })
    
    return result
  }

  function logout() {
    // Clear local storage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    
    // Clear state
    user.value = null
    token.value = null
    isAuthenticated.value = false
    
    appStore.addNotification('Logout realizado com sucesso!', 'info')
  }

  async function checkAuth(): Promise<boolean> {
    // If we already have user data from localStorage, no need to call API
    if (token.value && user.value) {
      isAuthenticated.value = true
      return true
    }
    
    if (!token.value) {
      return false
    }

    try {
      const response = await axiosInstance.get('/auth/me')
      
      if (response.data.code === 'SUCCESS') {
        const apiData = response.data.data
        
        // Criar objeto user com os dados da API
        const userData: User = {
          user_name: apiData.user_name,
          user_surname: apiData.user_surname,
          user_email: apiData.user_email,
          user_did: apiData.user_did
        }
        
        user.value = userData
        isAuthenticated.value = true
        
        // Save user data to localStorage
        localStorage.setItem('user_data', JSON.stringify(userData))
        return true
      }
    } catch (error) {
      // Token invalid, clear auth state
      logout()
    }
    
    return false
  }

  const userEmail = computed(() => user.value?.user_email ?? '')
  const userDid = computed(() => user.value?.user_did ?? '')


  // Initialize auth state on store creation
  initializeAuth()

  return {
    // State
    user,
    token,
    isAuthenticated,
    //getters
    userEmail,
    userDid,
    // Actions
    login,
    register,
    logout,
    checkAuth,
    initializeAuth,
  }
})
