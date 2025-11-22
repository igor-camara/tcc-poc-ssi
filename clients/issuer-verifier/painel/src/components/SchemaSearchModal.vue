<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50" @click.self="onClose">
    <div class="bg-gradient-to-br from-blue-900/90 to-blue-950/90 backdrop-blur-md rounded-xl border border-white/20 p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto" @click.stop>
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-bold text-white">Buscar Schema</h3>
        <button @click="onClose" class="text-white hover:text-blue-200 transition-colors cursor-pointer">
          <X class="w-6 h-6" />
        </button>
      </div>
      <div class="flex gap-2 mb-4">
        <Input v-model="search" placeholder="Buscar por nome ou ID..." class="bg-white/20 border-white/30 text-white" @keyup.enter="fetchSchemas(1)" />
        <Button @click="fetchSchemas(1)" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">Buscar</Button>
      </div>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div v-if="schemas.length === 0" class="text-center text-blue-100 py-8">Nenhum schema encontrado.</div>
        <div v-else class="space-y-2">
          <div v-for="schema in schemas" :key="schema.id" class="bg-white/10 rounded-lg p-4 flex justify-between items-center">
            <div>
              <div class="text-white font-semibold">{{ schema.name }}</div>
              <div class="text-blue-200 text-xs">ID: <span class="font-mono">{{ schema.id }}</span></div>
            </div>
            <Button @click="() => onSelect(schema)" class="bg-blue-600 hover:bg-blue-700 text-white cursor-pointer">Selecionar</Button>
          </div>
        </div>
        <div class="flex justify-between items-center mt-6">
          <Button :disabled="page === 1" @click="fetchSchemas(page - 1)" variant="ghost" class="text-blue-100 cursor-pointer">Anterior</Button>
          <span class="text-blue-100">Página {{ page }}</span>
          <Button :disabled="!hasNextPage" @click="fetchSchemas(page + 1)" variant="ghost" class="text-blue-100 cursor-pointer">Próxima</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

defineProps<{
  onSelect: (schema: any) => void
  onClose: () => void
}>()

const search = ref('')
const schemas = ref<any[]>([])
const page = ref(1)
const pageSize = 10
const hasNextPage = ref(false)
const loading = ref(false)

async function fetchSchemaDetails(schemaId: string) {
  try {
    const response = await fetch(`http://localhost:8002/api/ledger/schemas/${encodeURIComponent(schemaId)}`)
    if (!response.ok) {
      console.error('Failed to fetch schema details for', schemaId)
      return []
    }
    const data = await response.json()
    const schemaData = data.data || data
    return schemaData.attrNames || []
  } catch (error) {
    console.error('Error fetching schema details:', error)
    return []
  }
}

async function fetchSchemas(newPage = 1) {
  loading.value = true
  page.value = newPage
  let url = `http://localhost:8002/api/ledger/schemas-redirect?page=${newPage}&page_size=${pageSize}`
  if (search.value) {
    url += `&search=${encodeURIComponent(search.value)}`
  }
  try {
    const res = await fetch(url)
    const data = await res.json()
    // Ajuste para o novo formato de resposta
    const items = data.data?.items || []
    
    // Busca os detalhes de cada schema para obter os atributos
    const schemasWithDetails = await Promise.all(
      items.map(async (item: any) => {
        const attrNames = await fetchSchemaDetails(item.schema_id)
        return {
          id: item.schema_id,
          name: item.credential_name,
          attrNames: attrNames,
          raw: item
        }
      })
    )
    
    schemas.value = schemasWithDetails
    const totalPages = data.data?.total_pages || 1
    hasNextPage.value = newPage < totalPages
  } catch (e) {
    schemas.value = []
    hasNextPage.value = false
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSchemas(1)
})

watch(search, (val) => {
  if (!val) fetchSchemas(1)
})
</script>
