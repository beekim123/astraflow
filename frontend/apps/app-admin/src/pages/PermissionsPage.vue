<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable placeholder="搜索权限编码 / 名称 / 资源" style="width: 280px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增权限</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="code" label="权限编码" min-width="180" />
      <el-table-column prop="name" label="权限名称" min-width="140" />
      <el-table-column prop="resource" label="资源" width="150" />
      <el-table-column prop="action" label="动作" width="130" />
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑权限' : '新增权限'" width="620px" destroy-on-close>
    <el-form label-width="100px">
      <div class="form-grid">
        <el-form-item label="权限编码">
          <el-input v-model="form.code" :disabled="Boolean(form.id)" placeholder="admin:users" />
        </el-form-item>
        <el-form-item label="权限名称">
          <el-input v-model="form.name" placeholder="用户管理" />
        </el-form-item>
        <el-form-item label="资源">
          <el-input v-model="form.resource" placeholder="users" />
        </el-form-item>
        <el-form-item label="动作">
          <el-input v-model="form.action" placeholder="manage / read" />
        </el-form-item>
        <el-form-item class="full" label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="权限说明" />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

type PageResult<T> = { items: T[]; total: number; page: number; page_size: number }
type PermissionRow = {
  id: string
  code: string
  name: string
  resource: string
  action: string
  description: string
}

const rows = ref<PermissionRow[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })
const form = reactive({
  id: "",
  code: "",
  name: "",
  resource: "",
  action: "",
  description: "",
})

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<PermissionRow>>(api.get("/admin/permissions", { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    id: "",
    code: "",
    name: "",
    resource: "",
    action: "",
    description: "",
  })
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: PermissionRow) {
  Object.assign(form, row)
  dialogVisible.value = true
}

async function save() {
  if (!form.code || !form.name || !form.resource || !form.action) {
    ElMessage.warning("请填写权限编码、名称、资源和动作")
    return
  }

  saving.value = true
  try {
    const payload = {
      code: form.code,
      name: form.name,
      resource: form.resource,
      action: form.action,
      description: form.description,
    }
    if (form.id) {
      await unwrap(api.put(`/admin/permissions/${form.id}`, payload))
    } else {
      await unwrap(api.post("/admin/permissions", payload))
    }
    ElMessage.success("保存成功")
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function remove(row: PermissionRow) {
  try {
    await ElMessageBox.confirm(`确认删除权限「${row.name}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    })
    await unwrap(api.delete(`/admin/permissions/${row.id}`))
    ElMessage.success("删除成功")
    await load()
  } catch (error) {
    if (error !== "cancel") ElMessage.error(getApiErrorMessage(error))
  }
}

onMounted(load)
</script>
