<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable placeholder="搜索用户名 / 昵称 / 邮箱" style="width: 260px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增用户</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="nickname" label="昵称" min-width="140" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="220">
        <template #default="{ row }">
          <el-tag v-for="role in row.roles" :key="role.id" effect="plain" style="margin-right: 6px">
            {{ role.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="620px" destroy-on-close>
    <el-form label-width="104px">
      <div class="form-grid">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="Boolean(form.id)" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="新增必填，编辑留空不修改" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="超级管理员">
          <el-switch v-model="form.is_superuser" />
        </el-form-item>
        <el-form-item class="full" label="角色">
          <el-select v-model="form.role_ids" multiple filterable placeholder="请选择角色" style="width: 100%">
            <el-option v-for="role in roleOptions" :key="role.id" :label="`${role.name}（${role.code}）`" :value="role.id" />
          </el-select>
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
type RoleBrief = { id: string; code: string; name: string }
type UserRow = {
  id: string
  username: string
  nickname: string
  status: string
  is_superuser: boolean
  created_at: string
  role_ids: string[]
  roles: RoleBrief[]
}

const rows = ref<UserRow[]>([])
const roleOptions = ref<RoleBrief[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })
const form = reactive({
  id: "",
  username: "",
  nickname: "",
  password: "",
  status: "active",
  is_superuser: false,
  role_ids: [] as string[],
})

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<UserRow>>(api.get("/admin/users", { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  const data = await unwrap<PageResult<RoleBrief>>(api.get("/admin/roles", { params: { page: 1, page_size: 200 } }))
  roleOptions.value = data.items
}

function resetForm() {
  Object.assign(form, {
    id: "",
    username: "",
    nickname: "",
    password: "",
    status: "active",
    is_superuser: false,
    role_ids: [],
  })
}

async function openCreate() {
  resetForm()
  await loadRoles()
  dialogVisible.value = true
}

async function openEdit(row: UserRow) {
  await loadRoles()
  Object.assign(form, {
    id: row.id,
    username: row.username,
    nickname: row.nickname,
    password: "",
    status: row.status,
    is_superuser: row.is_superuser,
    role_ids: [...row.role_ids],
  })
  dialogVisible.value = true
}

async function save() {
  if (!form.username) {
    ElMessage.warning("请输入用户名")
    return
  }
  if (!form.id && !form.password) {
    ElMessage.warning("请输入初始密码")
    return
  }

  saving.value = true
  try {
    const payload: Record<string, unknown> = {
      nickname: form.nickname || form.username,
      status: form.status,
      is_superuser: form.is_superuser,
      role_ids: form.role_ids,
    }
    if (form.password) payload.password = form.password
    if (form.id) {
      await unwrap(api.put(`/admin/users/${form.id}`, payload))
    } else {
      await unwrap(api.post("/admin/users", { ...payload, username: form.username }))
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

async function remove(row: UserRow) {
  try {
    await ElMessageBox.confirm(`确认删除用户「${row.username}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    })
    await unwrap(api.delete(`/admin/users/${row.id}`))
    ElMessage.success("删除成功")
    await load()
  } catch (error) {
    if (error !== "cancel") ElMessage.error(getApiErrorMessage(error))
  }
}

onMounted(load)
</script>
