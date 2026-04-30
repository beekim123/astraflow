<template>
  <section>
    <header class="page-head">
      <div>
        <p>Management</p>
        <h2>{{ title }}</h2>
      </div>
      <div>
        <button @click="load">刷新</button>
        <button class="primary" @click="create">快速新增</button>
      </div>
    </header>
    <table>
      <thead>
        <tr>
          <th v-for="col in columns" :key="col">{{ col }}</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td v-for="col in columns" :key="col">{{ format(row[col]) }}</td>
          <td><button class="danger" @click="remove(row.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

const props = defineProps<{
  title: string
  endpoint: string
  columns: string[]
  factory: () => Record<string, unknown>
}>()

const rows = ref<any[]>([])
const error = ref("")

function format(value: unknown) {
  return Array.isArray(value) ? value.join(", ") : String(value ?? "")
}

async function load() {
  rows.value = await unwrap<any[]>(api.get(props.endpoint))
}

async function create() {
  error.value = ""
  try {
    await unwrap(api.post(props.endpoint, props.factory()))
    await load()
  } catch (err) {
    error.value = getApiErrorMessage(err, "创建失败，可能缺少关联 ID。")
  }
}

async function remove(id: string) {
  await unwrap(api.delete(`${props.endpoint}/${id}`))
  await load()
}

onMounted(load)
</script>
