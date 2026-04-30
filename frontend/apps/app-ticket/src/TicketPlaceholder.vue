<template>
  <main class="placeholder">
    <p class="eyebrow">AstraFlow Sub App</p>
    <h1>AI 工单中心</h1>
    <p>阶段 5 实现工单摘要、分类、定级、推荐处理人和流转建议。</p>
    <pre>{{ data }}</pre>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, unwrap } from "@astraflow/shared-api"

const data = ref("加载占位数据...")
onMounted(async () => {
  data.value = JSON.stringify(await unwrap(api.get("/placeholders/ticket")), null, 2)
})
</script>

