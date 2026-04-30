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
        <el-menu-item v-for="item in nav" :key="item.key" :index="item.key">
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

const active = ref("users")
const nav = [
  { key: "users", label: "用户管理" },
  { key: "roles", label: "角色管理" },
  { key: "menus", label: "菜单管理" },
  { key: "permissions", label: "权限管理" },
  { key: "logs", label: "操作日志" },
]

const currentLabel = computed(() => nav.find((item) => item.key === active.value)?.label || "管理系统")
</script>
