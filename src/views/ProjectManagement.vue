<template>
  <div class="project-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>專案管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新增專案
          </el-button>
        </div>
      </template>

      <!-- 專案列表 -->
      <el-table :data="projects" v-loading="loading" stripe>
        <el-table-column prop="name" label="專案名稱" width="200" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="狀態" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="建立時間" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewActivities(row)">管理作業</el-button>
            <el-button size="small" type="primary" @click="editProject(row)">編輯</el-button>
            <el-button size="small" type="danger" @click="deleteProject(row)">刪除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 建立/編輯專案對話框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '編輯專案' : '新增專案'"
      width="500px"
    >
      <el-form :model="projectForm" label-width="100px">
        <el-form-item label="專案名稱" required>
          <el-input v-model="projectForm.name" placeholder="請輸入專案名稱" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="請輸入專案描述"
          />
        </el-form-item>
        <el-form-item label="狀態">
          <el-select v-model="projectForm.status">
            <el-option label="草稿" value="draft" />
            <el-option label="進行中" value="active" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject" :loading="saving">確定</el-button>
      </template>
    </el-dialog>

    <!-- 作業管理對話框 -->
    <el-dialog
      v-model="showActivityDialog"
      title="作業活動管理"
      width="90%"
      :close-on-click-modal="false"
    >
      <ActivityTable
        v-if="currentProject"
        :project-id="currentProject.id"
        @close="showActivityDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { projectAPI } from '../services/api'
import ActivityTable from '../components/ActivityTable.vue'

const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showActivityDialog = ref(false)
const editingProject = ref(null)
const currentProject = ref(null)

const projectForm = ref({
  name: '',
  description: '',
  status: 'draft'
})

// 載入專案列表
const loadProjects = async () => {
  loading.value = true
  try {
    projects.value = await projectAPI.getProjects()
  } catch (error) {
    ElMessage.error('載入專案列表失敗：' + error.message)
  } finally {
    loading.value = false
  }
}

// 儲存專案
const saveProject = async () => {
  if (!projectForm.value.name.trim()) {
    ElMessage.warning('請輸入專案名稱')
    return
  }

  saving.value = true
  try {
    if (editingProject.value) {
      await projectAPI.updateProject(editingProject.value.id, projectForm.value)
      ElMessage.success('專案更新成功')
    } else {
      await projectAPI.createProject(projectForm.value)
      ElMessage.success('專案建立成功')
    }
    showCreateDialog.value = false
    resetForm()
    loadProjects()
  } catch (error) {
    ElMessage.error('儲存失敗：' + error.message)
  } finally {
    saving.value = false
  }
}

// 編輯專案
const editProject = (project) => {
  editingProject.value = project
  projectForm.value = {
    name: project.name,
    description: project.description || '',
    status: project.status
  }
  showCreateDialog.value = true
}

// 刪除專案
const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      `確定要刪除專案「${project.name}」嗎？此操作將刪除所有相關的作業和情境。`,
      '確認刪除',
      {
        type: 'warning'
      }
    )
    await projectAPI.deleteProject(project.id)
    ElMessage.success('專案已刪除')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('刪除失敗：' + error.message)
    }
  }
}

// 查看作業
const viewActivities = (project) => {
  currentProject.value = project
  showActivityDialog.value = true
}

// 重置表單
const resetForm = () => {
  editingProject.value = null
  projectForm.value = {
    name: '',
    description: '',
    status: 'draft'
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW')
}

// 取得狀態類型
const getStatusType = (status) => {
  const types = {
    draft: 'info',
    active: 'success',
    completed: ''
  }
  return types[status] || ''
}

// 監聽對話框關閉
const handleDialogClose = () => {
  resetForm()
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-management {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

