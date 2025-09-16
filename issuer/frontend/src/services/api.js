import axios from 'axios'

// Configuração base do axios
const apiService = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Interceptor para adicionar token de autenticação
apiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratar respostas e erros
apiService.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Se receber 401, limpar autenticação
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // Redirecionar para login se necessário
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export { apiService }