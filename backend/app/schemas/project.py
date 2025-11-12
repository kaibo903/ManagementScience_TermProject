"""
專案相關的 Pydantic 資料驗證模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProjectBase(BaseModel):
    """專案基礎模型"""
    name: str = Field(..., description="專案名稱", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="專案描述")
    status: str = Field("draft", description="專案狀態")


class ProjectCreate(ProjectBase):
    """建立專案請求模型"""
    pass


class ProjectUpdate(BaseModel):
    """更新專案請求模型"""
    name: Optional[str] = Field(None, description="專案名稱", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="專案描述")
    status: Optional[str] = Field(None, description="專案狀態")


class ProjectResponse(ProjectBase):
    """專案回應模型"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

