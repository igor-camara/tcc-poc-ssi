<template>
   <div class="fixed top-4 right-4 z-[9999] space-y-2">
      <TransitionGroup name="notification" tag="div" class="space-y-2">
         <div
            v-for="notification in appStore.notifications"
            :key="notification.id"
            :class="[
            'min-w-80 p-4 rounded-lg border backdrop-blur-md shadow-lg',
            'animate-slide-in-right',
            getNotificationClass(notification.type)
            ]"
            >
            <div class="flex items-center justify-between">
               <div class="flex items-center space-x-3">
                  <component :is="getNotificationIcon(notification.type)" class="w-5 h-5" />
                  <p class="text-sm font-medium">{{ notification.message }}</p>
               </div>
               <button
                  @click="appStore.removeNotification(notification.id)"
                  class="text-current hover:opacity-70 transition-opacity"
                  >
                  <X class="w-4 h-4" />
               </button>
            </div>
         </div>
      </TransitionGroup>
   </div>
</template>


<script setup lang="ts">
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-vue-next'
import { useAppStore } from '@/stores'

const appStore = useAppStore()

const getNotificationClass = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-500/20 border-green-500/30 text-green-100'
    case 'error':
      return 'bg-red-500/20 border-red-500/30 text-red-100'
    case 'warning':
      return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-100'
    case 'info':
    default:
      return 'bg-blue-500/20 border-blue-500/30 text-blue-100'
  }
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'success':
      return CheckCircle
    case 'error':
      return AlertCircle
    case 'warning':
      return AlertTriangle
    case 'info':
    default:
      return Info
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.animate-slide-in-right {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>