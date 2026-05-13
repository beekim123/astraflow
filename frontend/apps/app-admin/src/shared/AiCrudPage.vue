<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable :placeholder="`搜索${title}`" style="width: 280px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button v-if="!readonly" type="primary" @click="openCreate">新增</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column v-for="column in columns" :key="column.key" :prop="column.key" :label="column.label" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <el-tag v-if="column.type === 'boolean'" :type="row[column.key] ? 'success' : 'info'">
            {{ row[column.key] ? "启用" : "停用" }}
          </el-tag>
          <span v-else>{{ format(row[column.key]) }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="!readonly" label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? `编辑${title}` : `新增${title}`" width="680px" destroy-on-close>
    <el-form label-width="120px">
      <el-form-item v-for="field in formFields" :key="field.key" :label="field.label">
        <el-switch v-if="field.type === 'boolean'" v-model="form[field.key]" />
        <el-input-number v-else-if="field.type === 'number'" v-model="form[field.key]" :min="0" style="width: 100%" />
        <el-input v-else-if="field.type === 'textarea'" v-model="form[field.key]" type="textarea" :rows="5" />
        <el-input v-else v-model="form[field.key]" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import { ElMessage } from "element-plus"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

type PageResult<T> = { items: T[]; total: number; page: number; page_size: number }
type Field = { key: string; label: string; type?: "text" | "textarea" | "number" | "boolean" }

const props = defineProps<{
  title: string
  endpoint: string
  columns: Field[]
  formFields?: Field[]
  defaults?: Record<string, unknown>
  readonly?: boolean
}>()

const rows = ref<Record<string, any>[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })
const form = reactive<Record<string, any>>({})

function format(value: unknown) {
  if (value === null || value === undefined) return ""
  if (typeof value === "object") return JSON.stringify(value)
  return String(value)
}

function resetForm(row?: Record<string, any>) {
  Object.keys(form).forEach((key) => delete form[key])
  Object.assign(form, props.defaults || {}, row || {})
}

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<Record<string, any>>>(api.get(props.endpoint, { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, "加载失败"))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Record<string, any>) {
  resetForm(row)
  dialogVisible.value = true
}

async function save() {
  saving.value = true
  try {
    const payload = { ...form }
    const id = payload.id
    delete payload.id
    delete payload.created_at
    delete payload.updated_at
    if (id) {
      await unwrap(api.put(`${props.endpoint}/${id}`, payload))
    } else {
      await unwrap(api.post(props.endpoint, payload))
    }
    ElMessage.success("保存成功")
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, "保存失败"))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
