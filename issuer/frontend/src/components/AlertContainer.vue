<template>
  <!-- Container de Alertas - Posicionado no topo direito -->
  <teleport to="body">
    <div
      v-if="appStore.hasAlerts"
      class="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full"
    >
      <transition-group
        name="alert"
        tag="div"
        class="space-y-3"
      >
        <Alert
          v-for="alert in appStore.alerts"
          :key="alert.id"
          :variant="alert.variant"
          :title="alert.title"
          :description="alert.description"
          :closable="alert.closable"
          :auto-close="alert.autoClose"
          :duration="alert.duration"
          @close="handleAlertClose(alert.id)"
        />
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { useAppStore } from '../composables/useAppStore'
import Alert from './Alert.vue'

// Store
const appStore = useAppStore()

// Métodos
const handleAlertClose = (alertId) => {
  appStore.removeAlert(alertId)
}
</script>

<style scoped>
/* Animações para entrada/saída dos alertas */
.alert-enter-active {
  transition: all 0.3s ease-out;
}

.alert-leave-active {
  transition: all 0.3s ease-in;
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.alert-move {
  transition: transform 0.3s ease;
}
</style>