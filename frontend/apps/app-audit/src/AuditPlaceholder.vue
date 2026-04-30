<template>
  <main class="placeholder">
    <p class="eyebrow">AstraFlow Sub App</p>
    <h1>智能审核中心</h1>
    <p>阶段 4 接入 OCR、规则引擎、审核报告和人工复核闭环。</p>
    <pre>{{ data }}</pre>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, unwrap } from "@astraflow/shared-api"

const data = ref("加载占位数据...")
onMounted(async () => {
  data.value = JSON.stringify(await unwrap(api.get("/placeholders/audit")), null, 2)
})
</script>

