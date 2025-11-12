"""
專案管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.utils.supabase_client import supabase

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects():
    """取得所有專案列表"""
    try:
        response = supabase.table("projects").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得專案列表失敗：{str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID):
    """取得單一專案詳情"""
    try:
        response = supabase.table("projects").select("*").eq("id", str(project_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="專案不存在")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得專案失敗：{str(e)}")


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """建立新專案"""
    try:
        response = supabase.table("projects").insert(project.model_dump()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建立專案失敗：{str(e)}")


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project: ProjectUpdate):
    """更新專案"""
    try:
        # 只更新提供的欄位
        update_data = project.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="沒有提供要更新的欄位")
        
        response = supabase.table("projects").update(update_data).eq("id", str(project_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="專案不存在")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新專案失敗：{str(e)}")


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: UUID):
    """刪除專案（會連帶刪除相關的作業和情境）"""
    try:
        response = supabase.table("projects").delete().eq("id", str(project_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="專案不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除專案失敗：{str(e)}")

