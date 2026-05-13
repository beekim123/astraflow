<template>
  <AiCrudPage
    title="模型路由"
    endpoint="/admin/ai/model-routes"
    :columns="columns"
    :form-fields="formFields"
    :defaults="defaults"
  />
</template>

<script setup lang="ts">
import AiCrudPage from "../shared/AiCrudPage.vue"

const columns = [
  { key: "mode", label: "模式" },
  { key: "display_name", label: "显示名" },
  { key: "provider", label: "Provider" },
  { key: "model", label: "模型" },
  { key: "priority", label: "优先级", type: "number" as const },
  { key: "health_status", label: "健康状态" },
  { key: "failure_count", label: "失败次数", type: "number" as const },
  { key: "temperature", label: "温度", type: "number" as const },
  { key: "max_tokens", label: "最大 Token", type: "number" as const },
  { key: "fallback_enabled", label: "允许切换", type: "boolean" as const },
  { key: "enabled", label: "状态", type: "boolean" as const },
]
const formFields = [
  { key: "mode", label: "模式" },
  { key: "display_name", label: "显示名" },
  { key: "provider", label: "Provider" },
  { key: "model", label: "模型" },
  { key: "priority", label: "优先级", type: "number" as const },
  { key: "temperature", label: "温度", type: "number" as const },
  { key: "max_tokens", label: "最大 Token", type: "number" as const },
  { key: "fallback_enabled", label: "允许切换", type: "boolean" as const },
  { key: "enabled", label: "状态", type: "boolean" as const },
]
const defaults = {
  mode: "mock",
  display_name: "开发 Mock",
  provider: "mock",
  model: "mock-assistant",
  priority: 100,
  health_status: "unknown",
  failure_count: 0,
  temperature: 70,
  max_tokens: 2048,
  fallback_enabled: true,
  enabled: true,
}
</script>
