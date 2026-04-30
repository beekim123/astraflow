<template>
  <main class="gate-screen">
    <section class="gate-card">
      <p class="eyebrow">AstraFlow AI</p>
      <h1>访问门禁</h1>
      <p class="muted">先完成一个简单验证码，再进入首页。通过后会记住一段时间，不会每次都打扰你。</p>
      <div class="captcha-box">
        <span>{{ question || "加载中..." }}</span>
        <button @click="loadCaptcha">换一题</button>
      </div>
      <input v-model="answer" placeholder="输入答案" @keyup.enter="submit" />
      <button class="primary" @click="submit">继续访问</button>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { getCaptcha, verifyCaptcha } from "../api"

const router = useRouter()
const route = useRoute()
const captchaId = ref("")
const question = ref("")
const answer = ref("")
const error = ref("")

async function loadCaptcha() {
  error.value = ""
  const data = await getCaptcha()
  captchaId.value = data.captcha_id
  question.value = data.question
}

async function submit() {
  try {
    await verifyCaptcha(captchaId.value, answer.value)
    const redirect = route.query.redirect?.toString()
    router.push(redirect || "/")
  } catch {
    error.value = "验证码错误或已过期"
    await loadCaptcha()
  }
}

onMounted(loadCaptcha)
</script>
