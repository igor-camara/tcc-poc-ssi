import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false,
    alerts: [] // Array de alertas ativos
  }),
  
  getters: {
    // Getter para verificar se há alertas ativos
    hasAlerts: (state) => state.alerts.length > 0,
    
    // Getter para alertas por tipo
    alertsByType: (state) => (type) => state.alerts.filter(alert => alert.variant === type)
  },
  
  actions: {
    setLoading(status) {
      this.isLoading = status
    },
    
    // Adicionar um novo alerta
    addAlert(alert) {
      const id = Date.now() + Math.random()
      const newAlert = {
        id,
        variant: alert.variant || 'info',
        title: alert.title || '',
        description: alert.description || '',
        autoClose: alert.autoClose !== false, // Default true
        closable: alert.closable !== false, // Default true
        ...alert
      }
      
      this.alerts.push(newAlert)
      return id
    },
    
    // Remover um alerta específico
    removeAlert(alertId) {
      const index = this.alerts.findIndex(alert => alert.id === alertId)
      if (index > -1) {
        this.alerts.splice(index, 1)
      }
    },
    
    // Limpar todos os alertas
    clearAlerts() {
      this.alerts = []
    },
    
    // Métodos de conveniência para diferentes tipos de alerta
    showSuccess(message, options = {}) {
      return this.addAlert({
        variant: 'success',
        description: message,
        title: options.title || 'Sucesso!',
        ...options
      })
    },
    
    showWarning(message, options = {}) {
      return this.addAlert({
        variant: 'warning',
        description: message,
        title: options.title || 'Atenção!',
        ...options
      })
    },
    
    showError(message, options = {}) {
      return this.addAlert({
        variant: 'error',
        description: message,
        title: options.title || 'Erro!',
        duration: options.duration || 8000, // Erros ficam mais tempo
        ...options
      })
    },
    
    showInfo(message, options = {}) {
      return this.addAlert({
        variant: 'info',
        description: message,
        title: options.title || 'Informação',
        ...options
      })
    }
  }
})
