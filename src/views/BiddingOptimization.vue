<template>
  <div class="bidding-optimization">
    <el-card>
      <template #header>
        <span>投標最佳化決策</span>
      </template>

      <el-form :model="optimizationForm" label-width="150px" :rules="rules" ref="formRef">
        <el-form-item label="選擇專案" prop="project_id">
          <el-select
            v-model="optimizationForm.project_id"
            placeholder="請選擇專案"
            style="width: 100%"
            @change="loadProjectActivities"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="決策模式" prop="mode">
          <el-radio-group v-model="optimizationForm.mode" @change="handleModeChange">
            <el-radio label="budget_to_duration">模式一：給定預算，求最短工期</el-radio>
            <el-radio label="duration_to_cost">模式二：給定工期，求最低成本</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="optimizationForm.mode === 'budget_to_duration'"
          label="預算約束"
          prop="budget_constraint"
        >
          <el-input-number
            v-model="optimizationForm.budget_constraint"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="請輸入預算金額"
          />
        </el-form-item>

        <el-form-item
          v-if="optimizationForm.mode === 'duration_to_cost'"
          label="工期約束（天）"
          prop="duration_constraint"
        >
          <el-input-number
            v-model="optimizationForm.duration_constraint"
            :min="1"
            :precision="0"
            style="width: 100%"
            placeholder="請輸入目標工期"
          />
        </el-form-item>

        <el-form-item label="逾期違約金率（每日）">
          <el-input-number
            v-model="optimizationForm.penalty_rate"
            :min="0"
            :precision="4"
            style="width: 100%"
            placeholder="逾期每日的違約金率"
          />
        </el-form-item>

        <el-form-item label="趕工獎金率（每日）">
          <el-input-number
            v-model="optimizationForm.bonus_rate"
            :min="0"
            :precision="4"
            style="width: 100%"
            placeholder="提前每日的獎金率"
          />
        </el-form-item>

        <el-form-item label="目標工期（天）">
          <el-input-number
            v-model="optimizationForm.target_duration"
            :min="1"
            :precision="0"
            style="width: 100%"
            placeholder="用於計算獎懲的目標工期（可選）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="runOptimization" :loading="optimizing" size="large">
            <el-icon><Search /></el-icon>
            執行優化計算
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 優化結果 -->
      <el-card v-if="optimizationResult" class="result-card" style="margin-top: 20px;">
        <template #header>
          <span>優化結果</span>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="最優工期">
            {{ optimizationResult.optimal_duration }} 天
          </el-descriptions-item>
          <el-descriptions-item label="最優成本">
            {{ formatCurrency(optimizationResult.optimal_cost) }}
          </el-descriptions-item>
          <el-descriptions-item label="違約金">
            {{ formatCurrency(optimizationResult.penalty_amount) }}
          </el-descriptions-item>
          <el-descriptions-item label="獎金">
            {{ formatCurrency(optimizationResult.bonus_amount) }}
          </el-descriptions-item>
          <el-descriptions-item label="總成本（含獎懲）" :span="2">
            <strong>{{ formatCurrency(optimizationResult.total_cost) }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="計算時間">
            {{ optimizationResult.calculation_time?.toFixed(3) }} 秒
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px;">
          <el-button type="primary" @click="viewDetailedResult">
            查看詳細結果與圖表
          </el-button>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { projectAPI, optimizationAPI } from '../services/api'

const router = useRouter()

const projects = ref([])
const optimizing = ref(false)
const optimizationResult = ref(null)
const formRef = ref(null)

const optimizationForm = ref({
  project_id: null,
  mode: 'budget_to_duration',
  budget_constraint: null,
  duration_constraint: null,
  penalty_rate: 0,
  bonus_rate: 0,
  target_duration: null
})

const rules = {
  project_id: [{ required: true, message: '請選擇專案', trigger: 'change' }],
  mode: [{ required: true, message: '請選擇決策模式', trigger: 'change' }],
  budget_constraint: [
    {
      validator: (rule, value, callback) => {
        if (optimizationForm.value.mode === 'budget_to_duration' && !value) {
          callback(new Error('請輸入預算約束'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  duration_constraint: [
    {
      validator: (rule, value, callback) => {
        if (optimizationForm.value.mode === 'duration_to_cost' && !value) {
          callback(new Error('請輸入工期約束'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 載入專案列表
const loadProjects = async () => {
  try {
    projects.value = await projectAPI.getProjects()
  } catch (error) {
    ElMessage.error('載入專案列表失敗：' + error.message)
  }
}

// 載入專案作業（用於驗證）
const loadProjectActivities = async () => {
  // 可以在這裡載入作業以進行驗證
}

// 處理模式變更
const handleModeChange = () => {
  optimizationForm.value.budget_constraint = null
  optimizationForm.value.duration_constraint = null
}

// 執行優化計算
const runOptimization = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    optimizing.value = true
    try {
      const result = await optimizationAPI.optimize(optimizationForm.value)
      optimizationResult.value = result
      ElMessage.success('優化計算完成')
    } catch (error) {
      ElMessage.error('優化計算失敗：' + error.message)
    } finally {
      optimizing.value = false
    }
  })
}

// 查看詳細結果
const viewDetailedResult = () => {
  if (optimizationResult.value?.scenario_id) {
    router.push(`/results/${optimizationResult.value.scenario_id}`)
  }
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
  loadProjects()
})
</script>

<style scoped>
.bidding-optimization {
  max-width: 1000px;
  margin: 0 auto;
}

.result-card {
  background-color: #f9fafb;
}
</style>

