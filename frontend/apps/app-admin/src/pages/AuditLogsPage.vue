<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable placeholder="搜索 request_id / 路径 / IP" style="width: 300px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="created_at" label="时间" min-width="190" />
      <el-table-column prop="request_id" label="请求 ID" min-width="240" show-overflow-tooltip />
      <el-table-column prop="method" label="方法" width="90" />
      <el-table-column prop="path" label="路径" min-width="240" show-overflow-tooltip />
      <el-table-column prop="ip" label="IP" min-width="140" />
      <el-table-column prop="status_code" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status_code < 400 ? 'success' : 'danger'">{{ row.status_code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="user_agent" label="User Agent" min-width="240" show-overflow-tooltip />
    </el-table>

    <div class="pagination-row">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="load"
        @current-change="load"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import { ElMessage } from "element-plus"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

type PageResult<T> = { items: T[]; total: number; page: number; page_size: number }
type AuditLogRow = {
  id: string
  request_id: string
  method: string
  path: string
  ip: string
  status_code: number
  user_agent: string
  created_at: string
}

const rows = ref<AuditLogRow[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<AuditLogRow>>(api.get("/admin/audit-logs", { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, "加载失败"))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
