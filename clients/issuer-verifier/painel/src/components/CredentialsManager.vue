<template>
   <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4 pr-2">
         <div class="flex-1">
            <h2 class="text-2xl font-bold text-white mb-2">Controle de Credenciais</h2>
            <p class="text-blue-100">Gerencie os schemas de credenciais disponíveis</p>
         </div>
         <div class="flex-shrink-0">
            <Button @click="openCreateSheet" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
               <Plus class="w-4 h-4 mr-2" />
               Nova Credencial
            </Button>
         </div>
      </div>

      <!-- Filters and Search -->
      <div class="flex gap-4 pr-2">
         <div class="flex-1 min-w-0">
            <Input
               v-model="searchTerm"
               placeholder="Buscar por nome da credencial..."
               class="bg-white/20 border-white/30 text-white placeholder:text-blue-100"
            />
         </div>
         <div class="w-40 flex-shrink-0">
            <Select v-model="versionFilter" default-value="all">
               <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-blue-600/50 data-[placeholder]:text-blue-100">
                  <SelectValue placeholder="Filtrar por versão" />
               </SelectTrigger>
               <SelectContent class="bg-blue-900/95 backdrop-blur-md border-white/30 shadow-xl">
                  <SelectGroup>
                     <SelectItem
                        v-for="option in versionOptions"
                        :key="option.value"
                        :value="option.value"
                        class="!text-white hover:!bg-blue-600/60 focus:!bg-blue-600/70 focus:!text-white data-[highlighted]:bg-blue-600/60 data-[highlighted]:!text-white cursor-pointer transition-colors"
                     >
                        {{ option.label }}
                     </SelectItem>
                  </SelectGroup>
               </SelectContent>
            </Select>
         </div>
      </div>

      <!-- Credentials List -->
      <div class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-blue-600 scrollbar-track-white/10">
         <div v-if="!appStore.isLoading">
            <div
               v-for="credential in filteredCredentials"
               :key="credential.id"
               class="bg-white/10 backdrop-blur-md rounded-lg mt-4 border border-white/20 p-6 hover:bg-white/15 transition-all duration-200"
            >
               <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-4 flex-1">
                     <!-- Credential Icon -->
                     <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                        <CreditCard class="w-6 h-6 text-white" />
                     </div>
                     <!-- Credential Info -->
                     <div class="flex-1">
                        <div class="flex items-center space-x-3 mb-2">
                           <h3 class="text-lg font-semibold text-white">{{ credential.name }}</h3>
                           <span class="px-2 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-200">
                              v{{ credential.version }}
                           </span>
                        </div>
                        <div class="text-sm">
                           <div class="mb-1">
                              <span class="text-blue-200">Schema ID: </span>
                              <span class="text-white font-mono text-xs break-all">{{ credential.id }}</span>
                           </div>
                        </div>
                     </div>
                  </div>
                  <!-- Actions -->
                  <div class="flex items-center space-x-2">
                     <Button
                        @click="viewCredentialDetails(credential.id)"
                        variant="ghost"
                        size="sm"
                        class="text-blue-100 cursor-pointer hover:text-white hover:bg-white/10"
                        title="Ver Detalhes"
                     >
                        <Eye class="w-4 h-4" />
                     </Button>
                     <Button
                        @click="openEditSheet(credential.id)"
                        variant="ghost"
                        size="sm"
                        class="text-blue-300 cursor-pointer hover:text-blue-200 hover:bg-blue-500/20"
                        title="Editar Credencial"
                     >
                        <Edit class="w-4 h-4" />
                     </Button>
                  </div>
               </div>
            </div>

            <!-- Empty State -->
            <div v-if="filteredCredentials.length === 0" class="text-center py-12">
               <CreditCard class="w-16 h-16 text-white mx-auto mb-4" />
               <h3 class="text-xl font-semibold text-white mb-2">Nenhuma credencial encontrada</h3>
               <p class="text-blue-200 mb-6">
                  {{ searchTerm || (versionFilter && versionFilter !== 'all') ? 'Nenhuma credencial encontrada com os filtros aplicados' : 'Comece criando sua primeira credencial' }}
               </p>
               <Button v-if="!searchTerm && (!versionFilter || versionFilter === 'all')" @click="openCreateSheet" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">
                  <Plus class="w-4 h-4 mr-2" />
                  Criar Primeira Credencial
               </Button>
            </div>
         </div>

         <!-- Loading State -->
         <div v-else class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
         </div>
      </div>

      <!-- Details Modal -->
      <div
         v-if="showDetailsModal && credentialStore.currentCredential"
         class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
         @click="closeDetailsModal"
      >
         <div
            class="bg-gradient-to-br from-blue-900/90 to-blue-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto"
            @click.stop
         >
            <div class="flex justify-between items-center mb-6">
               <h3 class="text-2xl font-bold text-white">Detalhes da Credencial</h3>
               <Button class="cursor-pointer" @click="closeDetailsModal" variant="ghost" size="sm">
                  <X class="w-5 h-5 text-white" />
               </Button>
            </div>

            <div class="space-y-4">
               <div class="bg-white/5 rounded-lg p-4">
                  <label class="text-sm font-medium text-blue-200">Nome</label>
                  <p class="text-lg text-white font-semibold mt-1">{{ credentialStore.currentCredential.name }}</p>
               </div>

               <div class="bg-white/5 rounded-lg p-4">
                  <label class="text-sm font-medium text-blue-200">Versão</label>
                  <p class="text-lg text-white font-semibold mt-1">{{ credentialStore.currentCredential.version }}</p>
               </div>

               <div class="bg-white/5 rounded-lg p-4">
                  <label class="text-sm font-medium text-blue-200">Schema ID</label>
                  <p class="text-sm text-white font-mono break-all mt-1">{{ credentialStore.currentCredential.id }}</p>
               </div>

               <div class="bg-white/5 rounded-lg p-4">
                  <label class="text-sm font-medium text-blue-200 mb-2 block">Atributos</label>
                  <div class="flex flex-wrap gap-2">
                     <span
                        v-for="attr in credentialStore.currentCredential.attributes"
                        :key="attr"
                        class="px-3 py-1 bg-blue-600/30 text-blue-50 rounded-full text-sm font-medium border border-blue-500/30"
                     >
                        {{ attr }}
                     </span>
                  </div>
               </div>
            </div>

            <div class="flex justify-end space-x-3 pt-6 border-t border-white/20 mt-6">
               <Button @click="closeDetailsModal" class="bg-blue-600 cursor-pointer hover:bg-blue-700 text-white">
                  Fechar
               </Button>
            </div>
         </div>
      </div>

      <!-- Create/Edit Sheet -->
      <Sheet :open="isSheetOpen" @update:open="closeSheet">
         <SheetContent class="bg-gradient-to-br px-4 from-blue-900 via-blue-700 to-blue-800 border-l border-white/20 text-white overflow-y-auto">
            <SheetHeader>
               <SheetTitle class="text-white text-2xl">
                  {{ isEditMode ? 'Editar Credencial' : 'Nova Credencial' }}
               </SheetTitle>
               <SheetDescription class="text-blue-100">
                  {{ isEditMode ? 'Atualização criará uma nova versão da credencial' : 'Preencha as informações da credencial' }}
               </SheetDescription>
            </SheetHeader>

            <form @submit.prevent="handleSubmit" class="space-y-6 mt-6">
               <div class="space-y-2">
                  <label class="text-sm font-medium text-white">Nome da Credencial *</label>
                  <Input
                     v-model="credentialForm.name"
                     type="text"
                     placeholder="Ex: Certificado de Conclusão"
                     required
                     :disabled="isEditMode"
                     class="bg-white/20 border-white/30 text-white placeholder:text-blue-100"
                  />
               </div>

               <div class="space-y-2">
                  <label class="text-sm font-medium text-white">Versão *</label>
                  <Input
                     v-model="versionValue"
                     type="text"
                     placeholder="Ex: 1.0"
                     required
                     disabled
                     class="bg-white/20 border-white/30 text-white placeholder:text-blue-100"
                  />
               </div>

               <div class="space-y-3">
                  <div class="flex justify-between items-center">
                     <label class="text-sm font-medium text-white">Atributos *</label>
                     <Button
                        type="button"
                        @click="addAttribute"
                        size="sm"
                        variant="ghost"
                        class="text-blue-100 hover:text-white cursor-pointer hover:bg-white/10"
                     >
                        <Plus class="w-4 h-4 mr-1" />
                        Adicionar
                     </Button>
                  </div>

                  <div
                     v-for="(_, index) in credentialForm.attributes"
                     :key="index"
                     class="flex gap-2"
                  >
                     <Input
                        v-model="credentialForm.attributes[index]"
                        type="text"
                        placeholder="Nome do atributo (sem acentos)"
                        required
                        @input="sanitizeAttribute(index)"
                        class="flex-1 bg-white/20 border-white/30 text-white placeholder:text-blue-100"
                     />
                     <Button
                        type="button"
                        @click="removeAttribute(index)"
                        size="sm"
                        variant="ghost"
                        class="text-red-300 hover:text-red-200 hover:bg-red-500/20"
                        :disabled="credentialForm.attributes.length === 1"
                     >
                        <Trash2 class="w-4 h-4" />
                     </Button>
                  </div>
                  <p v-if="credentialForm.attributes.length == 1 && !credentialForm.attributes[0]" class="text-xs text-blue-200">
                     Adicione pelo menos um atributo para a credencial
                  </p>
               </div>

               <SheetFooter class="flex pt-6 border-t border-white/20">
                <Button
                     type="submit"
                     :disabled="appStore.isLoading || !isFormValid"
                     class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white"
                  >
                     {{ appStore.isLoading ? 'Salvando...' : (isEditMode ? 'Atualizar' : 'Criar') }}
                  </Button>
                  <Button
                     type="button"
                     @click="closeSheet"
                     variant="ghost"
                     class="text-blue-100 cursor-pointer"
                  >
                     Cancelar
                  </Button>
               </SheetFooter>
            </form>
         </SheetContent>
      </Sheet>
   </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, CreditCard, Eye, Edit, Trash2, X } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
   Sheet,
   SheetContent,
   SheetDescription,
   SheetFooter,
   SheetHeader,
   SheetTitle,
} from '@/components/ui/sheet'
import {
   Select,
   SelectContent,
   SelectGroup,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from '@/components/ui/select'
import { useAppStore, useCredentialStore } from '@/stores'
import type { CredentialFormData } from '@/stores/credential'

const appStore = useAppStore()
const credentialStore = useCredentialStore()

const searchTerm = ref('')
const versionFilter = ref('all')
const showDetailsModal = ref(false)
const isSheetOpen = ref(false)
const isEditMode = ref(false)
const editingSchemaId = ref<string | null>(null)

const credentialForm = ref<CredentialFormData>({
   name: '',
   version: '1.0',
   attributes: ['']
})

const versionOptions = computed(() => {
   const versions = new Set(credentialStore.credentials.map(c => c.version))
   return [
      { value: 'all', label: 'Todas as versões' },
      ...Array.from(versions).sort().map(v => ({ value: v, label: `v${v}` }))
   ]
})

const filteredCredentials = computed(() => {
   let result = credentialStore.credentials

   if (searchTerm.value) {
      const search = searchTerm.value.toLowerCase()
      result = result.filter(credential => {
         return credential.name.toLowerCase().includes(search) || 
                credential.id.toLowerCase().includes(search)
      })
   }

   if (versionFilter.value && versionFilter.value !== 'all') {
      result = result.filter(credential => {
         return credential.version === versionFilter.value
      })
   }

   return result
})

const isFormValid = computed(() => {
   return (
      credentialForm.value.name.trim() !== '' &&
      credentialForm.value.version.trim() !== '' &&
      credentialForm.value.attributes.length > 0 &&
      credentialForm.value.attributes.every(attr => attr.trim() !== '')
   )
})

const versionValue = computed(() => {
    if (isEditMode.value) {
        return calculateNewVersion()
    }
    return credentialForm.value.version
})

function calculateNewVersion(): string {
   const versionParts = credentialForm.value.version.split('.')
   const majorVersion = parseInt(versionParts[0] || '0') || 0
   return `${majorVersion + 1}.0`
}

async function viewCredentialDetails(schemaId: string) {
   const credential = credentialStore.credentials.find(c => c.id === schemaId)
   if (credential) {
      credentialStore.currentCredential = credential
      showDetailsModal.value = true
   } else {
      await credentialStore.fetchCredentialDetails(schemaId)
      showDetailsModal.value = true
   }
}

function closeDetailsModal() {
   showDetailsModal.value = false
   credentialStore.clearCurrentCredential()
}

function openCreateSheet() {
   isEditMode.value = false
   editingSchemaId.value = null
   credentialForm.value = {
      name: '',
      version: '1.0',
      attributes: ['']
   }
   isSheetOpen.value = true
}

async function openEditSheet(schemaId: string) {
   const credential = credentialStore.credentials.find(c => c.id === schemaId)
   
   if (credential) {
      isEditMode.value = true
      editingSchemaId.value = schemaId
      credentialForm.value = {
         name: credential.name,
         version: credential.version,
         attributes: [...credential.attributes]
      }
      isSheetOpen.value = true
   }
}

function closeSheet() {
   isSheetOpen.value = false
   setTimeout(() => {
      isEditMode.value = false
      editingSchemaId.value = null
      credentialForm.value = {
         name: '',
         version: '1.0',
         attributes: ['']
      }
   }, 300)
}

function addAttribute() {
   credentialForm.value.attributes.push('')
}

function removeAttribute(index: number) {
   if (credentialForm.value.attributes.length > 1) {
      credentialForm.value.attributes.splice(index, 1)
   }
}

function sanitizeAttribute(index: number) {
   const value = credentialForm.value.attributes[index]
   if (!value) return
   
   // Remove acentos e normaliza o texto
   const normalized = value
      .normalize('NFD') // Decompõe caracteres acentuados
      .replace(/[\u0300-\u036f]/g, '') // Remove marcas diacríticas
      .replace(/[^a-zA-Z0-9_]/g, '_') // Substitui caracteres especiais por underscore
      .replace(/_+/g, '_') // Remove underscores consecutivos
   
   credentialForm.value.attributes[index] = normalized
}

async function handleSubmit() {
   if (!isFormValid.value) return

   const cleanedForm = {
      ...credentialForm.value,
      attributes: credentialForm.value.attributes.filter(attr => attr.trim() !== '')
   }

   let result
   if (isEditMode.value) {
      result = await credentialStore.updateCredential(cleanedForm)
   } else {
      result = await credentialStore.createCredential(cleanedForm)
   }

   if (result !== null) {
      closeSheet()
   }
}

onMounted(async () => {
   await credentialStore.fetchCredentials()
})
</script>
