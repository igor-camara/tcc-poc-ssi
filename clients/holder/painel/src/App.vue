<template>
  <AuthForm v-if="!authStore.isAuthenticated" />
  <Dashboard v-else :user-data="authStore.user || undefined" />
  <GlobalNotifications />
  <GlobalLoading />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AuthForm from './components/AuthForm.vue'
import Dashboard from './components/Dashboard.vue'
import GlobalNotifications from './components/GlobalNotifications.vue'
import GlobalLoading from './components/GlobalLoading.vue'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()

onMounted(async () => {
  // Verificar se o usuário já está autenticado
  await authStore.checkAuth()
})
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
