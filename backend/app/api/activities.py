"""
作業活動管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.utils.supabase_client import supabase

router = APIRouter()


@router.get("/projects/{project_id}/activities", response_model=List[ActivityResponse])
async def get_activities(project_id: UUID):
    """取得專案的所有作業活動"""
    try:
        response = supabase.table("project_activities").select("*").eq("project_id", str(project_id)).order("created_at").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得作業列表失敗：{str(e)}")


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(activity_id: UUID):
    """取得單一作業活動詳情"""
    try:
        response = supabase.table("project_activities").select("*").eq("id", str(activity_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="作業不存在")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得作業失敗：{str(e)}")


@router.post("/projects/{project_id}/activities", response_model=ActivityResponse, status_code=201)
async def create_activity(project_id: UUID, activity: ActivityCreate):
    """建立新作業活動"""
    try:
        # 驗證專案是否存在
        project_check = supabase.table("projects").select("id").eq("id", str(project_id)).execute()
        if not project_check.data:
            raise HTTPException(status_code=404, detail="專案不存在")
        
        # 建立作業活動
        activity_data = activity.model_dump(exclude={'predecessor_ids'})
        activity_data['project_id'] = str(project_id)
        
        response = supabase.table("project_activities").insert(activity_data).execute()
        activity_id = response.data[0]['id']
        
        # 建立前置關係
        if activity.predecessor_ids:
            precedences = [
                {"activity_id": str(activity_id), "predecessor_id": str(pred_id)}
                for pred_id in activity.predecessor_ids
            ]
            supabase.table("activity_precedences").insert(precedences).execute()
        
        # 重新查詢以取得完整資料
        full_response = supabase.table("project_activities").select("*").eq("id", activity_id).execute()
        return full_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建立作業失敗：{str(e)}")


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(activity_id: UUID, activity: ActivityUpdate):
    """更新作業活動"""
    try:
        # 只更新提供的欄位
        update_data = activity.model_dump(exclude_unset=True, exclude={'predecessor_ids'})
        
        if update_data:
            response = supabase.table("project_activities").update(update_data).eq("id", str(activity_id)).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="作業不存在")
        
        # 更新前置關係
        if activity.predecessor_ids is not None:
            # 刪除舊的前置關係
            supabase.table("activity_precedences").delete().eq("activity_id", str(activity_id)).execute()
            
            # 建立新的前置關係
            if activity.predecessor_ids:
                precedences = [
                    {"activity_id": str(activity_id), "predecessor_id": str(pred_id)}
                    for pred_id in activity.predecessor_ids
                ]
                supabase.table("activity_precedences").insert(precedences).execute()
        
        # 重新查詢以取得完整資料
        full_response = supabase.table("project_activities").select("*").eq("id", str(activity_id)).execute()
        return full_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新作業失敗：{str(e)}")


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(activity_id: UUID):
    """刪除作業活動（會連帶刪除相關的前置關係）"""
    try:
        response = supabase.table("project_activities").delete().eq("id", str(activity_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="作業不存在")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除作業失敗：{str(e)}")


@router.get("/activities/{activity_id}/predecessors", response_model=List[ActivityResponse])
async def get_predecessors(activity_id: UUID):
    """取得作業的前置作業列表"""
    try:
        # 查詢前置關係
        precedence_response = supabase.table("activity_precedences").select("predecessor_id").eq("activity_id", str(activity_id)).execute()
        predecessor_ids = [p['predecessor_id'] for p in precedence_response.data]
        
        if not predecessor_ids:
            return []
        
        # 查詢前置作業詳情
        activities_response = supabase.table("project_activities").select("*").in_("id", predecessor_ids).execute()
        return activities_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得前置作業失敗：{str(e)}")

