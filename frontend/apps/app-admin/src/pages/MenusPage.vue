<template>
  <el-card class="page-card">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="query.keyword" clearable placeholder="搜索菜单编码 / 名称 / 路径" style="width: 280px" @keyup.enter="load" />
        <el-button @click="load">搜索</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增菜单</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="name" label="菜单名称" min-width="150" />
      <el-table-column prop="code" label="编码" min-width="180" show-overflow-tooltip />
      <el-table-column prop="menu_type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.menu_type === 'system' ? 'warning' : 'info'">{{ row.menu_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="app_key" label="App Key" width="140" />
      <el-table-column prop="path" label="路径" min-width="160" />
      <el-table-column prop="component" label="组件" min-width="160" show-overflow-tooltip />
      <el-table-column prop="sort" label="排序" width="90" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.visible && row.status === 'active' ? 'success' : 'info'">
            {{ row.visible ? row.status : "hidden" }}
          </el-tag>
        </template>
      </el-table-column>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑菜单' : '新增菜单'" width="720px" destroy-on-close>
    <el-form label-width="112px">
      <div class="form-grid">
        <el-form-item label="菜单编码">
          <el-input v-model="form.code" placeholder="system.chat / admin.users" />
        </el-form-item>
        <el-form-item label="菜单名称">
          <el-input v-model="form.name" placeholder="菜单名称" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-select v-model="form.parent_id" clearable filterable placeholder="无父级" style="width: 100%">
            <el-option v-for="menu in parentOptions" :key="menu.id" :label="menu.label" :value="menu.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="菜单类型">
          <el-select v-model="form.menu_type" style="width: 100%">
            <el-option label="system 子系统入口" value="system" />
            <el-option label="page 系统内页面" value="page" />
            <el-option label="button 按钮权限" value="button" />
          </el-select>
        </el-form-item>
        <el-form-item label="App Key">
          <el-input v-model="form.app_key" placeholder="admin / chat / audit" />
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="form.path" placeholder="/chat" />
        </el-form-item>
        <el-form-item label="组件">
          <el-input v-model="form.component" placeholder="app-chat / UsersPage" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="settings / message" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="权限编码">
          <el-input v-model="form.permission_code" placeholder="admin:users，可为空" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="前端可见">
          <el-switch v-model="form.visible" />
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
import { computed, onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { api, getApiErrorMessage, unwrap } from "@astraflow/shared-api"

type PageResult<T> = { items: T[]; total: number; page: number; page_size: number }
type MenuRow = {
  id: string
  parent_id?: string | null
  code: string
  name: string
  menu_type: string
  app_key?: string | null
  path: string
  component: string
  icon: string
  sort: number
  permission_code?: string | null
  visible: boolean
  status: string
  children?: MenuRow[]
}

const rows = ref<MenuRow[]>([])
const menuTree = ref<MenuRow[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: "" })
const form = reactive({
  id: "",
  parent_id: "",
  code: "",
  name: "",
  menu_type: "system",
  app_key: "",
  path: "",
  component: "",
  icon: "",
  sort: 99,
  permission_code: "",
  visible: true,
  status: "active",
})

const parentOptions = computed(() =>
  flattenMenus(menuTree.value)
    .filter((item) => item.id !== form.id)
    .map((item) => ({ id: item.id, label: `${"　".repeat(item.level)}${item.name}（${item.path || item.code}）` })),
)

function flattenMenus(items: MenuRow[], level = 0): Array<MenuRow & { level: number }> {
  return items.flatMap((item) => [{ ...item, level }, ...flattenMenus(item.children || [], level + 1)])
}

async function load() {
  loading.value = true
  try {
    const data = await unwrap<PageResult<MenuRow>>(api.get("/admin/menus", { params: query }))
    rows.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function loadTree() {
  menuTree.value = await unwrap<MenuRow[]>(api.get("/admin/menus/tree"))
}

function resetForm() {
  Object.assign(form, {
    id: "",
    parent_id: "",
    code: "",
    name: "",
    menu_type: "system",
    app_key: "",
    path: "",
    component: "",
    icon: "",
    sort: 99,
    permission_code: "",
    visible: true,
    status: "active",
  })
}

async function openCreate() {
  resetForm()
  await loadTree()
  dialogVisible.value = true
}

async function openEdit(row: MenuRow) {
  await loadTree()
  Object.assign(form, {
    id: row.id,
    parent_id: row.parent_id || "",
    code: row.code,
    name: row.name,
    menu_type: row.menu_type,
    app_key: row.app_key || "",
    path: row.path,
    component: row.component,
    icon: row.icon,
    sort: row.sort,
    permission_code: row.permission_code || "",
    visible: row.visible,
    status: row.status,
  })
  dialogVisible.value = true
}

function payload() {
  return {
    parent_id: form.parent_id || null,
    code: form.code,
    name: form.name,
    menu_type: form.menu_type,
    app_key: form.app_key || null,
    path: form.path,
    component: form.component,
    icon: form.icon,
    sort: form.sort,
    permission_code: form.permission_code || null,
    visible: form.visible,
    status: form.status,
  }
}

async function save() {
  if (!form.code || !form.name) {
    ElMessage.warning("请填写菜单编码和名称")
    return
  }

  saving.value = true
  try {
    if (form.id) {
      await unwrap(api.put(`/admin/menus/${form.id}`, payload()))
    } else {
      await unwrap(api.post("/admin/menus", payload()))
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

async function remove(row: MenuRow) {
  try {
    await ElMessageBox.confirm(`确认删除菜单「${row.name}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    })
    await unwrap(api.delete(`/admin/menus/${row.id}`))
    ElMessage.success("删除成功")
    await load()
  } catch (error) {
    if (error !== "cancel") ElMessage.error(getApiErrorMessage(error))
  }
}

onMounted(load)
</script>
