<template>
  <div class="activity-table">
    <!-- 表格容器 -->
    <div class="table-container">
      <!-- 表格標題和新增按鈕 -->
      <div class="table-header-bar">
        <h2 class="table-title-text">作業活動管理</h2>
        <button 
          @click="addNewRow" 
          class="add-activity-btn-header"
          :disabled="isAddingNew"
        >
          <el-icon class="add-icon"><Plus /></el-icon>
          <span class="add-text">新增作業</span>
        </button>
      </div>
      
      <div v-if="!isMobile">
        <el-table 
          :data="displayActivities" 
          v-loading="loading" 
          stripe 
          border
          class="activity-data-table"
          :empty-text="emptyText"
          style="width: 100%;"
        >
      <el-table-column prop="name" :label="''" min-width="200" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">作業名稱</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-input
            v-if="row.isEditing"
            v-model="row.name"
            placeholder="請輸入作業名稱"
            class="inline-input"
            size="small"
            ref="nameInputRef"
            @keyup.enter="handleEnterKey(row)"
          />
          <span v-else class="cell-text">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="normal_duration" :label="''" min-width="140" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">正常工期</span>
            <span class="sub-text">（天）</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-input-number
            v-if="row.isEditing"
            v-model="row.normal_duration"
            :min="1"
            :precision="0"
            class="inline-input-number"
            size="small"
            :controls="false"
            @keyup.enter="handleEnterKey(row)"
          />
          <span v-else class="cell-text">{{ row.normal_duration }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="crash_duration" :label="''" min-width="140" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">趕工工期</span>
            <span class="sub-text">（天）</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-input-number
            v-if="row.isEditing"
            v-model="row.crash_duration"
            :min="1"
            :precision="0"
            class="inline-input-number"
            size="small"
            :controls="false"
            @keyup.enter="handleEnterKey(row)"
          />
          <span v-else class="cell-text">{{ row.crash_duration }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="normal_cost" :label="''" min-width="160" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">正常成本</span>
            <span class="sub-text">（NT$）</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-input-number
            v-if="row.isEditing"
            v-model="row.normal_cost"
            :min="0"
            :precision="0"
            class="inline-input-number"
            size="small"
            :controls="false"
            @keyup.enter="handleEnterKey(row)"
          />
          <span v-else class="cell-text">{{ formatCurrency(row.normal_cost) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="crash_cost" :label="''" min-width="160" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">趕工成本</span>
            <span class="sub-text">（NT$）</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-input-number
            v-if="row.isEditing"
            v-model="row.crash_cost"
            :min="0"
            :precision="0"
            class="inline-input-number"
            size="small"
            :controls="false"
            @keyup.enter="handleEnterKey(row)"
          />
          <span v-else class="cell-text">{{ formatCurrency(row.crash_cost) }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="''" min-width="160" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">前置作業</span>
            <span class="sub-text">（可多選）</span>
          </div>
        </template>
        <template #default="{ row }">
          <el-select
            v-if="row.isEditing"
            v-model="row.predecessor_ids"
            multiple
            placeholder="請選擇"
            class="inline-select"
            size="small"
            :disabled="row.isNew && row.id"
          >
            <el-option
              v-for="act in availablePredecessorsForEdit(row)"
              :key="act.id"
              :label="act.name"
              :value="act.id"
            />
          </el-select>
          <div v-else class="predecessor-tags">
            <template v-if="getPredecessors(row.id) && getPredecessors(row.id).length > 0">
              <el-tag
                v-for="pred in getPredecessors(row.id)"
                :key="pred.id"
                size="small"
                class="predecessor-tag"
              >
                {{ pred.name }}
              </el-tag>
            </template>
            <span v-else class="empty-text">無</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="''" min-width="140" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">後續作業</span>
            <span class="sub-text">（系統顯示）</span>
          </div>
        </template>
        <template #default="{ row }">
          <span class="cell-text empty-text">無</span>
        </template>
      </el-table-column>
      <el-table-column :label="''" min-width="120" align="center">
        <template #header>
          <div class="header-label">
            <span class="main-text">操作</span>
          </div>
        </template>
        <template #default="{ row }">
          <div class="action-buttons-inline">
            <template v-if="row.isEditing">
              <el-button 
                size="small" 
                type="primary" 
                @click="saveInlineActivity(row)" 
                :icon="Check" 
                text 
                class="action-btn icon-btn save-btn"
                :loading="saving && row === editingRow"
              />
              <el-button 
                size="small" 
                @click="cancelInlineEdit(row)" 
                :icon="Close" 
                text 
                class="action-btn icon-btn cancel-btn"
                :disabled="saving"
              />
            </template>
            <template v-else>
              <el-button 
                size="small" 
                type="primary" 
                @click="editActivity(row)" 
                :icon="Edit" 
                text 
                class="action-btn icon-btn"
              />
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteActivity(row)" 
                :icon="Delete" 
                text 
                class="action-btn icon-btn"
              />
            </template>
          </div>
        </template>
      </el-table-column>
      </el-table>
      </div>

      <div v-else class="mobile-activity-list">
        <template v-if="displayActivities.length">
          <div
            v-for="(row, index) in displayActivities"
            :key="row.id || index"
            class="activity-card"
          >
            <div class="card-header">
              <div class="card-title">
                <el-input
                  v-if="row.isEditing"
                  v-model="row.name"
                  placeholder="請輸入作業名稱"
                  class="inline-input"
                  size="small"
                  @keyup.enter="handleEnterKey(row)"
                />
                <span v-else>{{ row.name || '未命名作業' }}</span>
              </div>
              <div class="card-actions-inline">
                <template v-if="row.isEditing">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="saveInlineActivity(row)" 
                    :icon="Check" 
                    text 
                    class="action-btn icon-btn save-btn"
                    :loading="saving && row === editingRow"
                  />
                  <el-button 
                    size="small" 
                    @click="cancelInlineEdit(row)" 
                    :icon="Close" 
                    text 
                    class="action-btn icon-btn cancel-btn"
                    :disabled="saving"
                  />
                </template>
                <template v-else>
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="editActivity(row)" 
                    :icon="Edit" 
                    text 
                    class="action-btn icon-btn"
                  />
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="deleteActivity(row)" 
                    :icon="Delete" 
                    text 
                    class="action-btn icon-btn"
                  />
                </template>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">正常工期（天）</span>
              <div class="field-value">
                <el-input-number
                  v-if="row.isEditing"
                  v-model="row.normal_duration"
                  :min="1"
                  :precision="0"
                  class="inline-input-number"
                  size="small"
                  :controls="false"
                />
                <span v-else>{{ row.normal_duration ?? '—' }}</span>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">趕工工期（天）</span>
              <div class="field-value">
                <el-input-number
                  v-if="row.isEditing"
                  v-model="row.crash_duration"
                  :min="1"
                  :precision="0"
                  class="inline-input-number"
                  size="small"
                  :controls="false"
                />
                <span v-else>{{ row.crash_duration ?? '—' }}</span>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">正常成本（NT$）</span>
              <div class="field-value">
                <el-input-number
                  v-if="row.isEditing"
                  v-model="row.normal_cost"
                  :min="0"
                  :precision="0"
                  class="inline-input-number"
                  size="small"
                  :controls="false"
                />
                <span v-else>{{ row.normal_cost != null ? formatCurrency(row.normal_cost) : '—' }}</span>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">趕工成本（NT$）</span>
              <div class="field-value">
                <el-input-number
                  v-if="row.isEditing"
                  v-model="row.crash_cost"
                  :min="0"
                  :precision="0"
                  class="inline-input-number"
                  size="small"
                  :controls="false"
                />
                <span v-else>{{ row.crash_cost != null ? formatCurrency(row.crash_cost) : '—' }}</span>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">前置作業</span>
              <div class="field-value">
                <el-select
                  v-if="row.isEditing"
                  v-model="row.predecessor_ids"
                  multiple
                  placeholder="請選擇"
                  class="inline-select"
                  size="small"
                >
                  <el-option
                    v-for="act in availablePredecessorsForEdit(row)"
                    :key="act.id"
                    :label="act.name"
                    :value="act.id"
                  />
                </el-select>
                <div v-else class="predecessor-tags">
                  <template v-if="getPredecessors(row.id) && getPredecessors(row.id).length > 0">
                    <el-tag
                      v-for="pred in getPredecessors(row.id)"
                      :key="pred.id"
                      size="small"
                      class="predecessor-tag"
                    >
                      {{ pred.name }}
                    </el-tag>
                  </template>
                  <span v-else class="empty-text">無</span>
                </div>
              </div>
            </div>

            <div class="card-field">
              <span class="field-label">後續作業</span>
              <div class="field-value">
                <span class="empty-text">無</span>
              </div>
            </div>
          </div>
        </template>
        <el-empty v-else description="暫無作業資料" />
      </div>
    </div>

    <!-- 建立/編輯作業對話框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingActivity ? '編輯作業' : '新增作業'"
      width="680px"
      class="activity-dialog"
      @close="handleDialogClose"
    >
      <el-form 
        :model="activityForm" 
        :rules="rules" 
        ref="formRef"
        label-width="140px"
        class="activity-form"
      >
        <div class="form-section">
          <div class="section-title">基本資訊</div>
          <el-form-item label="作業名稱" prop="name">
            <el-input 
              v-model="activityForm.name" 
              placeholder="請輸入作業名稱"
              class="form-input"
            />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="activityForm.description"
              type="textarea"
              :rows="3"
              placeholder="請輸入作業描述（選填）"
              class="form-textarea"
            />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">正常作業</div>
          <el-form-item label="正常工期（天）" prop="normal_duration">
            <el-input-number
              v-model="activityForm.normal_duration"
              :min="1"
              :precision="0"
              class="form-input-number"
              placeholder="請輸入正常工期"
            />
          </el-form-item>
          <el-form-item label="正常成本" prop="normal_cost">
            <el-input-number
              v-model="activityForm.normal_cost"
              :min="0"
              :precision="2"
              class="form-input-number"
              placeholder="請輸入正常成本"
            />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">趕工作業</div>
          <el-form-item label="趕工工期（天）" prop="crash_duration">
            <el-input-number
              v-model="activityForm.crash_duration"
              :min="1"
              :precision="0"
              class="form-input-number"
              placeholder="請輸入趕工工期"
            />
          </el-form-item>
          <el-form-item label="趕工成本" prop="crash_cost">
            <el-input-number
              v-model="activityForm.crash_cost"
              :min="0"
              :precision="2"
              class="form-input-number"
              placeholder="請輸入趕工成本"
            />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">作業關係</div>
          <el-form-item label="前置作業">
            <el-select
              v-model="activityForm.predecessor_ids"
              multiple
              placeholder="請選擇前置作業（選填）"
              class="form-select"
              :disabled="editingActivity && editingActivity.id"
            >
              <el-option
                v-for="act in availablePredecessors"
                :key="act.id"
                :label="act.name"
                :value="act.id"
              />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="saveActivity" :loading="saving" class="submit-btn">
            確定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Close } from '@element-plus/icons-vue'
import { activityAPI } from '../services/api'

const props = defineProps({
  projectId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

const activities = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const isMobile = ref(false)
const editingActivity = ref(null)
const formRef = ref(null)
const isAddingNew = ref(false)
const editingRow = ref(null)
const nameInputRef = ref(null)

// 計算顯示的活動列表（包含編輯中的行）
const displayActivities = computed(() => {
  return activities.value
})

const activityForm = ref({
  name: '',
  description: '',
  normal_duration: null,
  normal_cost: null,
  crash_duration: null,
  crash_cost: null,
  predecessor_ids: []
})

const rules = {
  name: [{ required: true, message: '請輸入作業名稱', trigger: 'blur' }],
  normal_duration: [{ required: true, message: '請輸入正常工期', trigger: 'blur' }],
  normal_cost: [{ required: true, message: '請輸入正常成本', trigger: 'blur' }],
  crash_duration: [{ required: true, message: '請輸入趕工工期', trigger: 'blur' }],
  crash_cost: [{ required: true, message: '請輸入趕工成本', trigger: 'blur' }]
}

// 可用的前置作業（排除自己）
const availablePredecessors = computed(() => {
  return activities.value.filter(act => act.id && !act.isEditing)
})

// 載入作業列表
const loadActivities = async () => {
  loading.value = true
  try {
    const data = await activityAPI.getActivities(props.projectId)
    activities.value = data.map(act => ({
      ...act,
      isEditing: false,
      isNew: false,
      predecessor_ids: []
    }))
    isAddingNew.value = false
    // 載入每個作業的前置作業
    for (const activity of activities.value) {
      try {
        const predecessors = await activityAPI.getPredecessors(activity.id)
        activity.predecessors = predecessors
      } catch (error) {
        activity.predecessors = []
      }
    }
  } catch (error) {
    ElMessage.error('載入作業列表失敗：' + error.message)
  } finally {
    loading.value = false
  }
}

// 取得作業的前置作業
const getPredecessors = (activityId) => {
  const activity = activities.value.find(a => a.id === activityId)
  return activity?.predecessors || []
}

// 儲存作業
const saveActivity = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 驗證趕工工期 <= 正常工期
    if (activityForm.value.crash_duration > activityForm.value.normal_duration) {
      ElMessage.warning('趕工工期必須小於等於正常工期')
      return
    }

    // 驗證趕工成本 >= 正常成本
    if (activityForm.value.crash_cost < activityForm.value.normal_cost) {
      ElMessage.warning('趕工成本必須大於等於正常成本')
      return
    }

    saving.value = true
    try {
      if (editingActivity.value) {
        await activityAPI.updateActivity(editingActivity.value.id, activityForm.value)
        ElMessage.success('作業更新成功')
      } else {
        await activityAPI.createActivity(props.projectId, activityForm.value)
        ElMessage.success('作業建立成功')
      }
      showCreateDialog.value = false
      resetForm()
      loadActivities()
    } catch (error) {
      ElMessage.error('儲存失敗：' + error.message)
    } finally {
      saving.value = false
    }
  })
}

// 新增一行
const addNewRow = () => {
  if (isAddingNew.value) return
  
  isAddingNew.value = true
  const newActivity = {
    id: null,
    name: '',
    description: '',
    normal_duration: null,
    normal_cost: null,
    crash_duration: null,
    crash_cost: null,
    predecessor_ids: [],
    isEditing: true,
    isNew: true,
    _originalData: null
  }
  activities.value.push(newActivity)
  
  // 自動聚焦到作業名稱輸入框
  setTimeout(() => {
    const inputs = document.querySelectorAll('.inline-input input')
    if (inputs.length > 0) {
      const lastInput = inputs[inputs.length - 1]
      lastInput?.focus()
    }
  }, 100)
}

// 處理 Enter 鍵
const handleEnterKey = (row) => {
  if (row.isEditing && row.name && row.name.trim()) {
    saveInlineActivity(row)
  }
}

// 保存內聯編輯
const saveInlineActivity = async (row) => {
  if (!row.name || !row.name.trim()) {
    ElMessage.warning('請輸入作業名稱')
    return
  }

  if (row.crash_duration > row.normal_duration) {
    ElMessage.warning('趕工工期必須小於等於正常工期')
    return
  }

  if (row.crash_cost < row.normal_cost) {
    ElMessage.warning('趕工成本必須大於等於正常成本')
    return
  }

  saving.value = true
  editingRow.value = row
  try {
    const activityData = {
      name: row.name.trim(),
      description: row.description || '',
      normal_duration: row.normal_duration,
      normal_cost: row.normal_cost,
      crash_duration: row.crash_duration,
      crash_cost: row.crash_cost,
      predecessor_ids: row.predecessor_ids || []
    }

    if (row.isNew) {
      // 新增
      const created = await activityAPI.createActivity(props.projectId, activityData)
      // 更新列表中的項目
      const index = activities.value.findIndex(a => a === row)
      if (index !== -1) {
        activities.value[index] = {
          ...created,
          isEditing: false,
          isNew: false
        }
      }
      ElMessage.success('作業建立成功')
      isAddingNew.value = false
    } else {
      // 更新
      await activityAPI.updateActivity(row.id, activityData)
      // 更新前置作業
      if (row.predecessor_ids && row.predecessor_ids.length > 0) {
        // 先刪除舊的前置作業關係
        const oldPredecessors = await activityAPI.getPredecessors(row.id)
        for (const pred of oldPredecessors) {
          // 這裡需要一個刪除前置作業的 API，暫時跳過
        }
        // 添加新的前置作業關係
        // 這裡需要一個添加前置作業的 API，暫時跳過
      }
      row.isEditing = false
      row.isNew = false
      ElMessage.success('作業更新成功')
    }
    loadActivities()
  } catch (error) {
    ElMessage.error('儲存失敗：' + error.message)
  } finally {
    saving.value = false
    editingRow.value = null
  }
}

// 取消內聯編輯
const cancelInlineEdit = (row) => {
  if (row.isNew) {
    // 如果是新行，直接移除
    const index = activities.value.findIndex(a => a === row)
    if (index !== -1) {
      activities.value.splice(index, 1)
    }
    isAddingNew.value = false
  } else {
    // 恢復原始數據
    if (row._originalData) {
      Object.assign(row, row._originalData)
      row.isEditing = false
    } else {
      loadActivities()
    }
  }
}

// 編輯作業
const editActivity = async (activity) => {
  // 保存原始數據
  activity._originalData = { ...activity }
  // 載入前置作業
  try {
    const predecessors = await activityAPI.getPredecessors(activity.id)
    activity.predecessor_ids = predecessors.map(p => p.id)
  } catch (error) {
    activity.predecessor_ids = []
  }
  activity.isEditing = true
  activity.isNew = false
}

// 獲取可用於編輯的前置作業列表
const availablePredecessorsForEdit = (currentRow) => {
  if (currentRow.isNew) {
    return availablePredecessors.value
  }
  // 編輯時，排除自己
  return availablePredecessors.value.filter(a => a.id !== currentRow.id)
}

// 刪除作業
const deleteActivity = async (activity) => {
  try {
    await ElMessageBox.confirm(
      `確定要刪除作業「${activity.name}」嗎？`,
      '確認刪除',
      { type: 'warning' }
    )
    await activityAPI.deleteActivity(activity.id)
    ElMessage.success('作業已刪除')
    loadActivities()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('刪除失敗：' + error.message)
    }
  }
}

// 重置表單
const resetForm = () => {
  editingActivity.value = null
  activityForm.value = {
    name: '',
    description: '',
    normal_duration: null,
    normal_cost: null,
    crash_duration: null,
    crash_cost: null,
    predecessor_ids: []
  }
  formRef.value?.resetFields()
}

// 格式化貨幣
const formatCurrency = (value) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(value)
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
  loadActivities()
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateIsMobile)
  }
})

