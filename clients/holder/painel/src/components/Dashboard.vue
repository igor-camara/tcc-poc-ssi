<template>
   <div class="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex">
      <!-- Sidebar -->
      <div class="w-64 bg-white/10 backdrop-blur-md border-r border-white/20 flex flex-col">
         <!-- Logo/Brand -->
         <div class="p-6 border-b border-white/20">
            <div class="flex items-center space-x-2">
               <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <span class="text-white font-bold text-sm">H</span>
               </div>
               <span class="text-white font-semibold text-xl">Painel Holder</span>
            </div>
         </div>
         <!-- Navigation Menu -->
         <nav class="flex-1 p-4 space-y-2">
            <a
               v-for="item in menuItems"
               :key="item.id"
               @click="activeMenu = item.id"
               :class="[
               'flex items-center space-x-3 px-4 py-3 rounded-lg cursor-pointer transition-all duration-200',
               activeMenu === item.id
               ? 'bg-purple-600 text-white shadow-lg'
               : 'text-purple-200 hover:bg-white/10 hover:text-white'
               ]"
               >
               <component :is="item.icon" class="w-5 h-5" />
               <span class="font-medium">{{ item.label }}</span>
            </a>
         </nav>
         <!-- User Profile -->
         <div class="p-4 border-t border-white/20">
            <div class="flex items-center space-x-3 mb-4">
               <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                  <span class="text-white font-semibold text-lg">{{ userInitials }}</span>
               </div>
               <div>
                  <p class="text-white font-medium">{{ userName }}</p>
                  <p class="text-purple-300 text-sm">{{ userRole }}</p>
               </div>
            </div>
            <button
               @click="handleLogout"
               class="flex items-center space-x-2 text-purple-200 hover:text-white cursor-pointer transition-colors duration-200 w-full px-2 py-1 rounded hover:bg-white/10"
               >
               <LogOut class="w-4 h-4" />
               <span class="text-sm">Log Out</span>
            </button>
         </div>
      </div>
      <!-- Main Content -->
      <div class="flex-1 flex flex-col">
         <!-- Header -->
         <header class="bg-white/5 backdrop-blur-sm border-b border-white/10 p-6">
            <div class="flex items-center justify-between">
               <h1 class="text-2xl font-bold text-white">{{ currentPageTitle }}</h1>
               <div class="text-purple-200 text-sm">
                  {{ currentDate }}
               </div>
            </div>
         </header>
         <!-- Page Content -->
         <main class="flex-1 p-6">
            <div class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-8 h-full">
               <!-- Connections Content -->
               <ConnectionsManager v-if="activeMenu === 'my-connections'" />
               <!-- Credentials Content -->
               <MyCredentials v-else-if="activeMenu === 'my-credentials'" />
               <!-- Credential Offers Content -->
               <CredentialOffers v-else-if="activeMenu === 'answer-issue-request'" />
               <!-- Proof Request Content -->
               <div v-else-if="activeMenu === 'answer-proof-request'" class="space-y-6">
                  <h2 class="text-xl font-semibold text-white mb-4">Pedidos de Prova</h2>
                  <p class="text-purple-200">Solicitações de prova de credenciais pendentes.</p>
               </div>
            </div>
         </main>
      </div>
   </div>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  LayoutDashboard, 
  BarChart3, 
  CreditCard, 
  LogOut 
} from 'lucide-vue-next'
import ConnectionsManager from './ConnectionsManager.vue'
import CredentialOffers from './CredentialOffers.vue'
import MyCredentials from './MyCredentials.vue'
import { useAuthStore } from '@/stores'

// Store
const authStore = useAuthStore()

// Props
interface Props {
  userData?: {
    id?: string
    username?: string
    email?: string
    user_name?: string
    user_surname?: string
    user_email?: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  userData: () => ({ user_name: 'Usuário', user_surname: '', user_email: '' })
})

const activeMenu = ref('my-connections')

const menuItems = [
  { id: 'my-connections', label: 'Minhas conexões', icon: LayoutDashboard },
  { id: 'my-credentials', label: 'Minhas credenciais', icon: LayoutDashboard },
  { id: 'answer-issue-request', label: 'Aceite de Credenciais', icon: BarChart3 },
  { id: 'answer-proof-request', label: 'Pedidos de Prova', icon: CreditCard },
]

// User data - compatível com ambas as estruturas
const userName = computed(() => {
  const name = props.userData?.user_name || props.userData?.username || 'Usuário'
  const surname = props.userData?.user_surname || ''
  return `${name} ${surname}`.trim()
})
const userRole = ref('Holder SSI')

const userInitials = computed(() => {
  const name = props.userData?.user_name || props.userData?.username || 'U'
  const surname = props.userData?.user_surname || ''
  return (name.charAt(0) + surname.charAt(0)).toUpperCase()
})

const currentPageTitle = computed(() => {
  const item = menuItems.find(item => item.id === activeMenu.value)
  return item?.label || 'Dashboard'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const handleLogout = () => {
  authStore.logout()
}
</script>