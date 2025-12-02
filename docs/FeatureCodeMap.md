# 功能與程式碼對應表

本文檔標註各功能邏輯的所在檔案與模組位置，以利後續維護與更新。

## 目錄結構

```
專案根目錄/
├── frontend/ (實際為 src/)
│   ├── components/          # Vue 元件
│   ├── views/               # 頁面視圖
│   ├── services/            # API 服務層
│   ├── utils/               # 工具函數
│   ├── router/              # 路由配置
│   └── lib/                 # 第三方庫配置
├── backend/
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── models/          # MILP 模型
│   │   ├── schemas/         # 資料驗證
│   │   └── utils/           # 工具函數
│   └── main.py              # FastAPI 主程式
├── docs/                    # 文件目錄
└── supabase/
    └── migrations/          # 資料庫遷移腳本
```

## 功能對應表

### 1. 專案管理

#### 1.1 專案 CRUD

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 專案列表 | `src/views/ProjectManagement.vue` | `backend/app/api/projects.py` (get_projects) | 取得所有專案 |
| 專案行動版卡片 | `src/views/ProjectManagement.vue` (project-card-list) | - | 手機螢幕顯示卡片式專案資訊 |
| 建立專案 | `src/views/ProjectManagement.vue` (saveProject) | `backend/app/api/projects.py` (create_project) | 建立新專案 |
| 更新專案 | `src/views/ProjectManagement.vue` (editProject) | `backend/app/api/projects.py` (update_project) | 更新專案資訊 |
| 刪除專案 | `src/views/ProjectManagement.vue` (deleteProject) | `backend/app/api/projects.py` (delete_project) | 刪除專案 |
| 專案資料驗證 | - | `backend/app/schemas/project.py` | Pydantic 驗證模型 |

#### 1.2 專案狀態管理

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 狀態顯示 | `src/views/ProjectManagement.vue` (getStatusType) | - | 狀態標籤樣式 |
| 狀態選擇 | `src/views/ProjectManagement.vue` (projectForm.status) | `backend/app/schemas/project.py` | 狀態選項 |

### 2. 作業活動管理

#### 2.1 作業活動 CRUD

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 作業列表 | `src/components/ActivityTable.vue` (loadActivities) | `backend/app/api/activities.py` (get_activities) | 取得專案的所有作業 |
| 手機版作業卡片 | `src/components/ActivityTable.vue` (mobile-activity-list) | - | 小螢幕改用卡片式呈現並支援編輯 |
| 作業列表欄位顯示 | `src/components/ActivityTable.vue` (table columns) | - | 顯示正常/趕工工期與成本欄位 |
| 建立作業 | `src/components/ActivityTable.vue` (saveActivity) | `backend/app/api/activities.py` (create_activity) | 建立新作業 |
| CSV 批次匯入作業 | `src/components/ActivityTable.vue` (handleImport) | `backend/app/api/activities.py` (create_activity) | 從 CSV 檔案批次建立作業 |
| CSV 模板下載 | `src/components/ActivityTable.vue` (downloadTemplate) | - | 下載作業匯入 CSV 範本 |
| 更新作業 | `src/components/ActivityTable.vue` (editActivity) | `backend/app/api/activities.py` (update_activity) | 更新作業資訊 |
| 刪除作業 | `src/components/ActivityTable.vue` (deleteActivity) | `backend/app/api/activities.py` (delete_activity) | 刪除作業 |
| 作業資料驗證 | `src/components/ActivityTable.vue` (rules) | `backend/app/schemas/activity.py` | 前後端驗證 |

#### 2.2 前置作業關係管理

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 設定前置作業 | `src/components/ActivityTable.vue` (predecessor_ids) | `backend/app/api/activities.py` (create_activity) | 建立前置關係 |
| 查詢前置作業 | `src/components/ActivityTable.vue` (getPredecessors) | `backend/app/api/activities.py` (get_predecessors) | 取得作業的前置作業 |
| 前置關係儲存 | - | `backend/app/api/activities.py` | 儲存到 activity_precedences 表 |

#### 2.3 資料驗證邏輯