watch(
  () => props.projectId,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      resetForm()
      loadActivities()
    }
  }
)
</script>

<style scoped>
.activity-table {
  padding: 24px 32px;
  max-width: 100%;
  background-color: var(--content-bg);
  min-height: calc(100vh - 64px);
}

/* 表格容器 */
.table-container {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
}

/* 表格標題欄 */
.table-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  background-color: #F9FAFB;
  border-bottom: 1px solid var(--border-color);
}

.table-title-text {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: 0;
  line-height: 1.4;
  margin: 0;
}

/* 新增作業按鈕（標題欄） */
.add-activity-btn-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 20px;
  background-color: #3B82F6;
  border: none;
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 6px;
  font-family: inherit;
  box-shadow: 0 1px 2px rgba(59, 130, 246, 0.2);
}

.add-activity-btn-header:hover {
  background-color: #2563EB;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

.add-activity-btn-header:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.add-activity-btn-header:disabled:hover {
  background-color: #3B82F6;
  box-shadow: 0 1px 2px rgba(59, 130, 246, 0.2);
}

.add-icon {
  font-size: 16px;
  transition: all 0.25s ease;
}

.add-text {
  font-size: 14px;
  letter-spacing: 0.01em;
}

.add-activity-btn:hover .add-icon {
  color: var(--text-white);
}

.add-activity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-activity-btn:disabled:hover {
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--text-primary);
}

