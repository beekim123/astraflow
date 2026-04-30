<template>
  <main class="login-screen">
    <section class="login-panel">
      <div>
        <p class="eyebrow">Enterprise AI Workflow</p>
        <h1>登录 AstraFlow</h1>
        <p class="muted">第一阶段默认账号：admin / Admin@123456，member / Member@123456。</p>
      </div>
      <form @submit.prevent="submit">
        <input v-model="username" placeholder="用户名" />
        <input v-model="password" placeholder="密码" type="password" />
        <button class="primary">登录</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "../stores/auth"

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const username = ref("admin")
const password = ref("Admin@123456")
const error = ref("")

async function submit() {
  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect?.toString()
    router.push(redirect || "/systems")
  } catch {
    error.value = "登录失败，请检查用户名或密码"
  }
}
</script>

