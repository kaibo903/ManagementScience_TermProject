<template>
  <div class="activity-table">
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增作業
      </el-button>
    </div>

    <el-table :data="activities" v-loading="loading" stripe border>
      <el-table-column prop="name" label="作業名稱" width="200" />
      <el-table-column prop="normal_duration" label="正常工期（天）" width="120" align="center" />
      <el-table-column prop="normal_cost" label="正常成本" width="120" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.normal_cost) }}
        </template>
      </el-table-column>
      <el-table-column prop="crash_duration" label="趕工工期（天）" width="120" align="center" />
      <el-table-column prop="crash_cost" label="趕工成本" width="120" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.crash_cost) }}
        </template>
      </el-table-column>
      <el-table-column label="前置作業" width="200">
        <template #default="{ row }">
          <el-tag
            v-for="pred in getPredecessors(row.id)"
            :key="pred.id"
            size="small"
            style="margin-right: 5px;"
          >
            {{ pred.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editActivity(row)">編輯</el-button>
          <el-button size="small" type="danger" @click="deleteActivity(row)">刪除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 建立/編輯作業對話框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingActivity ? '編輯作業' : '新增作業'"
      width="600px"
    >
      <el-form :model="activityForm" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="作業名稱" prop="name">
          <el-input v-model="activityForm.name" placeholder="請輸入作業名稱" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="activityForm.description"
            type="textarea"
            :rows="2"
            placeholder="請輸入作業描述"
          />
        </el-form-item>
        <el-form-item label="正常工期（天）" prop="normal_duration">
          <el-input-number
            v-model="activityForm.normal_duration"
            :min="1"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="正常成本" prop="normal_cost">
          <el-input-number
            v-model="activityForm.normal_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="趕工工期（天）" prop="crash_duration">
          <el-input-number
            v-model="activityForm.crash_duration"
            :min="1"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="趕工成本" prop="crash_cost">
          <el-input-number
            v-model="activityForm.crash_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="前置作業">
          <el-select
            v-model="activityForm.predecessor_ids"
            multiple
            placeholder="請選擇前置作業"
            style="width: 100%"
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
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveActivity" :loading="saving">確定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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
  if (editingActivity.value) {
    return activities.value.filter(act => act.id !== editingActivity.value.id)
  }
  return activities.value
})

// 載入作業列表
const loadActivities = async () => {
  loading.value = true
  try {
    activities.value = await activityAPI.getActivities(props.projectId)
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

// 編輯作業
const editActivity = async (activity) => {
  editingActivity.value = activity
  // 載入前置作業
  try {
    const predecessors = await activityAPI.getPredecessors(activity.id)
    activityForm.value = {
      name: activity.name,
      description: activity.description || '',
      normal_duration: activity.normal_duration,
      normal_cost: parseFloat(activity.normal_cost),
      crash_duration: activity.crash_duration,
      crash_cost: parseFloat(activity.crash_cost),
      predecessor_ids: predecessors.map(p => p.id)
    }
  } catch (error) {
    activityForm.value = {
      name: activity.name,
      description: activity.description || '',
      normal_duration: activity.normal_duration,
      normal_cost: parseFloat(activity.normal_cost),
      crash_duration: activity.crash_duration,
      crash_cost: parseFloat(activity.crash_cost),
      predecessor_ids: []
    }
  }
  showCreateDialog.value = true
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

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activity-table {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}
</style>

