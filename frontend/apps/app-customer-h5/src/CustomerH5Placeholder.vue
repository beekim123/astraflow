<template>
  <main class="placeholder">
    <p class="eyebrow">AstraFlow Sub App</p>
    <h1>H5 客服组件</h1>
    <p>阶段 6 做成可嵌入 App/小程序 WebView 的客服和数字人 H5。</p>
    <pre>{{ data }}</pre>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, unwrap } from "@astraflow/shared-api"

const data = ref("加载占位数据...")
onMounted(async () => {
  data.value = JSON.stringify(await unwrap(api.get("/placeholders/customer-h5")), null, 2)
})
</script>

