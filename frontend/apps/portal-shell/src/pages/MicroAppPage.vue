<template>
  <main class="micro-shell">
    <nav class="topbar">
      <button @click="$router.push('/systems')">返回系统入口</button>
      <span>{{ current.title }}</span>
    </nav>
    <iframe
      class="micro-frame"
      :name="current.name"
      :src="current.url"
      :title="current.title"
      @error="loadError = true"
    ></iframe>
    <p v-if="loadError" class="micro-error">子系统加载失败，请确认本地服务和 Nginx 代理已启动。</p>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const loadError = ref(false)
const withSlash = (url: string) => (url.endsWith("/") ? url : `${url}/`)
const appMap = {
  admin: { name: "admin", title: "管理系统", baseRoute: "/admin", url: withSlash(import.meta.env.VITE_APP_ADMIN_URL || "/micro/admin/") },
  chat: { name: "chat", title: "AI 对话", baseRoute: "/chat", url: withSlash(import.meta.env.VITE_APP_CHAT_URL || "/micro/chat/") },
  audit: { name: "audit", title: "智能审核", baseRoute: "/audit", url: withSlash(import.meta.env.VITE_APP_AUDIT_URL || "/micro/audit/") },
  ticket: { name: "ticket", title: "AI 工单", baseRoute: "/ticket", url: withSlash(import.meta.env.VITE_APP_TICKET_URL || "/micro/ticket/") },
  customer: { name: "customer", title: "H5 客服", baseRoute: "/customer-h5", url: withSlash(import.meta.env.VITE_APP_CUSTOMER_H5_URL || "/micro/customer/") },
  marketing: { name: "marketing", title: "内容营销助手", baseRoute: "/marketing", url: withSlash(import.meta.env.VITE_APP_MARKETING_URL || "/micro/marketing/") },
}

const current = computed(() => appMap[(route.meta.app as keyof typeof appMap) || "chat"])

watch(current, () => {
  loadError.value = false
})
</script>
