<template>
  <main class="systems-screen">
    <header class="hero">
      <div>
        <p class="eyebrow">AstraFlow AI</p>
        <h1>企业级 AI 工作流门户</h1>
        <p>一个入口进入管理、对话、审核、工单、H5 客服和内容营销系统。</p>
      </div>
      <div class="hero-actions">
        <button @click="$router.push('/')">返回首页</button>
        <button v-if="loggedIn" @click="logout">退出登录</button>
      </div>
    </header>
    <section class="system-grid">
      <article v-for="card in cards" :key="card.path" class="system-card" @click="go(card.path)">
        <div class="icon">{{ card.icon }}</div>
        <span class="tag">Phase 1</span>
        <h2>{{ card.name }}</h2>
        <p>{{ descriptions[card.path] || "平台能力占位，后续阶段逐步增强。" }}</p>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { clearTokens, isLoggedIn } from "@astraflow/shared-auth"
import { getMenus, type MenuItem } from "../api"

const router = useRouter()
const menus = ref<MenuItem[]>([])
const loggedIn = computed(() => isLoggedIn())
const descriptions: Record<string, string> = {
  "/admin": "用户、角色、菜单、权限和操作日志管理。",
  "/chat": "AI 对话系统占位，第二阶段接入模型网关。",
  "/audit": "供应链金融材料智能预审占位。",
  "/ticket": "AI 工单分类、摘要和派单占位。",
  "/customer-h5": "可嵌入 App/小程序的 H5 客服组件占位。",
  "/marketing": "小红书、公众号、抖音文案和素材生成占位。",
}

const defaultCards: MenuItem[] = [
  { id: "admin", code: "system.admin", name: "管理系统", menu_type: "system", path: "/admin", component: "app-admin", icon: "管", sort: 10 },
  { id: "chat", code: "system.chat", name: "AI 对话", menu_type: "system", path: "/chat", component: "app-chat", icon: "聊", sort: 20 },
  { id: "audit", code: "system.audit", name: "智能审核", menu_type: "system", path: "/audit", component: "app-audit", icon: "审", sort: 30 },
  { id: "ticket", code: "system.ticket", name: "AI 工单", menu_type: "system", path: "/ticket", component: "app-ticket", icon: "工", sort: 40 },
  { id: "customer", code: "system.customer_h5", name: "H5 客服", menu_type: "system", path: "/customer-h5", component: "app-customer-h5", icon: "客", sort: 50 },
  { id: "marketing", code: "system.marketing", name: "内容营销助手", menu_type: "system", path: "/marketing", component: "app-marketing", icon: "营", sort: 60 },
]

const cards = computed(() => {
  if (!menus.value.length) return defaultCards
  const flat = flatten(menus.value)
  return flat.filter((item) => item.menu_type === "system" && item.status !== "disabled")
})

function flatten(items: MenuItem[]): MenuItem[] {
  return items.flatMap((item) => [item, ...(item.children ? flatten(item.children) : [])])
}

function go(path: string) {
  if (!isLoggedIn()) {
    router.push(`/login?redirect=${encodeURIComponent(path)}`)
    return
  }
  router.push(path)
}

function logout() {
  clearTokens()
  router.push("/login")
}

onMounted(async () => {
  if (isLoggedIn()) {
    menus.value = await getMenus()
  }
})
</script>
