<template>
  <header class="mobile-chat-header">
    <button class="mobile-icon-button" @click="$emit('openSidebar')">菜单</button>
    <div>
      <strong>AstraFlow</strong>
      <span>{{ mode }} · {{ taskTypeLabel }}</span>
    </div>
    <button class="mobile-icon-button" @click="$emit('createConversation')">新建</button>
  </header>

  <div class="mobile-route-controls">
    <select :value="mode" aria-label="模型路由" @change="updateMode">
      <option v-for="route in modelRoutes" :key="route.mode" :value="route.mode">
        {{ route.mode }} · {{ route.display_name || route.provider }}
      </option>
    </select>
    <select :value="taskType" aria-label="任务类型" @change="updateTaskType">
      <option v-for="item in TASK_TYPE_OPTIONS" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
  </div>

  <header class="chat-topbar">
    <div>
      <p class="eyebrow">AstraFlow AI</p>
      <h1>多模态聊天</h1>
    </div>
    <div class="route-controls">
      <select :value="mode" aria-label="模型路由" @change="updateMode">
        <option v-for="route in modelRoutes" :key="route.mode" :value="route.mode">
          {{ route.mode }} · {{ route.display_name || route.provider }}
        </option>
      </select>
      <select :value="taskType" aria-label="任务类型" @change="updateTaskType">
        <option v-for="item in TASK_TYPE_OPTIONS" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>
  </header>
</template>

<script setup lang="ts">
import { TASK_TYPE_OPTIONS } from "../constants"
import type { ModelRoute } from "../types"

defineProps<{
  modelRoutes: ModelRoute[]
  mode: string
  taskType: string
  taskTypeLabel: string
}>()

const emit = defineEmits<{
  "update:mode": [value: string]
  "update:taskType": [value: string]
  openSidebar: []
  createConversation: []
}>()

function updateMode(event: Event) {
  emit("update:mode", (event.target as HTMLSelectElement).value)
}

function updateTaskType(event: Event) {
  emit("update:taskType", (event.target as HTMLSelectElement).value)
}
</script>
