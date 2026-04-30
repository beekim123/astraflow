import { isLoggedIn } from "@astraflow/shared-auth"
import { createRouter, createWebHistory } from "vue-router"
import { getGateStatus } from "../api"

const protectedPrefixes = ["/admin", "/chat", "/audit", "/ticket", "/customer-h5", "/marketing"]
const gateFreePaths = ["/gate"]

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: () => import("../pages/HomePage.vue") },
    { path: "/gate", component: () => import("../pages/GatePage.vue") },
    { path: "/login", component: () => import("../pages/LoginPage.vue") },
    { path: "/systems", component: () => import("../pages/SystemHomePage.vue") },
    { path: "/admin/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "admin" } },
    { path: "/chat/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "chat" } },
    { path: "/audit/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "audit" } },
    { path: "/ticket/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "ticket" } },
    { path: "/customer-h5/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "customer" } },
    { path: "/marketing/:pathMatch(.*)*", component: () => import("../pages/MicroAppPage.vue"), meta: { app: "marketing" } },
  ],
})

router.beforeEach(async (to) => {
  const needsGate = !gateFreePaths.includes(to.path)
  if (needsGate) {
    const gate = await getGateStatus().catch(() => ({ gate_passed: false }))
    if (!gate.gate_passed) return `/gate?redirect=${encodeURIComponent(to.fullPath)}`
  }
  const needsLogin = protectedPrefixes.some((prefix) => to.path.startsWith(prefix))
  if (needsLogin && !isLoggedIn()) {
    return `/login?redirect=${encodeURIComponent(to.fullPath)}`
  }
  if (to.path === "/login" && isLoggedIn()) return "/systems"
  return true
})