/* 內聯輸入框樣式 - 現代專業風格 */
.activity-table :deep(.inline-input),
.activity-table :deep(.inline-input-number),
.activity-table :deep(.inline-select) {
  width: 100%;
  display: block;
}

.activity-table :deep(.inline-input .el-input),
.activity-table :deep(.inline-select .el-select),
.activity-table :deep(.inline-input-number.el-input-number) {
  width: 100% !important;
}

.activity-table :deep(.inline-input .el-input__wrapper),
.activity-table :deep(.inline-input-number .el-input__wrapper),
.activity-table :deep(.inline-select .el-input__wrapper) {
  border-radius: 0;
  border: none;
  border-bottom: 1px solid #D1D5DB;
  box-shadow: none;
  background-color: #FFFFFF;
  transition: all 0.2s ease;
  padding: 0 20px;
}

.activity-table :deep(.inline-input .el-input__wrapper:hover),
.activity-table :deep(.inline-input-number .el-input__wrapper:hover),
.activity-table :deep(.inline-select .el-input__wrapper:hover) {
  border-color: #3B82F6;
  background-color: #FFFFFF;
}

.activity-table :deep(.inline-input .el-input__wrapper.is-focus),
.activity-table :deep(.inline-input-number .el-input__wrapper.is-focus),
.activity-table :deep(.inline-select .el-input__wrapper.is-focus) {
  border-color: #3B82F6;
  box-shadow: 0 1px 0 rgba(59, 130, 246, 0.3);
  background-color: #FFFFFF;
}

