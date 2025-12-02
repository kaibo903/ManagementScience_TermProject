<template>
  <div class="optimization-process">
    <el-card class="process-card">
      <template #header>
        <div class="card-header">
          <h2 class="card-title">最佳化計算過程說明</h2>
        </div>
      </template>

      <!-- 問題類型說明 -->
      <div class="section">
        <h3 class="section-title">一、問題類型</h3>
        <div class="content-box">
          <p><strong>混合整數線性規劃（Mixed Integer Linear Programming, MILP）</strong></p>
          <p class="description">
            本系統使用 MILP 求解營造專案的最佳化決策問題。MILP 是一種數學優化方法，
            其中部分變數限制為整數（如開始時間、工期），部分變數為 0/1 二元變數（如是否趕工）。
          </p>
        </div>
      </div>

      <!-- 優化模式 -->
      <div class="section">
        <h3 class="section-title">二、優化模式</h3>
        <div class="content-box">
          <div class="mode-badge" :class="`mode-${optimizationData.mode}`">
            {{ optimizationData.mode === 'budget_to_duration' ? '模式一：給定預算，求最短工期' : '模式二：給定工期，求最低成本' }}
          </div>
          <div class="constraints-list">
            <div v-if="optimizationData.mode === 'budget_to_duration'" class="constraint-item">
              <span class="constraint-label">預算約束：</span>
              <span class="constraint-value">{{ formatCurrency(optimizationData.budget_constraint) }}</span>
            </div>
            <div v-else class="constraint-item">
              <span class="constraint-label">工期約束：</span>
              <span class="constraint-value">{{ optimizationData.duration_constraint }} 天</span>
            </div>
            <div v-if="optimizationData.indirect_cost" class="constraint-item">
              <span class="constraint-label">間接成本：</span>
              <span class="constraint-value">{{ formatCurrency(optimizationData.indirect_cost) }} / 天</span>
            </div>
            <div v-if="optimizationData.target_duration" class="constraint-item">
              <span class="constraint-label">目標工期：</span>
              <span class="constraint-value">{{ optimizationData.target_duration }} 天</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 數學模型 -->
      <div class="section">
        <h3 class="section-title">三、MILP 數學模型</h3>
        
        <!-- 決策變數 -->
        <div class="subsection">
          <h4 class="subsection-title">3.1 決策變數</h4>
          <div class="formula-box">
            <div class="formula-item">
              <span class="formula-var">x<sub>i</sub></span>
              <span class="formula-desc">：作業 i 的開始時間（整數變數，單位：天）</span>
            </div>
            <div class="formula-item">
              <span class="formula-var">y<sub>i</sub></span>
              <span class="formula-desc">：作業 i 是否趕工（二元變數，0 = 正常施工，1 = 趕工）</span>
            </div>
            <div class="formula-item">
              <span class="formula-var">T</span>
              <span class="formula-desc">：專案總工期（整數變數，單位：天）</span>
            </div>
          </div>
          <div class="variable-details">
            <p><strong>變數總數：</strong></p>
            <ul>
              <li>連續/整數變數：{{ activities.length + 1 }} 個（{{ activities.length }} 個作業開始時間 + 1 個總工期）</li>
              <li>二元變數：{{ activities.length }} 個（每個作業的趕工決策）</li>
            </ul>
          </div>
        </div>

        <!-- 目標函數 -->
        <div class="subsection">
          <h4 class="subsection-title">3.2 目標函數</h4>
          <div class="formula-box">
            <div v-if="optimizationData.mode === 'budget_to_duration'" class="objective-formula">
              <div class="formula-line">
                <strong>目標：</strong> min Z = T + P - B
              </div>
              <div class="formula-explanation">
                <p>其中：</p>
                <ul>
                  <li>
                    <strong>T</strong>：專案總工期
                    <span class="calc-value"> = {{ result.optimal_duration }} 天</span>
                  </li>
                  <li>
                    <strong>P</strong>：違約金（若 T > 目標工期）
                    <span class="calc-value"> = {{ formatCurrency(result.penalty_amount) }}</span>
                  </li>
                  <li>
                    <strong>B</strong>：趕工獎金（若 T < 目標工期）
                    <span class="calc-value"> = {{ formatCurrency(result.bonus_amount) }}</span>
                  </li>
                </ul>
                <div class="total-calc">
                  <strong>總目標值：</strong>
                  {{ result.optimal_duration }} 天 + {{ formatCurrency(result.penalty_amount) }} 
                  - {{ formatCurrency(result.bonus_amount) }}
                  <br>
                  <strong>總成本（含獎懲）：</strong>
                  {{ formatCurrency(result.optimal_cost) }} + {{ formatCurrency(result.indirect_cost) }} 
                  + {{ formatCurrency(result.penalty_amount) }} - {{ formatCurrency(result.bonus_amount) }}
                  = <span class="highlight">{{ formatCurrency(result.total_cost) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="objective-formula">
              <div class="formula-line">
                <strong>目標：</strong> min Z = C<sub>直接</sub> + C<sub>間接</sub> + P - B
              </div>
              <div class="formula-explanation">
                <p>其中：</p>
                <ul>
                  <li>
                    <strong>C<sub>直接</sub></strong> = Σ [c<sub>i,正常</sub> × (1 - y<sub>i</sub>) + c<sub>i,趕工</sub> × y<sub>i</sub>]
                    <span class="calc-value"> = {{ formatCurrency(result.optimal_cost) }}</span>
                  </li>
                  <li>
                    <strong>C<sub>間接</sub></strong> = 間接成本率 × T = {{ formatCurrency(optimizationData.indirect_cost) }} × {{ result.optimal_duration }}
                    <span class="calc-value"> = {{ formatCurrency(result.indirect_cost) }}</span>
                  </li>
                  <li>
                    <strong>P</strong>：違約金 
                    <span class="calc-value"> = {{ formatCurrency(result.penalty_amount) }}</span>
                  </li>
                  <li>
                    <strong>B</strong>：趕工獎金 
                    <span class="calc-value"> = {{ formatCurrency(result.bonus_amount) }}</span>
                  </li>
                </ul>
                <div class="total-calc">
                  <strong>總目標值：</strong>
                  {{ formatCurrency(result.optimal_cost) }} + {{ formatCurrency(result.indirect_cost) }} 
                  + {{ formatCurrency(result.penalty_amount) }} - {{ formatCurrency(result.bonus_amount) }}
                  = <span class="highlight">{{ formatCurrency(result.total_cost) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 限制式 -->
        <div class="subsection">
          <h4 class="subsection-title">3.3 限制式</h4>
          <div class="constraints-box">
            <div class="constraint-group">
              <div class="constraint-title">
                <el-icon><Check /></el-icon>
                前置作業約束（共 {{ precedences.length }} 條）
              </div>
              <div class="constraint-formula">
                x<sub>j</sub> ≥ x<sub>i</sub> + d<sub>i</sub>, ∀ (i, j) ∈ 前置關係
              </div>
              <div class="constraint-desc">
                其中 d<sub>i</sub> = d<sub>i,正常</sub> × (1 - y<sub>i</sub>) + d<sub>i,趕工</sub> × y<sub>i</sub>
                <br>
                <em>說明：後續作業 j 的開始時間必須 ≥ 前置作業 i 的結束時間</em>
              </div>
              <div v-if="precedences.length > 0" class="constraint-example">
                <strong>範例：</strong>
                <div v-for="(prec, idx) in precedences.slice(0, 3)" :key="idx" class="example-item">
                  {{ getActivityName(prec.successor) }} 必須在 {{ getActivityName(prec.predecessor) }} 完成後才能開始
                </div>
                <div v-if="precedences.length > 3" class="more-info">
                  ...等共 {{ precedences.length }} 條前置關係
                </div>
              </div>
            </div>

            <div class="constraint-group">
              <div class="constraint-title">
                <el-icon><Check /></el-icon>
                工期定義約束（共 {{ activities.length }} 條）
              </div>
              <div class="constraint-formula">
                T ≥ x<sub>i</sub> + d<sub>i</sub>, ∀ i ∈ 作業集合
              </div>
              <div class="constraint-desc">
                <em>說明：專案總工期必須 ≥ 所有作業的結束時間</em>
              </div>
            </div>

            <div v-if="optimizationData.mode === 'budget_to_duration'" class="constraint-group">
              <div class="constraint-title">
                <el-icon><Check /></el-icon>
                預算約束
              </div>
              <div class="constraint-formula">
                C<sub>直接</sub> + C<sub>間接</sub> ≤ {{ formatCurrency(optimizationData.budget_constraint) }}
              </div>
              <div class="constraint-desc">
                <em>說明：直接成本 + 間接成本不得超過預算</em>
              </div>
            </div>

            <div v-else class="constraint-group">
              <div class="constraint-title">
                <el-icon><Check /></el-icon>
                工期約束（工期固定）
              </div>
              <div class="constraint-formula">
                T = {{ optimizationData.duration_constraint }} 天
              </div>
              <div class="constraint-desc">
                <em>說明：在「工期固定」模式中，專案總工期 T 會被嚴格固定為您輸入的工期值</em>
              </div>
            </div>

            <div class="constraint-group">
              <div class="constraint-title">
                <el-icon><Check /></el-icon>
                變數範圍約束
              </div>
              <div class="constraint-formula">
                x<sub>i</sub> ≥ 0, y<sub>i</sub> ∈ {0, 1}, T ≥ 0
              </div>
              <div class="constraint-desc">
                <em>說明：開始時間與工期為非負整數，趕工決策為二元變數</em>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 求解過程 -->
      <div class="section">
        <h3 class="section-title">四、求解過程</h3>
        <div class="solve-steps">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <div class="step-title">建立 MILP 模型</div>
              <div class="step-desc">
                根據上述數學模型，系統建立包含 {{ activities.length * 2 + 1 }} 個變數、
                {{ precedences.length + activities.length + 1 }} 條以上限制式的 MILP 問題
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <div class="step-title">調用 CBC 求解器</div>
              <div class="step-desc">
                使用 COIN-OR Branch and Cut (CBC) 求解器進行求解。
                CBC 是一個開源的 MILP 求解器，採用分支定界法（Branch-and-Bound）與割平面法（Cutting Plane）求解整數規劃問題
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <div class="step-title">搜尋最優解</div>
              <div class="step-desc">
                求解器探索可行解空間，透過線性鬆弛（Linear Relaxation）與分支策略，
                逐步縮小搜尋範圍，尋找滿足所有限制式且目標函數值最小的解
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <div class="step-title">驗證最優性</div>
              <div class="step-desc">
                當求解器找到一個可行解，且能證明該解的目標值不可能再改善時，
                即確認為全局最優解（Global Optimum）
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">5</div>
            <div class="step-content">
              <div class="step-title">提取最優解</div>
              <div class="step-desc">
                從求解器提取各決策變數的最優值：
                <ul>
                  <li>每個作業的開始時間 x<sub>i</sub>*</li>
                  <li>每個作業是否趕工 y<sub>i</sub>*</li>
                  <li>專案總工期 T*</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">6</div>
            <div class="step-content">
              <div class="step-title">計算結果指標</div>
              <div class="step-desc">
                根據最優解計算各項成本與獎懲：
                <ul>
                  <li>直接成本 = Σ [選定的作業成本]</li>
                  <li>間接成本 = 間接成本率 × T*</li>
                  <li>違約金/獎金（根據實際工期與目標工期比較）</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 求解時間 -->
        <div class="solve-result">
          <el-icon><Clock /></el-icon>
          <span class="result-text">
            求解完成時間：<strong>{{ (result.calculation_time * 1000).toFixed(2) }} 毫秒</strong>
          </span>
        </div>
      </div>

      <!-- 最優解詳細結果 -->
      <div class="section">
        <h3 class="section-title">五、最優解詳細結果</h3>
        
        <!-- 工期結果 -->
        <div class="result-box">
          <div class="result-item primary">
            <span class="result-label">最優工期（T*）</span>
            <span class="result-value">{{ result.optimal_duration }} 天</span>
          </div>
          <div class="result-item">
            <span class="result-label">直接成本</span>
            <span class="result-value">{{ formatCurrency(result.optimal_cost) }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">間接成本</span>
            <span class="result-value">{{ formatCurrency(result.indirect_cost) }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">違約金</span>
            <span class="result-value">{{ formatCurrency(result.penalty_amount) }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">趕工獎金</span>
            <span class="result-value">{{ formatCurrency(result.bonus_amount) }}</span>
          </div>
          <div class="result-item total">
            <span class="result-label">總成本（含獎懲）</span>
            <span class="result-value">{{ formatCurrency(result.total_cost) }}</span>
          </div>
        </div>

        <!-- 作業趕工決策 -->
        <div class="decision-table">
          <h4 class="subsection-title">5.1 作業趕工決策（y<sub>i</sub>*）</h4>
          <div class="stats-row">
            <div class="stat-item">
              <span class="stat-label">正常施工：</span>
              <span class="stat-value">{{ normalCount }} 項作業</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">趕工：</span>
              <span class="stat-value">{{ crashedCount }} 項作業</span>
            </div>
          </div>
          <el-table :data="schedules" stripe border class="schedule-table">
            <el-table-column prop="activity_name" label="作業名稱" width="200" />
            <el-table-column label="開始時間（x_i*）" width="120" align="center">
              <template #default="{ row }">
                第 {{ row.start_time }} 天
              </template>
            </el-table-column>
            <el-table-column label="結束時間" width="120" align="center">
              <template #default="{ row }">
                第 {{ row.end_time }} 天
              </template>
            </el-table-column>
            <el-table-column label="工期（d_i*）" width="100" align="center">
              <template #default="{ row }">
                {{ row.duration }} 天
              </template>
            </el-table-column>
            <el-table-column label="趕工決策（y_i*）" width="130" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_crashed ? 'warning' : 'success'" class="decision-tag">
                  {{ row.is_crashed ? '1（趕工）' : '0（正常）' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="作業成本" align="right">
              <template #default="{ row }">
                <span class="cost-text">{{ formatCurrency(row.cost) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 成本計算明細 -->
        <div class="cost-breakdown">
          <h4 class="subsection-title">5.2 成本計算明細</h4>
          <div class="calculation-steps">
            <div class="calc-step">
              <span class="calc-label">直接成本：</span>
              <span class="calc-formula">
                Σ [選定作業成本] = 
                <template v-for="(schedule, idx) in schedules" :key="schedule.activity_id">
                  {{ formatCurrency(schedule.cost) }}<template v-if="idx < schedules.length - 1"> + </template>
                </template>
                = <strong>{{ formatCurrency(result.optimal_cost) }}</strong>
              </span>
            </div>
            <div class="calc-step">
              <span class="calc-label">間接成本：</span>
              <span class="calc-formula">
                {{ formatCurrency(optimizationData.indirect_cost) }} × {{ result.optimal_duration }} 天
                = <strong>{{ formatCurrency(result.indirect_cost) }}</strong>
              </span>
            </div>
            <div v-if="result.penalty_amount > 0" class="calc-step penalty">
              <span class="calc-label">違約金：</span>
              <span class="calc-formula">
                <template v-if="optimizationData.penalty_type === 'fixed' && optimizationData.penalty_amount">
                  違約金 = 每日定額 × 延遲天數
                  <br>
                  = {{ formatCurrency(optimizationData.penalty_amount) }} × {{ result.optimal_duration - optimizationData.target_duration }} 天
                </template>
                <template v-else-if="optimizationData.penalty_type === 'rate' && optimizationData.penalty_rate">
                  違約金 = 合約總價 × 違約金率 × 延遲天數
                  <br>
                  = {{ formatCurrency(optimizationData.contract_amount) }} × {{ (Number(optimizationData.penalty_rate) * 100).toFixed(2) }}% × {{ result.optimal_duration - optimizationData.target_duration }} 天
                </template>
                = <strong>{{ formatCurrency(result.penalty_amount) }}</strong>
                <span v-if="optimizationData.contract_amount && Number(result.penalty_amount) >= Number(optimizationData.contract_amount) * 0.2" style="color: #EF4444;">
                  （已達上限：合約總價的 20%）
                </span>
              </span>
            </div>
            <div v-if="result.bonus_amount > 0" class="calc-step bonus">
              <span class="calc-label">趕工獎金：</span>
              <span class="calc-formula">
                趕工獎金 = 合約總價 × 提前天數 ÷ 合約工期 × 5%
                <br>
                <template v-if="optimizationData.contract_amount && optimizationData.contract_duration">
                  = {{ formatCurrency(optimizationData.contract_amount) }} × {{ optimizationData.target_duration - result.optimal_duration }} ÷ {{ optimizationData.contract_duration }} × 5%
                  = <strong>{{ formatCurrency(result.bonus_amount) }}</strong>
                  <span v-if="Number(result.bonus_amount) >= Number(optimizationData.contract_amount) * 0.01" style="color: #F59E0B;">
                    （已達上限：合約總價的 1%）
                  </span>
                </template>
                <template v-else>
                  = <strong>{{ formatCurrency(result.bonus_amount) }}</strong>
                </template>
              </span>
            </div>
            <div class="calc-step total">
              <span class="calc-label">總成本：</span>
              <span class="calc-formula">
                {{ formatCurrency(result.optimal_cost) }} + {{ formatCurrency(result.indirect_cost) }}
                <template v-if="result.penalty_amount > 0"> + {{ formatCurrency(result.penalty_amount) }}</template>
                <template v-if="result.bonus_amount > 0"> - {{ formatCurrency(result.bonus_amount) }}</template>
                = <strong class="highlight">{{ formatCurrency(result.total_cost) }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 最優性證明 -->
      <div class="section">
        <h3 class="section-title">六、最優性保證</h3>
        <div class="content-box optimality">
          <div class="optimality-item">
            <el-icon class="icon-success"><CircleCheck /></el-icon>
            <div class="optimality-content">
              <strong>全局最優解：</strong>
              CBC 求解器使用精確演算法（分支定界法），保證找到的解為全局最優解，
              而非局部最優解
            </div>
          </div>
          <div class="optimality-item">
            <el-icon class="icon-success"><CircleCheck /></el-icon>
            <div class="optimality-content">
              <strong>可行性驗證：</strong>
              所有限制式均已滿足，包括前置關係、工期/預算約束等
            </div>
          </div>
          <div class="optimality-item">
            <el-icon class="icon-success"><CircleCheck /></el-icon>
            <div class="optimality-content">
              <strong>目標值最優：</strong>
              在滿足所有限制式的前提下，目標函數值（{{ optimizationData.mode === 'budget_to_duration' ? '工期 + 獎懲' : '總成本 + 獎懲' }}）
              已達到理論最小值，無法再進一步改善
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Clock, CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  },
  optimizationData: {
    type: Object,
    required: true
  },
  activities: {
    type: Array,
    required: true
  },
  precedences: {
    type: Array,
    required: true
  }
})

// 計算統計數據
const schedules = computed(() => props.result.schedules || [])

const normalCount = computed(() => {
  return schedules.value.filter(s => !s.is_crashed).length
})

const crashedCount = computed(() => {
  return schedules.value.filter(s => s.is_crashed).length
})

// 格式化貨幣
const formatCurrency = (value) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(value)
}

// 根據 ID 獲取作業名稱
const getActivityName = (activityId) => {
  const activity = props.activities.find(a => a.id === activityId)
  return activity ? activity.name : activityId
}
</script>

<style scoped>
.optimization-process {
  margin-top: 24px;
}

.process-card {
  border: 1px solid var(--border-color);
  border-radius: 0;
  box-shadow: none;
}

.process-card :deep(.el-card__header) {
  background-color: #F9FAFB;
  border-bottom: 2px solid var(--border-color);
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 區段樣式 */
.section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border-light);
}

.section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid var(--primary);
}

.subsection {
  margin-bottom: 24px;
}

.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

/* 內容框 */
.content-box {
  background-color: #F9FAFB;
  border: 1px solid var(--border-color);
  border-radius: 0;
  padding: 20px;
  line-height: 1.8;
}

.content-box p {
  margin: 0 0 8px 0;
}

.content-box .description {
  color: var(--text-secondary);
  margin-top: 8px;
}

/* 模式標籤 */
.mode-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 0;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 16px;
}

.mode-badge.mode-budget_to_duration {
  background-color: #EEF2FF;
  color: #4F46E5;
  border: 1px solid #C7D2FE;
}

.mode-badge.mode-duration_to_cost {
  background-color: #F0FDF4;
  color: #16A34A;
  border: 1px solid #BBF7D0;
}

/* 約束列表 */
.constraints-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.constraint-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.constraint-label {
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 120px;
}

.constraint-value {
  color: var(--text-primary);
  font-weight: 600;
}

/* 公式框 */
.formula-box {
  background-color: #FFFFFF;
  border: 1px solid var(--border-color);
  border-radius: 0;
  padding: 20px;
  margin-bottom: 16px;
}

.formula-item {
  display: flex;
  align-items: baseline;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
}

.formula-item:last-child {
  border-bottom: none;
}

.formula-var {
  font-family: 'Times New Roman', serif;
  font-size: 16px;
  font-weight: 600;
  color: #1F2937;
  min-width: 60px;
}

.formula-desc {
  color: var(--text-secondary);
  line-height: 1.6;
}

.variable-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.variable-details ul {
  margin: 8px 0 0 0;
  padding-left: 24px;
}

.variable-details li {
  color: var(--text-secondary);
  line-height: 1.8;
}

/* 目標函數 */
.objective-formula {
  line-height: 1.8;
}

.formula-line {
  font-size: 16px;
  padding: 12px 0;
  color: var(--text-primary);
}

.formula-explanation {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.formula-explanation ul {
  margin: 8px 0;
  padding-left: 24px;
}

.formula-explanation li {
  margin: 8px 0;
  line-height: 1.8;
  color: var(--text-secondary);
}

.calc-value {
  color: var(--primary);
  font-weight: 600;
  margin-left: 8px;
}

.total-calc {
  margin-top: 16px;
  padding: 16px;
  background-color: #F0F9FF;
  border: 1px solid #BAE6FD;
  border-radius: 0;
  font-size: 15px;
  line-height: 1.8;
}

.total-calc .highlight {
  color: #DC2626;
  font-size: 18px;
  font-weight: 700;
}

/* 限制式框 */
.constraints-box {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.constraint-group {
  background-color: #FFFFFF;
  border: 1px solid var(--border-color);
  border-radius: 0;
  padding: 16px;
}

.constraint-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.constraint-title .el-icon {
  color: #10B981;
}

.constraint-formula {
  font-family: 'Times New Roman', serif;
  font-size: 15px;
  padding: 12px;
  background-color: #F9FAFB;
  border-left: 3px solid var(--primary);
  margin-bottom: 8px;
}

.constraint-desc {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-top: 8px;
}

.constraint-example {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-color);
}

.example-item {
  padding: 4px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.more-info {
  color: var(--text-tertiary);
  font-style: italic;
  margin-top: 8px;
}

/* 求解步驟 */
.solve-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.step-item {
  display: flex;
  gap: 16px;
  background-color: #FFFFFF;
  border: 1px solid var(--border-color);
  border-radius: 0;
  padding: 20px;
}

.step-number {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary);
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
  border-radius: 50%;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.step-desc {
  color: var(--text-secondary);
  line-height: 1.8;
  font-size: 14px;
}

.step-desc ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.step-desc li {
  margin: 4px 0;
}

.solve-result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: #F0FDF4;
  border: 1px solid #BBF7D0;
  border-radius: 0;
}

.solve-result .el-icon {
  font-size: 20px;
  color: #16A34A;
}

.result-text {
  color: var(--text-primary);
  font-size: 15px;
}

/* 結果框 */
.result-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background-color: #F9FAFB;
  border: 1px solid var(--border-color);
  border-radius: 0;
}

.result-item.primary {
  background-color: #EEF2FF;
  border-color: #C7D2FE;
}

.result-item.total {
  grid-column: 1 / -1;
  background-color: #FEF2F2;
  border-color: #FECACA;
}

.result-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.result-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.result-item.total .result-value {
  color: #DC2626;
  font-size: 24px;
}

/* 決策表格 */
.decision-table {
  margin-top: 24px;
}

.stats-row {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #F9FAFB;
  border: 1px solid var(--border-color);
  border-radius: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  color: var(--text-primary);
  font-weight: 600;
}

.schedule-table {
  border-radius: 0;
}

.schedule-table :deep(th) {
  background-color: #F9FAFB;
  color: var(--text-primary);
  font-weight: 600;
  border-radius: 0;
}

.decision-tag {
  border-radius: 0;
  font-weight: 500;
}

.cost-text {
  font-weight: 600;
  color: var(--text-primary);
}

/* 成本明細 */
.cost-breakdown {
  margin-top: 24px;
}

.calculation-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.calc-step {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background-color: #F9FAFB;
  border: 1px solid var(--border-color);
  border-radius: 0;
}

.calc-step.penalty {
  background-color: #FEF2F2;
  border-color: #FECACA;
}

.calc-step.bonus {
  background-color: #F0FDF4;
  border-color: #BBF7D0;
}

.calc-step.total {
  background-color: #FFF7ED;
  border: 2px solid #FDBA74;
}

.calc-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.calc-formula {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
  font-family: 'Times New Roman', serif;
}

.calc-formula strong {
  color: var(--text-primary);
  font-weight: 700;
}

.calc-step.total .calc-formula {
  font-size: 16px;
}

.calc-step.total .highlight {
  color: #DC2626;
  font-size: 20px;
}

/* 最優性保證 */
.content-box.optimality {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.optimality-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.icon-success {
  color: #10B981;
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.optimality-content {
  flex: 1;
  line-height: 1.8;
  color: var(--text-secondary);
}

.optimality-content strong {
  color: var(--text-primary);
}
</style>

