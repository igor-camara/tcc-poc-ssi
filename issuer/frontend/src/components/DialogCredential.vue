<template>
  <!-- Overlay e Dialog -->
  <div 
    v-if="isOpen"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    @click="handleClose"
  >
    <!-- Dialog -->
    <div 
      class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md mx-4 transform transition-all duration-300 ease-out max-h-[90vh] overflow-y-auto"
      @click.stop
    >
      <!-- Cabeçalho -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-slate-700">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Adicionar Nova Credencial
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
        <div class="pt-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
            Nome da credencial: *
          </label>
          <input
            v-model="credentialName"
            type="text"
            placeholder="Nome da credencial"
            class="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-400 transition-colors duration-200"
            @keyup.enter="confirmAction"
            @keyup.escape="handleClose"
          />
        </div>

        <div class="pt-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
            Versão da credencial: *
          </label>
          <input
            v-model="credentialVersion"
            type="text"
            placeholder="Versão da credencial (ex: 1.0)"
            class="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-400 transition-colors duration-200"
            @keyup.enter="confirmAction"
            @keyup.escape="handleClose"
          />
        </div>

        <!-- Seção de Atributos -->
        <div class="pt-4">
          <div class="flex items-center justify-between pt-3">
            <label class="block text-sm font-medium text-gray-700 dark:text-slate-300">
              Atributos da credencial:
            </label>
            <button
              @click="addAttribute"
              type="button"
              class="px-3 py-1 text-xs font-medium text-blue-600 hover:cursor-pointer dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 rounded-md transition-colors duration-200"
            >
              + Adicionar
            </button>
          </div>
          
          <div v-if="attributes.length === 0" class="text-sm text-gray-500 dark:text-slate-400 italic py-2">
            Nenhum atributo adicionado
          </div>
          
          <div class="pt-2">
            <div 
              v-for="(attribute, index) in attributes" 
              :key="index"
              class="flex items-center py-2"
            >
              <input
                v-model="attribute.name"
                type="text"
                placeholder="Nome do atributo"
                class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-400 transition-colors duration-200"
              />
              <button
                @click="removeAttribute(index)"
                type="button"
                class="p-2 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors duration-200"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Botões -->
      <div class="px-6 py-4 bg-gray-50 dark:bg-slate-700/50 rounded-b-2xl flex justify-end gap-x-3">
        <button
          @click="handleClose"
          class="px-4 py-2 text-sm font-medium text-gray-700 hover:cursor-pointer dark:text-slate-300 bg-white dark:bg-slate-600 border border-gray-300 dark:border-slate-500 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
        >
          {{ closeBtnText }}
        </button>
        <button
          @click="confirmAction"
          :disabled="!isFormValid || disabled"
          class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:cursor-pointer hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 border border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 disabled:cursor-not-allowed"
        >
          Criar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useInvitationStore } from '@/composables/useInvitationStore'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])
const invitationStore = useInvitationStore()

const credentialName = ref('')
const credentialVersion = ref('')
const attributes = ref([])
const connectionUrl = ref('')
const closeBtnText = ref('Cancelar')
const disabled = ref(false)

const isFormValid = computed(() => {
  return credentialName.value.trim() !== '' && 
         credentialVersion.value.trim() !== '' &&
         attributes.value.every(attr => attr.name.trim() !== '')
})

const addAttribute = () => {
  attributes.value.push({ name: '' })
}

const removeAttribute = (index) => {
  attributes.value.splice(index, 1)
}

const handleClose = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  credentialName.value = ''
  credentialVersion.value = ''
  attributes.value = []
  connectionUrl.value = ''
  disabled.value = false
  closeBtnText.value = 'Cancelar'
}

const confirmAction = async () => {
  if (!isFormValid.value) return
    
  const response = await invitationStore.createSchema(
    credentialName.value.trim(),
    credentialVersion.value.trim(),
    attributes.value.map(attr => attr.name.trim()).filter(name => name !== '')
  )

  if (response.success) {
    connectionUrl.value = response.data.invitation_url
    disabled.value = true
    closeBtnText.value = 'Fechar'
  } else {
    alert(response.error)
  }
}

watch(() => props.isOpen, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>
