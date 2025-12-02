<template>
  <div class="project-management">
    <!-- 麵包屑導航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item>首頁</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <template #header>
        <div class="card-header">
          <h2 class="page-title">專案管理</h2>
          <el-button type="primary" @click="showCreateDialog = true" class="add-project-btn">
            <el-icon><Plus /></el-icon>
            新增專案
          </el-button>
        </div>
      </template>

      <!-- 專案列表 -->
      <template v-if="!isMobile">
        <el-table 
          :data="projects" 
          v-loading="loading" 
          stripe
          :empty-text="emptyText"
          class="project-table"
        >
          <el-table-column prop="name" label="專案名稱" width="220" />
          <el-table-column prop="description" label="描述" min-width="120" show-overflow-tooltip />
          <el-table-column prop="status" label="狀態" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.status)" 
                :class="`status-tag status-${row.status}`"
                effect="plain"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="建立時間" width="200">
            <template #default="{ row }">
              <span style="white-space: nowrap;">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  @click="viewActivities(row)" 
                  class="action-btn manage-btn"
                  plain
                >
                  管理作業
                </el-button>
                <el-button size="small" type="primary" @click="editProject(row)" :icon="Edit" text class="action-btn icon-btn" />
                <el-button size="small" type="danger" @click="deleteProject(row)" :icon="Delete" text class="action-btn icon-btn" />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <div class="project-card-list">
          <template v-if="projects.length">
            <div 
              v-for="project in projects" 
              :key="project.id" 
              class="project-card"
            >
              <div class="project-card-header">
                <div>
                  <div class="card-title">{{ project.name }}</div>
                  <div class="card-subtitle">{{ formatDate(project.created_at) }}</div>
                </div>
                <el-tag 
                  :type="getStatusType(project.status)" 
                  :class="`status-tag status-${project.status}`"
                  effect="plain"
                >
                  {{ getStatusText(project.status) }}
                </el-tag>
              </div>
              <div class="project-card-body">
                <div class="card-field">
                  <span class="field-label">描述</span>
                  <span class="field-value">{{ project.description || '—' }}</span>
                </div>
              </div>
              <div class="project-card-actions">
                <el-button 
                  size="small" 
                  @click="viewActivities(project)" 
                  class="action-btn manage-btn"
                  plain
                >
                  管理作業
                </el-button>
                <div class="icon-action-group">
                  <el-button size="small" type="primary" @click="editProject(project)" :icon="Edit" text class="action-btn icon-btn" />
                  <el-button size="small" type="danger" @click="deleteProject(project)" :icon="Delete" text class="action-btn icon-btn" />
                </div>
              </div>
            </div>
          </template>
          <el-empty v-else :description="emptyText" />
        </div>
      </template>
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
      :width="isMobile ? '95%' : '90%'"
      :close-on-click-modal="false"
      class="activity-dialog-responsive"
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { projectAPI } from '../services/api'
import ActivityTable from '../components/ActivityTable.vue'

const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showActivityDialog = ref(false)
const editingProject = ref(null)
const currentProject = ref(null)
const isMobile = ref(false)

const emptyText = '暫無專案資料，請點擊「新增專案」建立第一個專案'

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

// 格式化日期（單行顯示）
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
}

// 取得狀態類型
const getStatusType = (status) => {
  const types = {
    draft: 'info',
    active: 'success',
    completed: 'success'
  }
  return types[status] || 'info'
}

// 取得狀態文字（繁體中文）
const getStatusText = (status) => {
  if (!status) return '草稿'
  const statusLower = String(status).toLowerCase()
  const texts = {
    draft: '草稿',
    active: '進行中',
    completed: '已完成',
    complete: '已完成',
    '進行中': '進行中',
    '已完成': '已完成',
    '草稿': '草稿'
  }
  return texts[statusLower] || texts[status] || status
}

// 監聽對話框關閉
const handleDialogClose = () => {
  resetForm()
}

const updateIsMobile = () => {
  if (typeof window === 'undefined') return
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  updateIsMobile()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateIsMobile)
  }
  loadProjects()
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateIsMobile)
  }
})
</script>

<style scoped>
.project-management {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: var(--spacing-3xl);
  background-color: var(--content-bg);
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: 0;
  line-height: 1.4;
  margin: 0;
}