.activity-table :deep(.inline-input-number .el-input__inner) {
  text-align: inherit;
  min-height: 40px;
  line-height: 40px;
  font-size: 18px;
  border: none;
}

.activity-table :deep(.inline-input .el-input__inner),
.activity-table :deep(.inline-select .el-input__inner) {
  min-height: 40px;
  line-height: 40px;
  font-size: 18px;
  border: none;
}

.activity-table :deep(.el-input-number__decrease),
.activity-table :deep(.el-input-number__increase) {
  width: 32px;
  font-size: 16px;
}

.activity-table :deep(.inline-input-number .el-input__wrapper),
.activity-table :deep(.inline-input .el-input__wrapper),
.activity-table :deep(.inline-select .el-input__wrapper) {
  min-height: 52px;
  padding: 0 20px;
  width: 100%;
}

.activity-table :deep(.inline-input .el-input__inner::placeholder),
.activity-table :deep(.inline-select .el-input__inner::placeholder) {
  font-size: 18px;
}

.action-buttons-inline {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  justify-content: center;
  flex-wrap: nowrap;
}

/* 操作按鈕樣式 - 參照專案管理 */
.activity-table :deep(.action-buttons-inline .icon-btn) {
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
.activity-table :deep(.el-button--primary.is-text.icon-btn) {
  background-color: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-secondary) !important;
}

