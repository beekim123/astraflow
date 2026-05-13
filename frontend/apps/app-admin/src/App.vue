<template>
  <el-container class="admin-shell">
    <el-aside width="236px" class="admin-aside">
      <div class="brand">
        <span>A</span>
        <div>
          <strong>AstraFlow</strong>
          <small>Admin Console</small>
        </div>
      </div>
      <el-menu :default-active="active" class="side-menu" @select="active = $event">
        <el-sub-menu index="system">
          <template #title>系统管理</template>
          <el-menu-item v-for="item in systemNav" :key="item.key" :index="item.key">
            <span>{{ item.label }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="ai">
          <template #title>AI 管理</template>
          <el-menu-item v-for="item in aiNav" :key="item.key" :index="item.key">
            <span>{{ item.label }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-for="item in standaloneNav" :key="item.key" :index="item.key">
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div>
          <p>Phase 1 RBAC Platform</p>
          <h1>{{ currentLabel }}</h1>
        </div>
      </el-header>
      <el-main class="admin-main">
        <UsersPage v-if="active === 'users'" />
        <RolesPage v-if="active === 'roles'" />
        <MenusPage v-if="active === 'menus'" />
        <PermissionsPage v-if="active === 'permissions'" />
        <AuditLogsPage v-if="active === 'logs'" />
        <ModelRoutesPage v-if="active === 'model-routes'" />
        <PromptTemplatesPage v-if="active === 'prompts'" />
        <ForbiddenWordsPage v-if="active === 'forbidden-words'" />
        <ModelCallLogsPage v-if="active === 'model-call-logs'" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from "vue"
import UsersPage from "./pages/UsersPage.vue"
import RolesPage from "./pages/RolesPage.vue"
import MenusPage from "./pages/MenusPage.vue"
import PermissionsPage from "./pages/PermissionsPage.vue"
import AuditLogsPage from "./pages/AuditLogsPage.vue"
import ModelRoutesPage from "./pages/ModelRoutesPage.vue"
import PromptTemplatesPage from "./pages/PromptTemplatesPage.vue"
import ForbiddenWordsPage from "./pages/ForbiddenWordsPage.vue"
import ModelCallLogsPage from "./pages/ModelCallLogsPage.vue"

const active = ref("users")
const systemNav = [
  { key: "users", label: "用户管理" },
  { key: "roles", label: "角色管理" },
  { key: "menus", label: "菜单管理" },
  { key: "permissions", label: "权限管理" },
  { key: "logs", label: "操作日志" },
]
const aiNav = [
  { key: "model-routes", label: "模型路由" },
  { key: "prompts", label: "Prompt 模板" },
  { key: "forbidden-words", label: "违禁词策略" },
  { key: "model-call-logs", label: "模型调用日志" },
]
const standaloneNav: { key: string; label: string }[] = []
const nav = [...systemNav, ...aiNav, ...standaloneNav]

const currentLabel = computed(() => nav.find((item) => item.key === active.value)?.label || "管理系统")
</script>