/* 統一卡片樣式 */
.project-management :deep(.el-card) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.project-management :deep(.el-card__header) {
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.project-management :deep(.el-card__body) {
  padding: var(--spacing-3xl);
}

/* 統一表格樣式 */
.project-management :deep(.project-table) {
  background-color: var(--card-bg);
  border-radius: 0;
  border: none;
  overflow: hidden;
}

.project-management :deep(.project-table .el-table__header-wrapper) {
  background-color: #F9FAFB;
}

.project-management :deep(.project-table th) {
  background-color: #F9FAFB;
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
  border-bottom: 2px solid var(--border-color);
  padding: var(--spacing-lg) var(--spacing-md);
  letter-spacing: 0;
}

.project-management :deep(.project-table td) {
  color: var(--text-primary);
  font-size: var(--font-size-md);
  border-bottom: 1px solid var(--border-light);
  padding: var(--spacing-lg) var(--spacing-md);
  line-height: 1.6;
  background-color: var(--card-bg);
}

.project-management :deep(.el-table td .el-tag) {
  white-space: normal;
}

.project-management :deep(.project-table .el-table__row:hover) {
  background-color: var(--sidebar-hover) !important;
  transition: background-color 0.2s ease;
}

.project-management :deep(.project-table .el-table__empty-block) {
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 無印風格標籤 */
.project-management :deep(.el-tag) {
  border-radius: 0;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  color: var(--text-primary);
  font-weight: 400;
  font-size: 13px;
  padding: 6px 12px;
  letter-spacing: 0.02em;
  line-height: 1.4;
}

/* 統一狀態標籤樣式 - 無印風格配色 */
.project-management :deep(.status-tag.status-draft),
.project-management :deep(.status-tag[class*="draft"]) {
  border-color: var(--text-light) !important;
  background-color: #F5F5F5 !important;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-sm) !important;
  padding: 4px 12px !important;
}

/* 進行中 - 使用無印紅色系（原已完成顏色） */
.project-management :deep(.status-tag.status-active),
.project-management :deep(.status-tag[class*="active"]) {
  border-color: #C85A4F !important;
  background-color: #F5E8E6 !important;
  color: #8B3A2F !important;
  border-radius: var(--radius-sm) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-sm) !important;
  padding: 4px 12px !important;
}

/* 已完成 - 使用柔和綠色系（原進行中顏色） */
.project-management :deep(.status-tag.status-completed),
.project-management :deep(.status-tag[class*="completed"]) {
  border-color: #7A9B7A !important;
  background-color: #E8F0E8 !important;
  color: #4A6B4A !important;
  border-radius: var(--radius-sm) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-sm) !important;
  padding: 4px 12px !important;
}

.project-management :deep(.el-tag--info) {
  border-color: var(--text-secondary);
  background-color: var(--content-bg);
  color: var(--text-primary);
}

.project-management :deep(.el-tag--success) {
  border-color: var(--success);
  background-color: var(--content-bg);
  color: var(--text-primary);
}

/* 按鈕樣式 */
.project-management :deep(.el-button) {
  border-radius: 0;
  font-weight: var(--font-weight-normal);
  transition: all 0.25s ease;
}

.project-management :deep(.el-button--small) {
  padding: 8px 16px;
  font-size: var(--font-size-md);
  letter-spacing: 0;
  transition: all 0.2s ease;
  white-space: nowrap;
  height: 32px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-wrap: nowrap;
}

/* 編輯和刪除按鈕之間更緊密 */
.action-buttons .icon-btn {
  margin-left: 0;
  margin-right: 0;
}

.action-btn {
  flex-shrink: 0;
}

