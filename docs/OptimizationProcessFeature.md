# 最佳化計算過程展示功能

## 功能概述

本功能在「優化結果分析」頁面中新增了詳細的最佳化計算過程說明，讓使用者能夠完整了解系統如何使用混合整數線性規劃（MILP）求解營造專案的最佳化決策問題。

## 更新內容

### 1. 新增組件

#### `src/components/OptimizationProcess.vue`

一個全新的 Vue 組件，負責展示完整的最佳化計算過程，包含：

**主要區塊：**

1. **問題類型說明**
   - 說明 MILP 的定義與應用

2. **優化模式**
   - 顯示當前使用的模式（模式一：預算→工期 或 模式二：工期→成本）
   - 展示所有輸入約束條件（預算/工期、間接成本、目標工期等）

3. **MILP 數學模型**
   - **決策變數**：詳細列出 x_i（開始時間）、y_i（是否趕工）、T（總工期）
   - **目標函數**：根據模式顯示完整的數學公式，並標註實際計算值
   - **限制式**：
     - 前置作業約束（含實際前置關係範例）
     - 工期定義約束
     - 預算/工期約束
     - 變數範圍約束

4. **求解過程**
   - 6 個步驟詳細說明從建模到求解的完整流程
   - 包含實際求解時間

5. **最優解詳細結果**
   - 所有成本指標（直接成本、間接成本、違約金、趕工獎金、總成本）
   - 作業趕工決策表格（顯示每個作業的 x_i*, y_i* 值）
   - 成本計算明細（一步一步的算式展開）

6. **最優性保證**
   - 說明全局最優解的保證
   - 可行性驗證
   - 目標值最優性說明

### 2. 後端 API 增強

#### `backend/app/schemas/optimization.py`

新增三個數據模型：

```python
class ActivityInfo(BaseModel):
    """作業資訊模型"""
    id: str
    name: str
    normal_duration: int
    normal_cost: Decimal
    crash_duration: int
    crash_cost: Decimal

class PrecedenceInfo(BaseModel):
    """前置關係模型"""
    successor: str
    predecessor: str

class OptimizationData(BaseModel):
    """優化輸入參數模型"""
    mode: str
    budget_constraint: Optional[Decimal]
    duration_constraint: Optional[int]
    indirect_cost: Decimal
    penalty_type: str
    penalty_amount: Optional[Decimal]
    penalty_rate: Optional[Decimal]
    contract_amount: Decimal
    contract_duration: Optional[int]
    target_duration: Optional[int]
```

並擴展 `OptimizationResult` 模型：

```python
class OptimizationResult(BaseModel):
    # ... 原有欄位 ...
    # 新增：計算過程所需的詳細數據
    optimization_data: Optional[OptimizationData] = None
    activities: Optional[List[ActivityInfo]] = None
    precedences: Optional[List[PrecedenceInfo]] = None
```

#### `backend/app/api/optimization.py`

修改兩個端點以返回詳細數據：

1. **POST `/optimize`**
   - 在返回結果中新增 `optimization_data`、`activities`、`precedences`
   - 讓前端能夠取得建立 MILP 模型所需的所有輸入數據

2. **GET `/scenarios/{scenario_id}/results`**
   - 從資料庫讀取投標情境（`bidding_scenarios`）
   - 讀取專案的所有作業活動（`project_activities`）
   - 讀取前置關係（`activity_precedences`）
   - 組裝完整的優化數據並返回

### 3. 前端頁面整合

#### `src/views/ResultAnalysis.vue`

- 匯入 `OptimizationProcess` 組件
- 新增 `hasOptimizationData` 計算屬性檢查數據完整性
- 在作業排程明細表格後方加入最佳化計算過程說明區塊
- 傳遞 `result`、`optimization_data`、`activities`、`precedences` 給組件

#### `src/views/BiddingOptimization.vue`

- 簡化原有的計算過程說明
- 改為「最佳化結果摘要」，只顯示核心信息
- 新增提示框引導使用者前往結果分析頁面查看完整計算過程

## 技術特點

### 1. 數學公式展示

- 使用 HTML sub/sup 標籤顯示下標與上標（如 x<sub>i</sub>、C<sub>直接</sub>）
- 清晰的公式佈局與數學符號
- 實際計算值與公式並列顯示

### 2. 數據驗證

- 所有數據都經過 Pydantic 驗證
- 前端在缺少數據時不顯示組件，避免錯誤

### 3. 用戶體驗

- 六大區塊清晰分隔
- 使用顏色區分不同類型的信息框（結果、步驟、最優性）
- 表格與卡片結合，便於閱讀
- 圖示與文字搭配，提升理解度

### 4. 無印風格

- 所有卡片與元件均使用 `border-radius: 0`
- 統一的邊框、背景色與間距
- 極簡的配色方案

## 使用流程

1. 使用者在「進度成本最佳化」頁面設定參數並執行計算
2. 計算完成後，點擊「查看詳細結果與圖表」按鈕
3. 進入「優化結果分析」頁面
4. 頁面顯示：
   - 結果摘要卡片
   - 甘特圖
   - 成本分析圖
   - 作業排程明細表
   - **最佳化計算過程說明**（新增）

## 實際效果

使用者可以看到：

1. **完整的 MILP 模型**
   - 例如：「min Z = C_直接 + C_間接 + P - B」
   - 「x_j ≥ x_i + d_i, ∀ (i, j) ∈ 前置關係」

2. **具體數字的計算範例**
   - 「直接成本 = $500,000 + $300,000 + $200,000 = $1,000,000」
   - 「間接成本 = $10,000 × 50 天 = $500,000」
   - 「總成本 = $1,000,000 + $500,000 + $0 - $50,000 = $1,450,000」

3. **每個作業的決策**
   - 作業 A：x_A* = 0，y_A* = 0（第 0 天開始，正常施工）
   - 作業 B：x_B* = 10，y_B* = 1（第 10 天開始，趕工）

4. **求解保證**
   - 「CBC 求解器使用精確演算法，保證找到的解為全局最優解」

## 檔案清單

### 新增檔案
- `src/components/OptimizationProcess.vue`
- `docs/OptimizationProcessFeature.md`（本文件）

### 修改檔案
- `backend/app/schemas/optimization.py`
- `backend/app/api/optimization.py`
- `src/views/ResultAnalysis.vue`
- `src/views/BiddingOptimization.vue`
- `docs/FeatureCodeMap.md`

## 未來擴展建議

1. **進階數學說明**
   - 可以新增一個摺疊區域，顯示完整的數學式（LaTeX 格式）
   - 提供符號定義表

2. **求解日誌**
   - 記錄求解器的中間步驟（如果 PuLP 支援）
   - 顯示迭代次數與分支數

3. **敏感度分析**
   - 顯示參數變化對結果的影響
   - 例如「如果預算增加 10%，工期可縮短多少？」

4. **互動式探索**
   - 讓使用者點選某個限制式，高亮相關的作業
   - 點選某個決策變數，顯示其在模型中的所有出現位置

---

**版本**：1.0.0  
**建立日期**：2024 年 12 月  
**作者**：AI Assistant

