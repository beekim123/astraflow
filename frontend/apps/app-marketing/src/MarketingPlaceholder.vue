<template>
  <main class="placeholder">
    <p class="eyebrow">AstraFlow Sub App</p>
    <h1>内容营销助手</h1>
    <p>阶段 6 实现小红书、公众号、抖音文案、图片和视频任务生成。</p>
    <pre>{{ data }}</pre>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, unwrap } from "@astraflow/shared-api"

const data = ref("加载占位数据...")
onMounted(async () => {
  data.value = JSON.stringify(await unwrap(api.get("/placeholders/marketing")), null, 2)
})
</script>

