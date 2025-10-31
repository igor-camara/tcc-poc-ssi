<template>
    <LoginForm @login-success="handleLoginSuccess" />
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import LoginForm from '../components/LoginForm.vue'

const router = useRouter()

function handleLoginSuccess() {
  router.push({ name: 'dashboard' })
}
</script>
