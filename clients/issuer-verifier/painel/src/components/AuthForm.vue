<template>
   <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-700 to-blue-800">
      <div class="w-full max-w-md p-8">
         <div class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 shadow-2xl p-8 animate-slide-up">
            <div class="text-center mb-8">
               <h1 class="text-3xl font-bold text-white mb-2">Bem-vindo</h1>
               <p class="text-blue-100">Acesse sua conta ou crie uma nova</p>
            </div>
            <Tabs v-model="activeTab" class="w-full">
               <TabsList class="grid w-full grid-cols-2 bg-white/20">
                  <TabsTrigger value="login" class="data-[state=active]:bg-blue-600 text-white cursor-pointer transition-all duration-200 hover:bg-white/30">
                     Login
                  </TabsTrigger>
                  <TabsTrigger value="register" class="data-[state=active]:bg-blue-600 text-white cursor-pointer transition-all duration-200 hover:bg-white/30">
                     Registro
                  </TabsTrigger>
               </TabsList>
               <div class="relative overflow-hidden transition-all duration-500 ease-out" :style="{ height: containerHeight + 'px' }">
                  <TabsContent value="login" class="mt-6 absolute w-full transition-all duration-300" :class="activeTab === 'login' ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-full'">
                     <div class="animate-fade-in">
                        <form @submit.prevent="handleLogin" class="space-y-4">
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Email</label>
                              <Input
                                 v-model="loginForm.email"
                                 type="email"
                                 placeholder="seu@email.com"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Senha</label>
                              <Input
                                 v-model="loginForm.password"
                                 type="password"
                                 placeholder="••••••••"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <Button
                              type="submit"
                              :disabled="appStore.isLoading"
                              class="w-full bg-blue-600 hover:bg-blue-700 text-white"
                              >
                           {{ appStore.isLoading ? 'Entrando...' : 'Entrar' }}
                           </Button>
                        </form>
                     </div>
                  </TabsContent>
                  <TabsContent value="register" class="mt-6 absolute w-full transition-all duration-300" :class="activeTab === 'register' ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'">
                     <div class="animate-fade-in">
                        <form @submit.prevent="handleRegister" class="space-y-4">
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Nome</label>
                              <Input
                                 v-model="registerForm.first_name"
                                 type="text"
                                 placeholder="Seu nome"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Sobrenome</label>
                              <Input
                                 v-model="registerForm.last_name"
                                 type="text"
                                 placeholder="Seu sobrenome"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Email</label>
                              <Input
                                 v-model="registerForm.email"
                                 type="email"
                                 placeholder="seu@email.com"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <div class="space-y-2">
                              <label class="text-sm font-medium text-white">Senha</label>
                              <Input
                                 v-model="registerForm.password"
                                 type="password"
                                 placeholder="••••••••"
                                 required
                                 class="bg-white/20 border-white/30 text-white placeholder:text-blue-100 transition-all duration-200 focus:bg-white/30 focus:border-blue-500"
                                 />
                           </div>
                           <Button
                              type="submit"
                              :disabled="appStore.isLoading"
                              class="w-full bg-blue-600 hover:bg-blue-700 text-white cursor-pointer transition-all duration-200 transform hover:scale-105 disabled:cursor-not-allowed disabled:hover:scale-100"
                              >
                           {{ appStore.isLoading ? 'Criando conta...' : 'Criar conta' }}
                           </Button>
                        </form>
                     </div>
                  </TabsContent>
               </div>
            </Tabs>
         </div>
      </div>
   </div>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore, useAppStore } from '@/stores'

// Stores
const authStore = useAuthStore()
const appStore = useAppStore()

const activeTab = ref('login')

// Altura aproximada dos formulários
const containerHeight = computed(() => {
  return activeTab.value === 'login' ? 220 : 380
})

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  await authStore.login({
    email: loginForm.value.email,
    password: loginForm.value.password
  })
}

const handleRegister = async () => {
  const result = await authStore.register({
    first_name: registerForm.value.first_name,
    last_name: registerForm.value.last_name,
    email: registerForm.value.email,
    password: registerForm.value.password
  })

  if (result) {
    activeTab.value = 'login'
    registerForm.value = { first_name: '', last_name: '', email: '', password: '' }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.6s ease-out;
}

/* Ajustes para melhor transição */
.tabs-content-container {
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>