| 驗證項目 | 前端檔案 | 後端檔案 | 說明 |
|---------|---------|---------|------|
| 趕工工期 ≤ 正常工期 | `src/components/ActivityTable.vue` (saveActivity) | `backend/app/schemas/activity.py` (validate_crash_duration) | 驗證趕工工期 |
| 趕工成本 ≥ 正常成本 | `src/components/ActivityTable.vue` (saveActivity) | `backend/app/schemas/activity.py` (validate_crash_cost) | 驗證趕工成本 |

### 3. 投標最佳化決策

#### 3.1 決策模式

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 模式選擇 | `src/views/BiddingOptimization.vue` (optimizationForm.mode) | `backend/app/schemas/optimization.py` | 決策模式選擇 |
| 模式一：預算→工期 | `src/views/BiddingOptimization.vue` | `backend/app/models/bidding_optimizer.py` (solve_budget_to_duration) | 給定預算求最短工期 |
| 模式二：工期→成本 | `src/views/BiddingOptimization.vue` | `backend/app/models/bidding_optimizer.py` (solve_duration_to_cost) | 給定工期求最低成本 |

#### 3.2 MILP 模型實作

| 功能 | 檔案 | 說明 |
|------|------|------|
| 模型初始化 | `backend/app/models/bidding_optimizer.py` (__init__) | 初始化優化器 |
| 決策變數定義 | `backend/app/models/bidding_optimizer.py` | x[i], y[i], T 變數 |
| 約束條件 | `backend/app/models/bidding_optimizer.py` | 前置約束、工期約束、預算約束 |
| 目標函數 | `backend/app/models/bidding_optimizer.py` | 最小化工期或成本 |
| 求解 | `backend/app/models/bidding_optimizer.py` | 使用 PuLP 求解 |

#### 3.3 優化計算 API

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| 執行優化 | `src/views/BiddingOptimization.vue` (runOptimization) | `backend/app/api/optimization.py` (optimize) | 執行優化計算並回傳結果與詳細數據 |
| 取得結果 | `src/views/ResultAnalysis.vue` (loadResult) | `backend/app/api/optimization.py` (get_optimization_result) | 取得優化結果及計算過程數據 |
| 優化數據模型 | - | `backend/app/schemas/optimization.py` (OptimizationData, ActivityInfo, PrecedenceInfo) | 定義優化輸入參數、作業資訊、前置關係的數據結構 |

#### 3.4 獎懲條款計算

| 功能 | 檔案 | 說明 |
|------|------|------|
| 違約金計算 | `backend/app/models/bidding_optimizer.py` | 計算逾期違約金 |
| 獎金計算 | `backend/app/models/bidding_optimizer.py` | 計算提前獎金 |
| 總成本計算 | `backend/app/models/bidding_optimizer.py` | 含獎懲的總成本 |

### 4. 結果分析與視覺化

#### 4.1 結果展示

| 功能 | 前端檔案 | 說明 |
|------|---------|------|
| 結果摘要 | `src/views/ResultAnalysis.vue` | 顯示最優工期、成本、獎懲 |
| 作業排程表 | `src/views/ResultAnalysis.vue` | 詳細的作業排程資訊 |
| 最佳化計算過程說明 | `src/components/OptimizationProcess.vue` | 詳細的 MILP 數學模型與計算流程 |

#### 4.2 圖表視覺化

| 功能 | 前端檔案 | 說明 |
|------|---------|------|
| 甘特圖 | `src/components/GanttChart.vue` | 使用 ECharts 繪製甘特圖 |
| 成本分析圖 | `src/components/CostChart.vue` | 使用 ECharts 繪製成本分析 |

#### 4.3 圖表資料處理

| 功能 | 檔案 | 說明 |
|------|------|------|
| 甘特圖資料準備 | `src/components/GanttChart.vue` (chartOption) | 準備甘特圖資料 |
| 成本圖資料準備 | `src/components/CostChart.vue` (chartOption) | 準備成本分析資料 |

#### 4.4 最佳化計算過程展示

| 功能 | 前端檔案 | 後端檔案 | 說明 |
|------|---------|---------|------|
| MILP 數學模型 | `src/components/OptimizationProcess.vue` | `backend/app/models/bidding_optimizer.py` | 顯示完整的決策變數、目標函數、限制式 |
| 求解流程說明 | `src/components/OptimizationProcess.vue` | - | 一步一步展示從建模到求解的過程 |
| 最優解詳細結果 | `src/components/OptimizationProcess.vue` | - | 顯示所有決策變數的最優值 |
| 成本計算明細 | `src/components/OptimizationProcess.vue` | - | 具體數字的成本計算步驟 |
| 優化數據傳遞 | `src/views/ResultAnalysis.vue` | `backend/app/api/optimization.py` | 從後端取得並傳遞優化詳細數據 |

