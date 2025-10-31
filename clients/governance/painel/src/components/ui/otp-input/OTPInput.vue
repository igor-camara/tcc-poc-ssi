<template>
  <div class="flex gap-2 justify-center">
    <input
      v-for="(_digit, index) in digits"
      :key="index"
      :ref="el => inputRefs[index] = el as HTMLInputElement"
      v-model="digits[index]"
      type="text"
      inputmode="numeric"
      pattern="[0-9]"
      maxlength="1"
      class="otp-input w-12 h-14 text-center text-2xl font-bold bg-slate-700/50 border-2 border-slate-600 rounded-lg text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200"
      :placeholder="'•'"
      @input="handleInput(index, $event)"
      @keydown="handleKeyDown(index, $event)"
      @paste="handlePaste"
      @focus="handleFocus(index)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

interface Props {
  length?: number
  modelValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  length: 6,
  modelValue: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'complete': [value: string]
}>()

// State
const digits = ref<string[]>(Array(props.length).fill(''))
const inputRefs = ref<HTMLInputElement[]>([])

// Inicializar com o valor do modelValue
onMounted(() => {
  if (props.modelValue) {
    const chars = props.modelValue.split('').slice(0, props.length)
    chars.forEach((char, index) => {
      digits.value[index] = char
    })
  }
})

// Watch para mudanças externas no modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue !== digits.value.join('')) {
    const chars = newValue.split('').slice(0, props.length)
    digits.value = Array(props.length).fill('')
    chars.forEach((char, index) => {
      digits.value[index] = char
    })
  }
})

// Atualizar o valor quando os dígitos mudarem
watch(digits, (newDigits) => {
  const value = newDigits.join('')
  emit('update:modelValue', value)
  
  if (value.length === props.length && !value.includes('')) {
    emit('complete', value)
  }
}, { deep: true })

function handleInput(index: number, event: Event) {
  const input = event.target as HTMLInputElement
  const value = input.value
  
  // Permitir apenas números
  if (value && !/^\d$/.test(value)) {
    digits.value[index] = ''
    return
  }
  
  // Se um valor foi inserido, mover para o próximo campo
  if (value && index < props.length - 1) {
    inputRefs.value[index + 1]?.focus()
  }
}

function handleKeyDown(index: number, event: KeyboardEvent) {
  // Backspace
  if (event.key === 'Backspace') {
    if (!digits.value[index] && index > 0) {
      // Se o campo atual está vazio, voltar para o anterior
      inputRefs.value[index - 1]?.focus()
    } else {
      // Limpar o campo atual
      digits.value[index] = ''
    }
  }
  
  // Setas para navegação
  if (event.key === 'ArrowLeft' && index > 0) {
    event.preventDefault()
    inputRefs.value[index - 1]?.focus()
  }
  
  if (event.key === 'ArrowRight' && index < props.length - 1) {
    event.preventDefault()
    inputRefs.value[index + 1]?.focus()
  }
  
  // Delete
  if (event.key === 'Delete') {
    digits.value[index] = ''
  }
}

function handlePaste(event: ClipboardEvent) {
  event.preventDefault()
  const pastedData = event.clipboardData?.getData('text/plain')
  
  if (pastedData) {
    const numbers = pastedData.replace(/\D/g, '').slice(0, props.length)
    numbers.split('').forEach((char, index) => {
      if (index < props.length) {
        digits.value[index] = char
      }
    })
    
    // Focar no último campo preenchido ou no primeiro vazio
    const nextEmptyIndex = digits.value.findIndex(d => !d)
    const focusIndex = nextEmptyIndex === -1 ? props.length - 1 : nextEmptyIndex
    inputRefs.value[focusIndex]?.focus()
  }
}

function handleFocus(index: number) {
  // Selecionar o conteúdo ao focar
  inputRefs.value[index]?.select()
}

// Expor método para focar no primeiro campo
defineExpose({
  focus: () => inputRefs.value[0]?.focus()
})
</script>

<style scoped>
.otp-input {
  /* Remove spinners do número em alguns navegadores */
  appearance: textfield;
  -moz-appearance: textfield;
}

.otp-input::-webkit-outer-spin-button,
.otp-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Animação de foco */
.otp-input:focus {
  transform: scale(1.05);
}

/* Animação quando preenchido */
.otp-input:not(:placeholder-shown) {
  border-color: rgb(59 130 246);
  background-color: rgb(51 65 85 / 0.7);
}
</style>
