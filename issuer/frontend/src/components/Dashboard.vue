<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
    <!-- Navigation -->
    <nav class="bg-white/80 dark:bg-slate-800/80 backdrop-blur-md shadow-lg border-b border-white/20 dark:border-slate-700/20 sticky top-0 z-50">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 w-full">
          <!-- Logo/Brand -->
          <div class="flex p-2 w-1/3 items-center gap-x-3">
            <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
            <div class="gap-x-4">
              <h1 class="text-xl font-bold text-slate-900 dark:text-white">SSI Holder Wallet</h1>
              <p class="text-xs text-slate-500 dark:text-slate-400 -mt-1">Self-Sovereign Identity</p>
            </div>
          </div>
          
          <!-- User Menu -->
          <div class="flex w-2/3 items-center justify-end gap-x-8">
            <!-- Theme Toggle -->
            <ThemeToggle />
            
            <div class="hidden sm:flex items-center gap-x-3">
              <div class="w-8 h-8 bg-gradient-to-br from-slate-400 to-slate-600 rounded-full flex items-center justify-center">
                <span class="text-white text-sm font-semibold">
                  {{ getUserInitials(user?.name) }}
                </span>
              </div>
              <div class="text-sm">
                <p class="font-medium text-slate-900 dark:text-white">{{ user?.name || 'Usuário' }}</p>
                <p class="text-slate-500 dark:text-slate-400">{{ user?.email || 'email@exemplo.com' }}</p>
              </div>
            </div>
            
            <button
              @click="handleLogout"
              class="inline-flex items-center gap-1 px-4 py-2 border border-transparent text-sm font-medium rounded-xl text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              Sair
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">
          Bem-vindo de volta, {{ getFirstName(user?.name) }}! 👋
        </h2>
        <p class="text-slate-600 dark:text-slate-300">
          Gerencie suas credenciais digitais e identidade de forma segura
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
        
        <div class="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-slate-700/20 shadow-lg hover:shadow-xl transition-all duration-200">
          <div class="flex items-center gap-x-2">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
              </div>
            </div>
            <div class="ml-4 w-full">
              <p class="text-sm font-medium text-slate-600 dark:text-slate-300">Conexões</p>
              <p class="text-2xl font-bold text-slate-900 dark:text-white">3</p>
            </div>
          </div>

          <!-- Botões em coluna abaixo do texto -->
          <div class="flex gap-x-2 pt-4">
            <button class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-2 px-4 rounded-xl transition-all duration-200" @click="isDialogOpen = true">
              Adicionar
            </button>
            <button class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-2 px-4 rounded-xl transition-all duration-200">
              Exibir
            </button>
          </div>
        </div>
      </div>
      <Dialog :isOpen="isDialogOpen" @close="closeDialog"/>
    </main>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useInvitation } from '../composables/useInvitation'
import { ref } from 'vue'
import ThemeToggle from './ThemeToggle.vue'
import Dialog from './Dialog.vue'

const { user, logout } = useAuth()
const { sendInvitation } = useInvitation()
const isDialogOpen = ref(false);

const closeDialog = async (inputText, connectionUrl) => {
  if (inputText == '' || connectionUrl == '') {
    isDialogOpen.value = false
    return
  }

  const response = await sendInvitation(inputText, connectionUrl)

  if (response.success) {
    alert('Convite enviado com sucesso!')
  } else {
    alert(response.data)
  }
  
  isDialogOpen.value = false
}

const handleLogout = () => {
  logout()
}

const getUserInitials = (name) => {
  if (!name) return 'U'
  const names = name.split(' ')
  return names.length > 1 
    ? `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase()
    : name[0].toUpperCase()
}

const getFirstName = (name) => {
  if (!name) return 'Usuário'
  return name.split(' ')[0]
}
</script>