### 5. 報告輸出

#### 5.1 PDF 報告

| 功能 | 檔案 | 說明 |
|------|------|------|
| PDF 生成 | `src/utils/pdfGenerator.js` (exportToPDF) | 使用 jsPDF 生成 PDF |
| PDF 內容 | `src/utils/pdfGenerator.js` | 結果摘要、作業排程表 |

#### 5.2 Excel 報告

| 功能 | 檔案 | 說明 |
|------|------|------|
| Excel 生成 | `src/utils/excelGenerator.js` (exportToExcel) | 使用 xlsx 生成 Excel |
| Excel 工作表 | `src/utils/excelGenerator.js` | 結果摘要、作業排程 |

### 6. 資料庫操作

#### 6.1 Supabase 連接

| 功能 | 檔案 | 說明 |
|------|------|------|
| 後端連接 | `backend/app/utils/supabase_client.py` | Supabase 客戶端設定 |
| 前端連接 | `src/lib/supabase.ts` | Supabase 客戶端（前端） |

#### 6.2 資料庫 Schema

| 資料表 | 檔案 | 說明 |
|--------|------|------|
| projects | `supabase/migrations/001_initial_schema.sql` | 專案主表 |
| project_activities | `supabase/migrations/001_initial_schema.sql` | 作業活動表 |
| activity_precedences | `supabase/migrations/001_initial_schema.sql` | 前置關係表 |
| bidding_scenarios | `supabase/migrations/001_initial_schema.sql` | 投標情境表 |
| optimization_results | `supabase/migrations/001_initial_schema.sql` | 優化結果表 |
| activity_schedules | `supabase/migrations/001_initial_schema.sql` | 作業排程表 |

### 7. API 服務層

#### 7.1 API 封裝

| 功能 | 檔案 | 說明 |
|------|------|------|
| 專案 API | `src/services/api.js` (projectAPI) | 專案相關 API 封裝 |
| 作業 API | `src/services/api.js` (activityAPI) | 作業相關 API 封裝 |
| 優化 API | `src/services/api.js` (optimizationAPI) | 優化相關 API 封裝 |
| Axios 設定 | `src/services/api.js` | HTTP 客戶端設定 |

### 8. 路由與導航

| 功能 | 檔案 | 說明 |
|------|------|------|
| 路由配置 | `src/router/index.js` | Vue Router 路由定義 |
| 導航選單 | `src/App.vue` | 頂部導航選單 |

### 9. 工具函數

| 功能 | 檔案 | 說明 |
|------|------|------|
| 貨幣格式化 | 多個檔案 | formatCurrency 函數 |
| 日期格式化 | `src/views/ProjectManagement.vue` | formatDate 函數 |

## 關鍵模組說明

### MILP 模型模組

**檔案**：`backend/app/models/bidding_optimizer.py`

**核心類別**：
- `Activity`：作業活動類別，包含工期和成本資訊
- `BiddingOptimizer`：優化器類別，實作 MILP 模型

**關鍵方法**：
- `solve_budget_to_duration()`：模式一求解
- `solve_duration_to_cost()`：模式二求解

### 資料驗證模組

**檔案**：`backend/app/schemas/`

**核心模組**：
- `project.py`：專案資料驗證
- `activity.py`：作業活動資料驗證
- `optimization.py`：優化請求資料驗證

### API 路由模組

**檔案**：`backend/app/api/`

**核心模組**：
- `projects.py`：專案管理 API
- `activities.py`：作業管理 API
- `optimization.py`：優化計算 API

## 擴充指南

### 新增功能模組

1. **後端**：
   - 在 `backend/app/api/` 建立新的路由檔案
   - 在 `backend/app/schemas/` 建立對應的驗證模型
   - 在 `backend/main.py` 註冊路由

2. **前端**：
   - 在 `src/views/` 建立新的頁面元件
   - 在 `src/services/api.js` 新增 API 方法
   - 在 `src/router/index.js` 新增路由

3. **資料庫**：
   - 在 `supabase/migrations/` 建立新的 migration 檔案

---

**版本**：1.0.0  
**最後更新**：2024年

