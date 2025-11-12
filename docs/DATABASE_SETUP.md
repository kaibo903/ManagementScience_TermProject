# 資料庫設定指南

## 在 Supabase 中建立資料表

### 方法一：使用 Supabase Dashboard（推薦）

1. **登入 Supabase Dashboard**
   - 前往 https://app.supabase.com
   - 選擇您的專案

2. **開啟 SQL Editor**
   - 在左側選單中點擊「SQL Editor」
   - 點擊「New query」

3. **執行遷移文件**
   - 複製 `supabase/migrations/001_initial_schema.sql` 的完整內容
   - 貼上到 SQL Editor 中
   - 點擊「Run」或按 `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

4. **驗證資料表已建立**
   - 在左側選單中點擊「Table Editor」
   - 確認以下資料表已建立：
     - `projects`
     - `project_activities`
     - `activity_precedences`
     - `bidding_scenarios`
     - `optimization_results`
     - `activity_schedules`

### 方法二：使用 Supabase CLI（進階）

如果您已安裝 Supabase CLI：

```bash
supabase db push
```

## 設定 Row Level Security (RLS)

如果需要啟用 RLS，請在 SQL Editor 中執行：

```sql
-- 啟用 RLS（如果需要）
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_precedences ENABLE ROW LEVEL SECURITY;
ALTER TABLE bidding_scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_schedules ENABLE ROW LEVEL SECURITY;

-- 建立允許所有操作的策略（僅用於開發，生產環境應設定更嚴格的策略）
CREATE POLICY "Allow all operations" ON projects FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON project_activities FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON activity_precedences FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON bidding_scenarios FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON optimization_results FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON activity_schedules FOR ALL USING (true);
```

**注意**：如果使用 Service Role Key，通常不需要啟用 RLS，因為 Service Role Key 會繞過 RLS 檢查。

## 驗證設定

執行以下 SQL 查詢來驗證資料表是否正確建立：

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'projects',
    'project_activities',
    'activity_precedences',
    'bidding_scenarios',
    'optimization_results',
    'activity_schedules'
)
ORDER BY table_name;
```

應該會返回 6 個資料表名稱。

