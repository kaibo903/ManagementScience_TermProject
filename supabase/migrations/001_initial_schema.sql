-- 營造廠決策分析平台 - 初始資料庫架構
-- 建立 SSOT (Single Source of Truth) 資料結構

-- 專案主表
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 作業活動表
CREATE TABLE IF NOT EXISTS project_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    normal_duration INTEGER NOT NULL,  -- 正常工期（天）
    normal_cost DECIMAL(15, 2) NOT NULL,  -- 正常成本
    crash_duration INTEGER NOT NULL,  -- 趕工工期（天）
    crash_cost DECIMAL(15, 2) NOT NULL,  -- 趕工成本
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_duration CHECK (crash_duration <= normal_duration),
    CONSTRAINT valid_cost CHECK (crash_cost >= normal_cost)
);

-- 作業前置關係表（多對多）
CREATE TABLE IF NOT EXISTS activity_precedences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES project_activities(id) ON DELETE CASCADE,
    predecessor_id UUID NOT NULL REFERENCES project_activities(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT no_self_precedence CHECK (activity_id != predecessor_id),
    CONSTRAINT unique_precedence UNIQUE (activity_id, predecessor_id)
);

-- 投標情境表
CREATE TABLE IF NOT EXISTS bidding_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    mode VARCHAR(50) NOT NULL,  -- 'budget_to_duration' 或 'duration_to_cost'
    budget_constraint DECIMAL(15, 2),  -- 預算約束（模式一）
    duration_constraint INTEGER,  -- 工期約束（模式二）
    penalty_rate DECIMAL(5, 4) DEFAULT 0.0,  -- 逾期違約金率（每日）
    bonus_rate DECIMAL(5, 4) DEFAULT 0.0,  -- 趕工獎金率（每日）
    target_duration INTEGER,  -- 目標工期（用於計算獎懲）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_mode CHECK (mode IN ('budget_to_duration', 'duration_to_cost'))
);

-- 優化結果表
CREATE TABLE IF NOT EXISTS optimization_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES bidding_scenarios(id) ON DELETE CASCADE,
    optimal_duration INTEGER NOT NULL,  -- 最優工期（天）
    optimal_cost DECIMAL(15, 2) NOT NULL,  -- 最優成本
    penalty_amount DECIMAL(15, 2) DEFAULT 0.0,  -- 違約金金額
    bonus_amount DECIMAL(15, 2) DEFAULT 0.0,  -- 獎金金額
    total_cost DECIMAL(15, 2) NOT NULL,  -- 總成本（含獎懲）
    calculation_time DECIMAL(10, 3),  -- 計算時間（秒）
    status VARCHAR(50) DEFAULT 'success',  -- 'success', 'infeasible', 'error'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 作業排程表
CREATE TABLE IF NOT EXISTS activity_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    result_id UUID NOT NULL REFERENCES optimization_results(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES project_activities(id) ON DELETE CASCADE,
    start_time INTEGER NOT NULL,  -- 開始時間（天）
    end_time INTEGER NOT NULL,  -- 結束時間（天）
    is_crashed BOOLEAN DEFAULT FALSE,  -- 是否趕工
    duration INTEGER NOT NULL,  -- 實際工期
    cost DECIMAL(15, 2) NOT NULL,  -- 實際成本
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_schedule CHECK (end_time >= start_time)
);

-- 建立索引以提升查詢效能
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_activities_project ON project_activities(project_id);
CREATE INDEX IF NOT EXISTS idx_precedences_activity ON activity_precedences(activity_id);
CREATE INDEX IF NOT EXISTS idx_precedences_predecessor ON activity_precedences(predecessor_id);
CREATE INDEX IF NOT EXISTS idx_scenarios_project ON bidding_scenarios(project_id);
CREATE INDEX IF NOT EXISTS idx_results_scenario ON optimization_results(scenario_id);
CREATE INDEX IF NOT EXISTS idx_schedules_result ON activity_schedules(result_id);
CREATE INDEX IF NOT EXISTS idx_schedules_activity ON activity_schedules(activity_id);

-- 建立更新時間觸發器函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為需要自動更新時間的表格建立觸發器
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON project_activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON bidding_scenarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

