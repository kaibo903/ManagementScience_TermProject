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
      
      <el-table 
      :data="displayActivities" 
      v-loading="loading" 
      stripe 
      border
      class="activity-data-table"
      :empty-text="emptyText"
    >
      <el-table-column prop="name" label="作業名稱" width="120" min-width="120">
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
      <el-table-column prop="normal_duration" label="工期" width="80" align="center">
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
      <el-table-column label="開始時間" width="100" align="center">
        <template #default="{ row }">
          <span class="cell-text empty-text">-</span>
        </template>
      </el-table-column>
      <el-table-column label="結束時間" width="100" align="center">
        <template #default="{ row }">
          <span class="cell-text empty-text">-</span>
        </template>
      </el-table-column>
      <el-table-column label="前置作業" width="120" align="center">
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
      <el-table-column label="後續作業" width="120" align="center">
        <template #default="{ row }">
          <span class="cell-text empty-text">無</span>
        </template>
      </el-table-column>
      <el-table-column prop="normal_cost" label="成本" width="120" align="right">
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
          >
            <template #prefix>NT$</template>
          </el-input-number>
          <span v-else class="cell-text">{{ formatCurrency(row.normal_cost) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right" align="center">
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
            >
              <template #prefix>NT$</template>
            </el-input-number>
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
            >
              <template #prefix>NT$</template>
            </el-input-number>
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
import { ref, onMounted, computed } from 'vue'
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
  normal_duration: 1,
  normal_cost: 0,
  crash_duration: 1,
  crash_cost: 0,
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
    normal_duration: 1,
    normal_cost: 0,
    crash_duration: 1,
    crash_cost: 0,
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
    normal_duration: 1,
    normal_cost: 0,
    crash_duration: 1,
    crash_cost: 0,
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

onMounted(() => {
  loadActivities()
})
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
.activity-table :deep(.inline-input .el-input__wrapper),
.activity-table :deep(.inline-input-number .el-input__wrapper),
.activity-table :deep(.inline-select .el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #E5E7EB;
  box-shadow: none;
  background-color: #FFFFFF;
  transition: all 0.2s ease;
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
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background-color: #FFFFFF;
}

.activity-table :deep(.inline-input-number .el-input__inner) {
  text-align: inherit;
}

.activity-table :deep(.inline-input-number) {
  width: 100%;
}

.activity-table :deep(.inline-select) {
  width: 100%;
}

.action-buttons-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
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

/* 現代專業風格表格 */
.activity-table :deep(.activity-data-table) {
  border: none;
  border-radius: 0;
  overflow: hidden;
}

.activity-table :deep(.activity-data-table .el-table__header-wrapper) {
  background-color: var(--card-bg);
}

.activity-table :deep(.activity-data-table th) {
  background-color: #F9FAFB;
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
  border-bottom: 2px solid var(--border-color);
  padding: var(--spacing-md) var(--spacing-md);
  letter-spacing: 0;
  text-align: center;
  white-space: nowrap;
}

.activity-table :deep(.activity-data-table td) {
  color: var(--text-primary);
  font-size: var(--font-size-base);
  border-bottom: 1px solid var(--border-light);
  padding: var(--spacing-lg) var(--spacing-md);
  line-height: 1.6;
  background-color: var(--card-bg);
  text-align: center;
  font-weight: var(--font-weight-normal);
}

.activity-table :deep(.activity-data-table th:first-child),
.activity-table :deep(.activity-data-table td:first-child) {
  text-align: left;
  padding-left: 20px;
}

.activity-table :deep(.activity-data-table td[align="right"]) {
  text-align: right;
  padding-right: 20px;
}

.activity-table :deep(.activity-data-table .el-table__row:hover) {
  background-color: #F9FAFB !important;
  transition: background-color 0.15s ease;
}

.activity-table :deep(.activity-data-table .el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #FFFFFF;
}

.activity-table :deep(.activity-data-table .el-table__empty-block) {
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 14px;
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

/* 操作按鈕 - 紅色方塊按鈕設計 */
.activity-table :deep(.el-button--primary.is-text) {
  background-color: #EF4444;
  border: none;
  color: #FFFFFF;
  padding: 10px;
  min-width: 40px;
  width: 40px;
  height: 40px;
  border-radius: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(239, 68, 68, 0.2);
}

.activity-table :deep(.el-button--primary.is-text:hover) {
  background-color: #DC2626;
  border: none;
  color: #FFFFFF;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.activity-table :deep(.el-button--primary.is-text .el-icon),
.activity-table :deep(.el-button--primary.is-text svg) {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  font-size: 18px;
  width: 18px;
  height: 18px;
}

.activity-table :deep(.el-button--danger.is-text) {
  background-color: #EF4444;
  border: none;
  color: #FFFFFF;
  padding: 10px;
  min-width: 40px;
  width: 40px;
  height: 40px;
  border-radius: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(239, 68, 68, 0.2);
}

.activity-table :deep(.el-button--danger.is-text:hover) {
  background-color: #DC2626;
  border: none;
  color: #FFFFFF;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.activity-table :deep(.el-button--danger.is-text .el-icon),
.activity-table :deep(.el-button--danger.is-text svg) {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  font-size: 18px;
  width: 18px;
  height: 18px;
}

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

