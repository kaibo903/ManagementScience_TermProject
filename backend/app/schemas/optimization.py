"""
優化計算相關的 Pydantic 資料驗證模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class OptimizationRequest(BaseModel):
    """優化計算請求模型"""
    project_id: UUID = Field(..., description="專案ID")
    mode: str = Field(..., description="決策模式：budget_to_duration 或 duration_to_cost")
    budget_constraint: Optional[Decimal] = Field(None, description="預算約束（模式一）", gt=0)
    duration_constraint: Optional[int] = Field(None, description="工期約束（模式二）", gt=0)
    indirect_cost: Optional[Decimal] = Field(0.0, description="間接成本（每日）", ge=0)
    # 違約金計算方式
    penalty_type: str = Field('rate', description="違約金計算方式：'fixed' 定額 或 'rate' 比率")
    penalty_amount: Optional[Decimal] = Field(None, description="定額違約金（每日，當 penalty_type='fixed' 時使用）", ge=0)
    penalty_rate: Optional[Decimal] = Field(None, description="比率違約金（每日，契約金額比率，當 penalty_type='rate' 時使用）", ge=0)
    contract_amount: Optional[Decimal] = Field(0.0, description="契約決標總價（用於計算違約金上限和趕工費用）", ge=0)
    contract_duration: Optional[int] = Field(None, description="契約工期（天，用於計算趕工費用）", gt=0)
    target_duration: Optional[int] = Field(None, description="目標工期（用於計算獎懲）", gt=0)

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        """驗證決策模式"""
        if v not in ['budget_to_duration', 'duration_to_cost']:
            raise ValueError('決策模式必須是 budget_to_duration 或 duration_to_cost')
        return v
    
    @field_validator('penalty_type')
    @classmethod
    def validate_penalty_type(cls, v):
        """驗證違約金計算方式"""
        if v not in ['fixed', 'rate']:
            raise ValueError('違約金計算方式必須是 fixed（定額）或 rate（比率）')
        return v
    
    @field_validator('penalty_amount', 'penalty_rate')
    @classmethod
    def validate_penalty_params(cls, v, info):
        """驗證違約金參數"""
        penalty_type = info.data.get('penalty_type', 'rate')
        if penalty_type == 'fixed':
            if 'penalty_amount' in info.data and info.data['penalty_amount'] is None:
                raise ValueError('定額計算方式必須提供 penalty_amount（定額違約金）')
        elif penalty_type == 'rate':
            if 'penalty_rate' in info.data and info.data['penalty_rate'] is None:
                raise ValueError('比率計算方式必須提供 penalty_rate（違約金率）')
        return v

    @field_validator('budget_constraint', 'duration_constraint')
    @classmethod
    def validate_constraints(cls, v, info):
        """驗證約束條件"""
        mode = info.data.get('mode')
        if mode == 'budget_to_duration' and 'budget_constraint' in info.data:
            if info.data['budget_constraint'] is None:
                raise ValueError('模式一（預算→工期）必須提供預算約束')
        elif mode == 'duration_to_cost' and 'duration_constraint' in info.data:
            if info.data['duration_constraint'] is None:
                raise ValueError('模式二（工期→成本）必須提供工期約束')
        return v


class ActivitySchedule(BaseModel):
    """作業排程模型"""
    activity_id: UUID
    activity_name: str
    start_time: int
    end_time: int
    duration: int
    is_crashed: bool
    cost: Decimal


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


class OptimizationResult(BaseModel):
    """優化結果模型"""
    scenario_id: UUID
    result_id: UUID
    optimal_duration: int
    optimal_cost: Decimal
    indirect_cost: Decimal
    penalty_amount: Decimal
    bonus_amount: Decimal
    total_cost: Decimal
    calculation_time: Optional[float]
    status: str
    error_message: Optional[str]
    schedules: List[ActivitySchedule]
    created_at: datetime
    # 新增：計算過程所需的詳細數據
    optimization_data: Optional[OptimizationData] = None
    activities: Optional[List[ActivityInfo]] = None
    precedences: Optional[List[PrecedenceInfo]] = None

