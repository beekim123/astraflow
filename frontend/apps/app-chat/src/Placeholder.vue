<template>
  <main class="placeholder">
    <p class="eyebrow">AstraFlow Sub App</p>
    <h1>{{ title }}</h1>
    <p>{{ next }}</p>
    <pre>{{ data }}</pre>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, unwrap } from "@astraflow/shared-api"

const props = defineProps<{ title: string; endpoint: string; next: string }>()
const data = ref("加载占位数据...")

onMounted(async () => {
  data.value = JSON.stringify(await unwrap(api.get(props.endpoint)), null, 2)
})
</script>

