<template>
  <AiCrudPage
    title="Prompt 模板"
    endpoint="/admin/ai/prompts"
    :columns="columns"
    :form-fields="formFields"
    :defaults="defaults"
  />
</template>

<script setup lang="ts">
import AiCrudPage from "../shared/AiCrudPage.vue"

const columns = [
  { key: "name", label: "名称" },
  { key: "scene", label: "场景" },
  { key: "version", label: "版本" },
  { key: "enabled", label: "状态", type: "boolean" as const },
]
const formFields = [
  { key: "name", label: "名称" },
  { key: "scene", label: "场景" },
  { key: "version", label: "版本" },
  { key: "content", label: "模板内容", type: "textarea" as const },
  { key: "enabled", label: "启用", type: "boolean" as const },
]
const defaults = { name: "新 Prompt", scene: "chat-general", version: "v1", content: "", variables_json: {}, enabled: true }
</script>
