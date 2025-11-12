# Railway 後端部署指南

本文件說明如何將後端 API 部署到 Railway 平台。

## 前置需求

1. GitHub 帳號
2. Railway 帳號（可使用 GitHub 登入）
3. Supabase 專案（已設定資料庫）

## 部署步驟

### 步驟 1：準備代碼

確認以下文件已存在：
- ✅ `backend/main.py` - FastAPI 應用程式
- ✅ `backend/Procfile` - Railway 啟動命令
- ✅ `backend/requirements.txt` - Python 依賴
- ✅ `backend/.gitignore` - Git 忽略文件

### 步驟 2：上傳代碼到 GitHub

```bash
# 在專案根目錄執行
git add .
git commit -m "準備 Railway 部署"
git push origin main
```

### 步驟 3：在 Railway 建立專案

1. 前往 https://railway.app
2. 使用 GitHub 帳號登入
3. 點擊 **"New Project"**
4. 選擇 **"Deploy from GitHub repo"**
5. 選擇您的專案倉庫
6. Railway 會自動偵測並開始部署

### 步驟 4：設定部署配置

在 Railway 專案設定中：

1. **設定 Root Directory**：
   - 前往專案設定 → Settings
   - 找到 "Root Directory"
   - 設定為：`backend`

2. **確認 Build Command**（通常自動偵測）：
   ```
   pip install -r requirements.txt
   ```

3. **確認 Start Command**（從 Procfile 讀取）：
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### 步驟 5：設定環境變數

在 Railway 專案中，前往 **Variables** 標籤，新增以下環境變數：

| 變數名稱 | 說明 | 取得方式 |
|---------|------|---------|
| `SUPABASE_URL` | Supabase 專案 URL | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | Supabase Dashboard → Settings → API → service_role key |
| `FRONTEND_URL` | 前端部署 URL（可選） | 例如：`https://your-app.vercel.app` |

**重要**：如果有多個前端 URL，用逗號分隔：
```
FRONTEND_URL=https://your-app.vercel.app,https://another-domain.com
```

### 步驟 6：取得部署 URL

1. 部署完成後，Railway 會自動生成一個 URL
2. 前往 **Settings** → **Domains**
3. 可以：
   - 使用預設的 Railway 域名（例如：`your-app.railway.app`）
   - 或設定自訂域名

### 步驟 7：測試部署

1. 訪問 `https://your-app.railway.app/` 應該看到：
   ```json
   {
     "message": "營造廠決策分析平台 API",
     "status": "running"
   }
   ```

2. 訪問 `https://your-app.railway.app/docs` 查看 API 文件

3. 訪問 `https://your-app.railway.app/health` 檢查健康狀態

### 步驟 8：更新前端配置

在前端的 Vercel 環境變數中，設定：

```
VITE_API_BASE_URL=https://your-app.railway.app
```

## 常見問題

### Q: 部署失敗，顯示 "Module not found"

**A**: 確認 `requirements.txt` 包含所有必要的依賴，並且在 Railway 的 Build Command 中執行 `pip install -r requirements.txt`。

### Q: 無法連接到 Supabase

**A**: 
1. 確認環境變數 `SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY` 已正確設定
2. 確認使用的是 `service_role` key，不是 `anon` key
3. 檢查 Supabase 專案的網路設定是否允許 Railway 的 IP

### Q: CORS 錯誤

**A**: 
1. 確認 `FRONTEND_URL` 環境變數已設定為正確的前端 URL
2. 檢查 `backend/main.py` 中的 CORS 設定
3. 如果有多個前端 URL，用逗號分隔

### Q: 如何查看日誌？

**A**: 在 Railway 專案中，前往 **Deployments** 標籤，點擊最新的部署，即可查看日誌。

### Q: 如何重新部署？

**A**: 
- 自動：每次推送到 GitHub 的 main 分支會自動觸發部署
- 手動：在 Railway 專案中點擊 **"Redeploy"**

## 成本說明

Railway 提供：
- **免費額度**：每月 $5 美元額度
- **付費方案**：按使用量計費，超出免費額度後開始收費

對於小型專案，免費額度通常足夠使用。

## 下一步

部署完成後：
1. ✅ 測試所有 API 端點
2. ✅ 更新前端環境變數
3. ✅ 部署前端到 Vercel
4. ✅ 進行端到端測試

## 相關文件

- [Supabase 資料庫設定](./DATABASE_SETUP.md)
- [前端 Vercel 部署](./VERCEL_DEPLOYMENT.md)（待建立）

