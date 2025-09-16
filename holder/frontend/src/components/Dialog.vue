<template>
  <!-- Overlay e Dialog -->
  <div 
    v-if="isOpen"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    @click="handleClose"
  >
    <!-- Dialog -->
    <div 
      class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md mx-4 transform transition-all duration-300 ease-out"
      @click.stop
    >
      <!-- Cabeçalho -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-slate-700">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Adicionar Nova Conexão
          </h2>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600 dark:text-slate-400 dark:hover:text-slate-200 transition-colors duration-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Conteúdo -->
      <div class="px-6 py-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
            Nome da Conexão:
          </label>
          <input
            v-model="inputText"
            type="text"
            placeholder="Digite o nome da conexão..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-400 transition-colors duration-200"
            @keyup.enter="confirmAction"
            @keyup.escape="handleClose"
          />
        </div>
        
        <div class="pt-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
            URL da Conexão:
          </label>
          <input
            v-model="connectionUrl"
            type="url"
            placeholder="https://exemplo.com"
            class="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-400 transition-colors duration-200"
            @keyup.enter="confirmAction"
            @keyup.escape="handleClose"
          />
        </div>
      </div>
      
      <!-- Botões -->
      <div class="px-6 py-4 bg-gray-50 dark:bg-slate-700/50 rounded-b-2xl flex justify-end gap-x-3">
        <button
          @click="handleClose"
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-slate-300 bg-white dark:bg-slate-600 border border-gray-300 dark:border-slate-500 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
        >
          Cancelar
        </button>
        <button
          @click="confirmAction"
          :disabled="!inputText.trim() || !connectionUrl.trim()"
          class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 border border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 disabled:cursor-not-allowed"
        >
          Adicionar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const inputText = ref('')
const connectionUrl = ref('')

const handleClose = () => {
  emit('close', inputText.value, connectionUrl.value)
  inputText.value = ''
  connectionUrl.value = ''
}

const confirmAction = () => {
  if (!inputText.value.trim() || !connectionUrl.value.trim()) {
    return
  }
    
  handleClose()
}

watch(() => props.isOpen, (newValue) => {
  if (!newValue) {
    inputText.value = ''
    connectionUrl.value = ''
  }
})
</script>
