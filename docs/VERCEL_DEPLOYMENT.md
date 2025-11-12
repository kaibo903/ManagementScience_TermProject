# Vercel 前端部署指南

本文件說明如何將前端應用程式部署到 Vercel 平台。

## 前置需求

1. GitHub 帳號
2. Vercel 帳號（可使用 GitHub 登入）
3. 後端已部署到 Railway（取得後端 URL）

## 部署步驟

### 步驟 1：確認配置文件

確認以下文件已存在：
- ✅ `vercel.json` - Vercel 部署配置
- ✅ `package.json` - 前端依賴和建置腳本
- ✅ `vite.config.js` - Vite 配置

### 步驟 2：上傳代碼到 GitHub

```bash
# 在專案根目錄執行
git add .
git commit -m "準備 Vercel 部署：新增 vercel.json"
git push origin main
```

### 步驟 3：在 Vercel 建立專案

1. **前往 Vercel**：
   - 開啟瀏覽器，前往 https://vercel.com
   - 使用 GitHub 帳號登入

2. **建立新專案**：
   - 點擊右上角 "Add New..." 按鈕
   - 選擇 "Project"
   - 選擇您的 GitHub 倉庫
   - 如果第一次使用，需要授權 Vercel 存取 GitHub 倉庫

3. **設定專案配置**：
   Vercel 會自動偵測 Vite 專案，確認以下設定：
   - **Framework Preset**: Vite（自動偵測）
   - **Root Directory**: `./`（根目錄）
   - **Build Command**: `npm run build`（自動偵測）
   - **Output Directory**: `dist`（自動偵測）
   - **Install Command**: `npm install`（自動偵測）

4. **部署**：
   - 點擊 "Deploy" 按鈕
   - Vercel 會開始建置和部署

### 步驟 4：設定環境變數

**重要**：必須設定環境變數，前端才能連接到後端 API。

1. **進入專案設定**：
   - 在 Vercel 專案頁面，點擊 "Settings" 標籤
   - 點擊左側選單的 "Environment Variables"

2. **新增環境變數**：
   - 點擊 "Add New" 按鈕
   - 新增以下變數：
   
   | Name | Value | Environment |
   |------|-------|-------------|
   | `VITE_API_BASE_URL` | `https://term-project-production.up.railway.app` | Production, Preview, Development |
   
   **注意**：
   - 將 `term-project-production.up.railway.app` 替換為您的實際 Railway 後端 URL
   - 建議同時勾選 Production、Preview 和 Development 三個環境
   - 點擊 "Save" 儲存

3. **重新部署**：
   - 環境變數設定後，前往 "Deployments" 標籤
   - 點擊最新部署右側的 "..." 選單
   - 選擇 "Redeploy"
   - 或點擊 "Redeploy" 按鈕
   - 等待部署完成

### 步驟 5：更新 Railway 的 CORS 設定

讓後端允許前端訪問：

1. **前往 Railway 專案**：
   - 開啟 https://railway.app
   - 選擇您的後端專案

2. **設定環境變數**：
   - 點擊 "Variables" 標籤
   - 點擊 "New Variable"
   - 新增或更新：
     - **Name**: `FRONTEND_URL`
     - **Value**: 您的 Vercel URL（例如：`https://your-app.vercel.app`）
   - 點擊 "Add"

3. **等待重新部署**：
   - Railway 會自動偵測環境變數變更並重新部署
   - 等待部署完成（約 1-2 分鐘）

### 步驟 6：測試部署

1. **訪問前端**：
   - 在 Vercel 專案頁面，您會看到部署的 URL
   - 例如：`https://your-app.vercel.app`
   - 在瀏覽器訪問這個 URL

2. **測試功能**：
   - ✅ 確認前端頁面正常載入
   - ✅ 測試專案管理功能
   - ✅ 測試建立/編輯專案
   - ✅ 確認 API 連線正常（檢查瀏覽器開發者工具的 Network 標籤）

3. **檢查錯誤**：
   - 開啟瀏覽器開發者工具（F12）
   - 查看 Console 標籤是否有錯誤
   - 查看 Network 標籤確認 API 請求是否成功

## 部署完成檢查清單

- [ ] 代碼已推送到 GitHub
- [ ] Vercel 專案已建立並連接 GitHub 倉庫
- [ ] 環境變數 `VITE_API_BASE_URL` 已設定
- [ ] 前端已成功部署
- [ ] Railway 的 `FRONTEND_URL` 環境變數已設定
- [ ] 前端可以正常訪問
- [ ] API 連線正常（無 CORS 錯誤）

## 常見問題排除

### Q: 部署後顯示空白頁面？

**可能原因**：
1. `vercel.json` 中的 `rewrites` 設定不正確
2. 路由配置問題

**解決方法**：
1. 確認 `vercel.json` 文件存在且內容正確
2. 檢查 Vercel 部署日誌是否有錯誤
3. 確認 Vue Router 使用 `createWebHistory`（已在 `src/router/index.js` 中確認）
4. 檢查瀏覽器控制台是否有 JavaScript 錯誤

### Q: API 請求失敗，顯示 CORS 錯誤？

**可能原因**：
1. Railway 的 `FRONTEND_URL` 環境變數未設定或設定錯誤
2. 後端 CORS 設定不正確

**解決方法**：
1. 確認 Railway 的 `FRONTEND_URL` 環境變數已設定為正確的 Vercel URL
2. 確認後端已重新部署
3. 檢查 `backend/main.py` 中的 CORS 設定
4. 確認前端 URL 格式正確（包含 `https://`）

### Q: 環境變數未生效？

**可能原因**：
1. 環境變數設定後未重新部署
2. 環境變數名稱錯誤（必須以 `VITE_` 開頭）

**解決方法**：
1. 確認環境變數名稱是 `VITE_API_BASE_URL`（不是 `API_BASE_URL`）
2. 設定環境變數後，必須重新部署
3. 檢查 Vercel 部署日誌確認環境變數已載入

### Q: 路由無法正常運作（刷新頁面顯示 404）？

**可能原因**：
1. `vercel.json` 中的 `rewrites` 設定不正確

**解決方法**：
1. 確認 `vercel.json` 文件存在
2. 確認 `rewrites` 設定正確：
   ```json
   "rewrites": [
     {
       "source": "/(.*)",
       "destination": "/index.html"
     }
   ]
   ```
3. 重新部署

### Q: 建置失敗？

**可能原因**：
1. 依賴安裝失敗
2. 建置腳本錯誤

**解決方法**：
1. 檢查 Vercel 部署日誌中的錯誤訊息
2. 確認 `package.json` 中的依賴都正確
3. 嘗試在本地執行 `npm run build` 確認可以建置
4. 檢查 Node.js 版本（Vercel 通常使用 Node.js 18+）

## 自動部署

Vercel 會自動：
- 偵測推送到 GitHub 的變更
- 自動觸發新的部署
- 為每個 Pull Request 建立 Preview 部署

## 自訂域名（可選）

如果需要使用自訂域名：

1. 在 Vercel 專案頁面，點擊 "Settings"
2. 點擊 "Domains"
3. 輸入您的域名
4. 按照指示設定 DNS 記錄
5. 等待 DNS 傳播完成（通常幾分鐘到幾小時）

## 成本說明

Vercel 提供：
- **免費方案**：適合個人專案和小型應用
- **付費方案**：適合商業用途和大型應用

對於本專案，免費方案通常足夠使用。

## 相關文件

- [Railway 後端部署指南](./RAILWAY_DEPLOYMENT.md)
- [Supabase 資料庫設定](./DATABASE_SETUP.md)

