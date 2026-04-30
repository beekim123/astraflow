<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable placeholder="搜索角色编码 / 名称" style="width: 260px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增角色</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="code" label="角色编码" min-width="150" />
      <el-table-column prop="name" label="角色名称" min-width="140" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="菜单数" width="100">
        <template #default="{ row }">{{ row.menu_ids.length }}</template>
      </el-table-column>
      <el-table-column label="权限数" width="100">
        <template #default="{ row }">{{ row.permission_ids.length }}</template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
      <el-table-column label="操作" width="190" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑/授权</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色授权' : '新增角色'" width="780px" destroy-on-close @opened="syncCheckedMenus">
    <el-form label-width="100px">
      <div class="form-grid">
        <el-form-item label="角色编码">
          <el-input v-model="form.code" :disabled="Boolean(form.id)" placeholder="role_code" />
        </el-form-item>
        <el-form-item label="角色名称">
          <el-input v-model="form.name" placeholder="角色名称" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item class="full" label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="角色用途说明" />
        </el-form-item>
        <el-form-item class="full" label="接口权限">
          <el-select v-model="form.permission_ids" multiple filterable collapse-tags collapse-tags-tooltip placeholder="请选择接口权限" style="width: 100%">
            <el-option v-for="permission in permissionOptions" :key="permission.id" :label="`${permission.name}（${permission.code}）`" :value="permission.id" />
          </el-select>
        </el-form-item>
        <el-form-item class="full" label="菜单授权">
          <div class="menu-tree-box">
            <el-tree
              ref="menuTreeRef"
              :data="menuTree"
              node-key="id"
              show-checkbox
              check-strictly
              default-expand-all
              :props="{ label: 'name', children: 'children' }"
            />
          </div>
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
import { nextTick, onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

type PageResult<T> = { items: T[]; total: number; page: number; page_size: number }
type PermissionRow = { id: string; code: string; name: string }
type MenuRow = { id: string; name: string; children?: MenuRow[] }
type RoleRow = {
  id: string
  code: string
  name: string
  description: string
  status: string
  permission_ids: string[]
  menu_ids: string[]
}

const rows = ref<RoleRow[]>([])
const permissionOptions = ref<PermissionRow[]>([])
const menuTree = ref<MenuRow[]>([])
const menuTreeRef = ref()
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })
const form = reactive({
  id: "",
  code: "",
  name: "",
  description: "",
  status: "active",
  permission_ids: [] as string[],
  menu_ids: [] as string[],
})

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<RoleRow>>(api.get("/admin/roles", { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  const [permissions, menus] = await Promise.all([
    unwrap<PageResult<PermissionRow>>(api.get("/admin/permissions", { params: { page: 1, page_size: 200 } })),
    unwrap<MenuRow[]>(api.get("/admin/menus/tree")),
  ])
  permissionOptions.value = permissions.items
  menuTree.value = menus
}

function resetForm() {
  Object.assign(form, {
    id: "",
    code: "",
    name: "",
    description: "",
    status: "active",
    permission_ids: [],
    menu_ids: [],
  })
}

async function openCreate() {
  resetForm()
  await loadOptions()
  dialogVisible.value = true
}

async function openEdit(row: RoleRow) {
  await loadOptions()
  Object.assign(form, {
    id: row.id,
    code: row.code,
    name: row.name,
    description: row.description,
    status: row.status,
    permission_ids: [...row.permission_ids],
    menu_ids: [...row.menu_ids],
  })
  dialogVisible.value = true
}

async function syncCheckedMenus() {
  await nextTick()
  menuTreeRef.value?.setCheckedKeys(form.menu_ids)
}

async function save() {
  if (!form.code || !form.name) {
    ElMessage.warning("请填写角色编码和名称")
    return
  }

  saving.value = true
  try {
    const payload = {
      name: form.name,
      description: form.description,
      status: form.status,
      permission_ids: form.permission_ids,
      menu_ids: menuTreeRef.value?.getCheckedKeys(false) || [],
    }
    if (form.id) {
      await unwrap(api.put(`/admin/roles/${form.id}`, payload))
    } else {
      await unwrap(api.post("/admin/roles", { ...payload, code: form.code }))
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

async function remove(row: RoleRow) {
  try {
    await ElMessageBox.confirm(`确认删除角色「${row.name}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    })
    await unwrap(api.delete(`/admin/roles/${row.id}`))
    ElMessage.success("删除成功")
    await load()
  } catch (error) {
    if (error !== "cancel") ElMessage.error(getApiErrorMessage(error))
  }
}

onMounted(load)
</script>
