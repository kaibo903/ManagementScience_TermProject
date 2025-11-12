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
    penalty_rate: Decimal = Field(0.0, description="逾期違約金率（每日）", ge=0)
    bonus_rate: Decimal = Field(0.0, description="趕工獎金率（每日）", ge=0)
    target_duration: Optional[int] = Field(None, description="目標工期（用於計算獎懲）", gt=0)

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        """驗證決策模式"""
        if v not in ['budget_to_duration', 'duration_to_cost']:
            raise ValueError('決策模式必須是 budget_to_duration 或 duration_to_cost')
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


class OptimizationResult(BaseModel):
    """優化結果模型"""
    scenario_id: UUID
    result_id: UUID
    optimal_duration: int
    optimal_cost: Decimal
    penalty_amount: Decimal
    bonus_amount: Decimal
    total_cost: Decimal
    calculation_time: Optional[float]
    status: str
    error_message: Optional[str]
    schedules: List[ActivitySchedule]
    created_at: datetime