.project-card-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-card {
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px;
  background-color: var(--card-bg);
  box-shadow: var(--shadow);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.project-card .card-title {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.project-card .card-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.project-card-body {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.project-card .card-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-card .field-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.project-card .field-value {
  font-size: 15px;
  color: var(--text-primary);
}

.project-card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.icon-action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 管理作業按鈕 - 統一為無底色樣式 */
.manage-btn {
  min-width: 90px;
  background-color: transparent !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-primary) !important;
}

.manage-btn:hover {
  background-color: var(--content-bg) !important;
  border-color: var(--primary) !important;
  color: var(--primary) !important;
}

/* 編輯和刪除按鈕 - 無底色、無邊框、灰色圖示 */
.icon-btn {
  padding: 6px !important;
  min-width: 32px;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: transparent !important;
  border: 1px solid transparent !important;
}

/* 編輯按鈕 - 透明背景、透明邊框、灰色圖示 */
.project-management :deep(.el-button--primary.is-text.icon-btn) {
  background-color: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-secondary) !important;
}

.project-management :deep(.el-button--primary.is-text.icon-btn:hover) {
  background-color: var(--sidebar-hover) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

/* 刪除按鈕 - 透明背景、透明邊框、灰色圖示 */
.project-management :deep(.el-button--danger.is-text.icon-btn) {
  background-color: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-secondary) !important;
}

.project-management :deep(.el-button--danger.is-text.icon-btn:hover) {
  background-color: var(--sidebar-hover) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.icon-btn :deep(.el-icon) {
  font-size: 16px;
  width: 16px;
  height: 16px;
}

.icon-btn :deep(svg) {
  width: 16px;
  height: 16px;
}

/* 編輯按鈕圖示顏色 - 灰色 */
.project-management :deep(.el-button--primary.is-text.icon-btn .el-icon),
.project-management :deep(.el-button--primary.is-text.icon-btn svg) {
  color: var(--text-secondary) !important;
  fill: var(--text-secondary) !important;
}

.project-management :deep(.el-button--primary.is-text.icon-btn:hover .el-icon),
.project-management :deep(.el-button--primary.is-text.icon-btn:hover svg) {
  color: var(--text-primary) !important;
  fill: var(--text-primary) !important;
}

/* 刪除按鈕圖示顏色 - 灰色 */
.project-management :deep(.el-button--danger.is-text.icon-btn .el-icon),
.project-management :deep(.el-button--danger.is-text.icon-btn svg) {
  color: var(--text-secondary) !important;
  fill: var(--text-secondary) !important;
}

.project-management :deep(.el-button--danger.is-text.icon-btn:hover .el-icon),
.project-management :deep(.el-button--danger.is-text.icon-btn:hover svg) {
  color: var(--text-primary) !important;
  fill: var(--text-primary) !important;
}

.project-management :deep(.el-button--primary) {
  background-color: transparent;
  border-color: var(--primary);
  color: var(--primary);
}

.project-management :deep(.el-button--primary:hover) {
  background-color: var(--content-bg);
  border-color: var(--primary-hover);
  color: var(--primary-hover);
}

.project-management :deep(.el-button--primary.is-text) {
  background-color: transparent;
  border: none;
  color: var(--primary);
  padding: 6px;
}

.project-management :deep(.el-button--primary.is-text:hover) {
  background-color: var(--content-bg);
  border: none;
  color: var(--primary-hover);
}

.project-management :deep(.el-button--danger) {
  background-color: transparent;
  border-color: var(--danger);
  color: var(--danger);
}

.project-management :deep(.el-button--danger:hover) {
  background-color: var(--content-bg);
  border-color: var(--primary-hover);
  color: var(--primary-hover);
}

.project-management :deep(.el-button--danger.is-text) {
  background-color: transparent;
  border: none;
  color: var(--danger);
  padding: 6px;
}

.project-management :deep(.el-button--danger.is-text:hover) {
  background-color: var(--content-bg);
  border: none;
  color: var(--primary-hover);
}

/* 新增專案按鈕 - 保持有背景色（主要操作） */
.add-project-btn {
  background-color: var(--primary);
  border-color: var(--primary);
  color: var(--text-white);
  padding: 10px 24px;
  font-size: 14px;
  letter-spacing: 0.02em;
  transition: all 0.25s ease;
  height: 40px;
}

.add-project-btn:hover {
  background-color: var(--primary-hover);
  border-color: var(--primary-hover);
  color: var(--text-white);
}

.add-project-btn :deep(.el-icon) {
  margin-right: 6px;
}

@media (max-width: 768px) {
  .project-management {
    padding: 12px;
  }

  .project-management :deep(.el-card__header),
  .project-management :deep(.el-card__body) {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .add-project-btn {
    width: 100%;
    justify-content: center;
  }

  .project-management :deep(.project-table) {
    overflow-x: auto;
  }

  .project-card {
    padding: 12px;
    margin-bottom: 12px;
  }

  .project-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .project-card .card-title {
    font-size: 16px;
    width: 100%;
  }

  .project-card-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    width: 100%;
  }

  .manage-btn {
    width: 100%;
  }

  .icon-action-group {
    display: flex;
    gap: 8px;
    width: 100%;
    justify-content: flex-end;
  }

  .project-management :deep(.el-dialog) {
    width: 95% !important;
    max-width: 100% !important;
    margin: 0 auto !important;
  }

  .project-management :deep(.el-dialog__body) {
    padding: 12px;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }

  .project-management :deep(.el-dialog__header) {
    padding: 12px;
  }

  .project-management :deep(.el-dialog__footer) {
    padding: 12px;
  }
}
</style>