.activity-table :deep(.el-button--primary.is-text.icon-btn:hover) {
  background-color: var(--sidebar-hover) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

/* 刪除按鈕 - 透明背景、透明邊框、灰色圖示 */
.activity-table :deep(.el-button--danger.is-text.icon-btn) {
  background-color: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-secondary) !important;
}

.activity-table :deep(.el-button--danger.is-text.icon-btn:hover) {
  background-color: var(--sidebar-hover) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

/* 編輯按鈕圖示顏色 - 灰色 */
.activity-table :deep(.el-button--primary.is-text.icon-btn .el-icon),
.activity-table :deep(.el-button--primary.is-text.icon-btn svg) {
  color: var(--text-secondary) !important;
  fill: var(--text-secondary) !important;
}

.activity-table :deep(.el-button--primary.is-text.icon-btn:hover .el-icon),
.activity-table :deep(.el-button--primary.is-text.icon-btn:hover svg) {
  color: var(--text-primary) !important;
  fill: var(--text-primary) !important;
}

/* 刪除按鈕圖示顏色 - 灰色 */
.activity-table :deep(.el-button--danger.is-text.icon-btn .el-icon),
.activity-table :deep(.el-button--danger.is-text.icon-btn svg) {
  color: var(--text-secondary) !important;
  fill: var(--text-secondary) !important;
}

.activity-table :deep(.el-button--danger.is-text.icon-btn:hover .el-icon),
.activity-table :deep(.el-button--danger.is-text.icon-btn:hover svg) {
  color: var(--text-primary) !important;
  fill: var(--text-primary) !important;
}

.save-btn :deep(.el-icon),
.cancel-btn :deep(.el-icon) {
  font-size: 16px;
}

.save-btn :deep(svg),
.cancel-btn :deep(svg) {
  width: 16px;
  height: 16px;
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

/* 統一表格樣式 - 參照專案管理表格 */
.activity-table :deep(.activity-data-table) {
  background-color: var(--card-bg);
  border-radius: 0;
  border: none;
  overflow: hidden;
  width: 100%;
}

.activity-table :deep(.activity-data-table .el-table__header-wrapper) {
  background-color: #F9FAFB;
}

.activity-table :deep(.activity-data-table th) {
  background-color: #F9FAFB;
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
  border-bottom: 2px solid var(--border-color);
  padding: 18px 16px;
  letter-spacing: 0;
  text-align: center;
  white-space: nowrap;
}

.activity-table :deep(.activity-data-table th:first-child) {
  text-align: left;
  padding-left: var(--spacing-xl);
}

.header-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  line-height: 1.2;
}

.header-label .main-text {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.header-label .sub-text {
  font-size: 12px;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.activity-table :deep(.activity-data-table td) {
  color: var(--text-primary);
  font-size: var(--font-size-md);
  border-bottom: 1px solid var(--border-light);
  padding: 18px 16px;
  line-height: 1.6;
  background-color: var(--card-bg);
  text-align: center;
}

.activity-table :deep(.activity-data-table td:first-child) {
  text-align: left;
  padding-left: var(--spacing-xl);
}

.activity-table :deep(.activity-data-table td[align="right"]) {
  text-align: right;
  padding-right: var(--spacing-xl);
}

.activity-table :deep(.activity-data-table .el-table__row:hover) {
  background-color: var(--sidebar-hover) !important;
  transition: background-color 0.2s ease;
}

.activity-table :deep(.activity-data-table .el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #FFFFFF;
}

.activity-table :deep(.activity-data-table .el-table__empty-block) {
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: var(--font-size-md);
}

.card-actions-inline {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-wrap: nowrap;
}

.mobile-activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-card {
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px;
  background-color: var(--card-bg);
  box-shadow: var(--shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  flex: 1;
}

.card-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
}

.field-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.field-value {
  font-size: 16px;
  color: var(--text-primary);
}

.mobile-activity-list :deep(.inline-select .el-select__wrapper) {
  width: 100%;
}

.mobile-activity-list :deep(.inline-input input),
.mobile-activity-list :deep(.inline-input-number input) {
  font-size: 16px;
}

.cell-text {
  display: inline-block;
  font-size: var(--font-size-base);
  color: var(--text-primary);
  letter-spacing: 0;
  font-weight: var(--font-weight-normal);
}

.unit-text {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: 2px;
}

.predecessor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: flex-start;
  justify-content: center;
  min-height: 24px;
}

.predecessor-tag {
  margin: 0;
}

.empty-text {
  color: var(--text-light);
  font-size: var(--font-size-base);
  font-style: normal;
  display: inline-block;
  font-weight: var(--font-weight-normal);
}

/* 無印風格標籤 */
.activity-table :deep(.el-tag) {
  border-radius: 0;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  color: var(--text-primary);
  font-weight: 400;
  font-size: 13px;
  padding: 5px 12px;
  letter-spacing: 0.01em;
  line-height: 1.4;
}

.activity-table :deep(.predecessor-tag) {
  margin: 0;
  border-color: #3B82F6;
  background-color: #DBEAFE;
  color: #1E40AF;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 10px;
  line-height: 1.4;
  white-space: nowrap;
}

/* 無印風格按鈕 */
.activity-table :deep(.el-button) {
  border-radius: 0;
}

.activity-table :deep(.el-button--small) {
  padding: 8px 12px;
  font-size: 14px;
  letter-spacing: 0.01em;
  transition: all 0.25s ease;
}

.activity-table :deep(.el-button--primary) {
  background-color: transparent;
  border-color: var(--primary);
  color: var(--primary);
}

.activity-table :deep(.el-button--primary:hover) {
  background-color: var(--content-bg);
  border-color: var(--primary-hover);
  color: var(--primary-hover);
}

/* 舊的按鈕樣式已移除，使用上方統一的樣式 */

/* 保存和取消按鈕 */
.activity-table :deep(.save-btn) {
  background-color: #10B981 !important;
  border: none !important;
  color: #FFFFFF !important;
  padding: 10px !important;
  min-width: 40px !important;
  width: 40px !important;
  height: 40px !important;
  border-radius: 6px !important;
  box-shadow: 0 1px 2px rgba(16, 185, 129, 0.2) !important;
}

.activity-table :deep(.save-btn:hover) {
  background-color: #059669 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3) !important;
}

.activity-table :deep(.save-btn .el-icon),
.activity-table :deep(.save-btn svg) {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  font-size: 18px;
  width: 18px;
  height: 18px;
}

.activity-table :deep(.cancel-btn) {
  background-color: #6B7280 !important;
  border: none !important;
  color: #FFFFFF !important;
  padding: 10px !important;
  min-width: 40px !important;
  width: 40px !important;
  height: 40px !important;
  border-radius: 6px !important;
  box-shadow: 0 1px 2px rgba(107, 114, 128, 0.2) !important;
}

.activity-table :deep(.cancel-btn:hover) {
  background-color: #4B5563 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(107, 114, 128, 0.3) !important;
}

.activity-table :deep(.cancel-btn .el-icon),
.activity-table :deep(.cancel-btn svg) {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  font-size: 18px;
  width: 18px;
  height: 18px;
}

/* 對話框樣式 - 無印風格 */
.activity-table :deep(.activity-dialog) {
  border-radius: 0;
}

.activity-table :deep(.activity-dialog .el-dialog) {
  border-radius: 0;
  border: 1px solid var(--border-color);
  box-shadow: none;
}

.activity-table :deep(.activity-dialog .el-dialog__header) {
  padding: 24px 28px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--card-bg);
}

.activity-table :deep(.activity-dialog .el-dialog__title) {
  font-size: 20px;
  font-weight: 400;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.activity-table :deep(.activity-dialog .el-dialog__body) {
  padding: 28px;
  background-color: var(--card-bg);
}

.activity-table :deep(.activity-dialog .el-dialog__footer) {
  padding: 20px 28px;
  border-top: 1px solid var(--border-color);
  background-color: var(--card-bg);
}

/* 表單樣式 */
.activity-form {
  padding: 0;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
}

.activity-table :deep(.activity-form .el-form-item) {
  margin-bottom: 20px;
}

.activity-table :deep(.activity-form .el-form-item__label) {
  font-weight: 400;
  color: var(--text-primary);
  font-size: 14px;
  letter-spacing: 0.01em;
  padding-right: 16px;
}

/* 輸入框樣式 - 無印風格 */
.activity-table :deep(.form-input .el-input__wrapper),
.activity-table :deep(.form-input-number .el-input__wrapper),
.activity-table :deep(.form-select .el-input__wrapper),
.activity-table :deep(.form-textarea .el-textarea__inner) {
  border-radius: 0;
  border: 1px solid var(--border-color);
  box-shadow: none;
  background-color: var(--card-bg);
  transition: all 0.25s ease;
}

.activity-table :deep(.form-input .el-input__wrapper:hover),
.activity-table :deep(.form-input-number .el-input__wrapper:hover),
.activity-table :deep(.form-select .el-input__wrapper:hover),
.activity-table :deep(.form-textarea .el-textarea__inner:hover) {
  border-color: var(--primary);
  background-color: var(--content-bg);
}

.activity-table :deep(.form-input .el-input__wrapper.is-focus),
.activity-table :deep(.form-input-number .el-input__wrapper.is-focus),
.activity-table :deep(.form-select .el-input__wrapper.is-focus),
.activity-table :deep(.form-textarea .el-textarea__inner:focus) {
  border-color: var(--primary);
  box-shadow: none;
  background-color: var(--card-bg);
}

.activity-table :deep(.form-textarea .el-textarea__inner) {
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  padding: 10px 12px;
  resize: vertical;
}

.activity-table :deep(.form-input-number) {
  width: 100%;
}

.activity-table :deep(.form-select) {
  width: 100%;
}

/* 按鈕樣式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .activity-table {
    padding: 12px;
    min-height: auto;
  }

  .table-container {
    border: none;
    border-radius: 12px;
    box-shadow: none;
    overflow-x: hidden;
  }

  .table-header-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }

  .add-activity-btn-header {
    width: 100%;
    justify-content: center;
  }

  .activity-card {
    padding: 12px;
    border-radius: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
  }

  .card-title {
    font-size: 16px;
    width: 100%;
  }

  .card-actions-inline {
    width: 100%;
    justify-content: flex-end;
  }

  .card-field {
    margin-top: 10px;
  }

  .field-label {
    font-size: 12px;
  }

  .field-value {
    font-size: 14px;
  }

  .mobile-activity-list :deep(.inline-input),
  .mobile-activity-list :deep(.inline-input-number),
  .mobile-activity-list :deep(.inline-select) {
    width: 100%;
  }

  .mobile-activity-list :deep(.inline-input .el-input__wrapper),
  .mobile-activity-list :deep(.inline-input-number .el-input__wrapper),
  .mobile-activity-list :deep(.inline-select .el-input__wrapper) {
    padding: 0 12px;
    min-height: 44px;
  }

  .mobile-activity-list :deep(.inline-input .el-input__inner),
  .mobile-activity-list :deep(.inline-input-number .el-input__inner),
  .mobile-activity-list :deep(.inline-select .el-input__inner) {
    font-size: 16px;
    min-height: 44px;
    line-height: 44px;
  }

  .activity-table :deep(.activity-dialog .el-dialog) {
    width: 95% !important;
    max-width: 100% !important;
    margin: 0 auto !important;
  }

  .activity-table :deep(.activity-dialog .el-dialog__body) {
    padding: 16px;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }

  .activity-table :deep(.activity-dialog .el-dialog__header) {
    padding: 16px;
  }

  .activity-table :deep(.activity-dialog .el-dialog__footer) {
    padding: 12px 16px;
  }
}

.activity-table :deep(.cancel-btn) {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 10px 24px;
  font-size: 14px;
  letter-spacing: 0.01em;
  transition: all 0.25s ease;
}

.activity-table :deep(.cancel-btn:hover) {
  background-color: var(--content-bg);
  border-color: var(--primary);
  color: var(--primary);
}

.activity-table :deep(.submit-btn) {
  background-color: var(--primary);
  border-color: var(--primary);
  color: var(--text-white);
  padding: 10px 24px;
  font-size: 14px;
  letter-spacing: 0.02em;
  transition: all 0.25s ease;
}

.activity-table :deep(.submit-btn:hover) {
  background-color: var(--primary-hover);
  border-color: var(--primary-hover);
  color: var(--text-white);
}
</style>

