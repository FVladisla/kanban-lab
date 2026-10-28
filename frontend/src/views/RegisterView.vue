<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const role = ref('developer')
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = ''
  try {
    await auth.register(email.value, password.value, role.value)
    router.push('/projects')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Регистрация</h1>
      <input v-model="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Пароль (мин. 8 символов)" />
      <select v-model="role">
        <option value="developer">Разработчик</option>
        <option value="manager">Менеджер</option>
        <option value="admin">Администратор</option>
      </select>
      <button class="btn" @click="submit">Зарегистрироваться</button>
      <p class="error" v-if="error">{{ error }}</p>
      <p class="link">Есть аккаунт? <router-link to="/login">Вход</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.auth-card { background: white; padding: 32px; border-radius: 8px; width: 340px; display: flex; flex-direction: column; gap: 12px; box-shadow: 0 4px 16px rgba(0,0,0,.08); }
.auth-card h1 { font-size: 20px; text-align: center; }
.error { color: #de350b; font-size: 13px; }
.link { font-size: 13px; text-align: center; }
</style>
