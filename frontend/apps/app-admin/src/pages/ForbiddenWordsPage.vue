<template>
  <AiCrudPage
    title="违禁词策略"
    endpoint="/admin/ai/forbidden-words"
    :columns="columns"
    :form-fields="formFields"
    :defaults="defaults"
  />
</template>

<script setup lang="ts">
import AiCrudPage from "../shared/AiCrudPage.vue"

const columns = [
  { key: "word", label: "词条" },
  { key: "category", label: "分类" },
  { key: "action", label: "动作" },
  { key: "enabled", label: "状态", type: "boolean" as const },
]
const formFields = columns
const defaults = { word: "", category: "default", action: "block", enabled: true }
</script>
