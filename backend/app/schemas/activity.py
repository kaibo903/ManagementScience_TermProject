"""
作業活動相關的 Pydantic 資料驗證模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ActivityBase(BaseModel):
    """作業活動基礎模型"""
    name: str = Field(..., description="作業名稱", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="作業描述")
    normal_duration: int = Field(..., description="正常工期（天）", gt=0)
    normal_cost: Decimal = Field(..., description="正常成本", gt=0)
    crash_duration: int = Field(..., description="趕工工期（天）", gt=0)
    crash_cost: Decimal = Field(..., description="趕工成本", gt=0)

    @field_validator('crash_duration')
    @classmethod
    def validate_crash_duration(cls, v, info):
        """驗證趕工工期必須小於等於正常工期"""
        if 'normal_duration' in info.data and v > info.data['normal_duration']:
            raise ValueError('趕工工期必須小於等於正常工期')
        return v

    @field_validator('crash_cost')
    @classmethod
    def validate_crash_cost(cls, v, info):
        """驗證趕工成本必須大於等於正常成本"""
        if 'normal_cost' in info.data and v < info.data['normal_cost']:
            raise ValueError('趕工成本必須大於等於正常成本')
        return v


class ActivityCreate(ActivityBase):
    """建立作業活動請求模型"""
    project_id: UUID = Field(..., description="專案ID")
    predecessor_ids: Optional[List[UUID]] = Field(default=[], description="前置作業ID列表")


class ActivityUpdate(BaseModel):
    """更新作業活動請求模型"""
    name: Optional[str] = Field(None, description="作業名稱", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="作業描述")
    normal_duration: Optional[int] = Field(None, description="正常工期（天）", gt=0)
    normal_cost: Optional[Decimal] = Field(None, description="正常成本", gt=0)
    crash_duration: Optional[int] = Field(None, description="趕工工期（天）", gt=0)
    crash_cost: Optional[Decimal] = Field(None, description="趕工成本", gt=0)
    predecessor_ids: Optional[List[UUID]] = Field(None, description="前置作業ID列表")


class ActivityResponse(ActivityBase):
    """作業活動回應模型"""
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

