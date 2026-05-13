<template>
  <AiCrudPage title="模型调用日志" endpoint="/admin/ai/model-call-logs" :columns="columns" readonly />
</template>

<script setup lang="ts">
import AiCrudPage from "../shared/AiCrudPage.vue"

const columns = [
  { key: "created_at", label: "时间" },
  { key: "request_id", label: "请求 ID" },
  { key: "provider", label: "Provider" },
  { key: "model", label: "模型" },
  { key: "mode", label: "模式" },
  { key: "input_tokens", label: "输入 Token", type: "number" as const },
  { key: "output_tokens", label: "输出 Token", type: "number" as const },
  { key: "latency_ms", label: "耗时 ms", type: "number" as const },
  { key: "fallback_used", label: "降级", type: "boolean" as const },
  { key: "status", label: "状态" },
  { key: "error_message", label: "错误信息" },
]
</script>
