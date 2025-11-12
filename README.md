# 營造廠決策分析平台

本專案旨在建立以單一資料來源（SSOT）為核心的營造決策分析平台，首個核心模組為「投標最佳化決策系統」。

## 專案概述

營造廠決策分析平台是一個專為營造廠設計的決策支援系統，採用整數線性規劃（MILP）模型，協助使用者在投標階段快速獲得最優的工期與成本方案。

### 主要功能

- **專案管理**：建立與管理專案
- **作業活動管理**：定義專案的作業活動及其前置關係
- **投標優化計算**：支援兩種決策模式
  - 模式一：給定預算，求最短工期
  - 模式二：給定工期，求最低成本
- **結果分析**：查看優化結果、圖表視覺化
- **報告匯出**：匯出 PDF 或 Excel 報告

## 技術架構

### 前端
- Vue 3 + Vite
- Element Plus (UI 元件庫)
- ECharts (圖表庫)
- Axios (HTTP 客戶端)
- jsPDF + xlsx (報告生成)

### 後端
- FastAPI (Web 框架)
- PuLP (MILP 求解器)
- Pydantic (資料驗證)
- Supabase (資料庫)

## 快速開始

### 前置需求

- Node.js 18+ 
- Python 3.9+
- Supabase 專案

### 安裝步驟

#### 1. 安裝前端依賴

```bash
npm install
```

#### 2. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 設定環境變數

**前端**：建立 `.env` 檔案
```
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

**後端**：建立 `backend/.env` 檔案
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

#### 4. 設定資料庫

在 Supabase 中執行 `supabase/migrations/001_initial_schema.sql` 建立資料表。

#### 5. 啟動開發伺服器

**後端**：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**前端**：
```bash
npm run dev
```

## 專案結構

```
專案根目錄/
├── src/                    # 前端原始碼
│   ├── components/          # Vue 元件
│   ├── views/               # 頁面視圖
│   ├── services/            # API 服務層
│   ├── utils/               # 工具函數
│   └── router/              # 路由配置
├── backend/                 # 後端原始碼
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── models/          # MILP 模型
│   │   ├── schemas/         # 資料驗證
│   │   └── utils/           # 工具函數
│   └── main.py              # FastAPI 主程式
├── docs/                    # 專案文件
│   ├── PRD.md               # 產品需求文件
│   ├── UserManual.md        # 使用者手冊
│   ├── FeatureCodeMap.md    # 功能與程式碼對應表
│   └── ChatHistory.md       # 開發決策紀錄
└── supabase/
    └── migrations/          # 資料庫遷移腳本
```

## 文件

詳細文件請參考 `docs/` 目錄：

- [產品需求文件 (PRD)](docs/PRD.md)
- [使用者手冊](docs/UserManual.md)
- [功能與程式碼對應表](docs/FeatureCodeMap.md)
- [開發決策紀錄](docs/ChatHistory.md)

## 開發指南

### 程式碼規範

- 所有程式碼必須包含清晰、完整的繁體中文註解
- 使用一致的命名規範（駝峰式命名）
- 遵循 ESLint + Prettier 標準

### 新增功能

1. 在 `backend/app/api/` 建立新的路由檔案
2. 在 `src/views/` 建立對應的前端頁面
3. 更新路由配置
4. 更新文件

## 授權

本專案為學術專案，僅供學習與研究使用。

## 聯絡資訊

如有任何問題或建議，請聯繫專案維護者。
