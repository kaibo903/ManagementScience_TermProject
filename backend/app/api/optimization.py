"""
優化計算 API 路由
"""
from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.schemas.optimization import (
    OptimizationRequest, 
    OptimizationResult, 
    ActivitySchedule,
    ActivityInfo,
    PrecedenceInfo,
    OptimizationData
)
from app.models.bidding_optimizer import BiddingOptimizer, Activity
from app.utils.supabase_client import supabase
from decimal import Decimal
from datetime import datetime

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResult)
async def optimize(request: OptimizationRequest):
    """執行投標最佳化計算"""
    try:
        # 1. 取得專案的所有作業活動
        activities_response = supabase.table("project_activities").select("*").eq("project_id", str(request.project_id)).execute()
        if not activities_response.data:
            raise HTTPException(status_code=404, detail="專案沒有作業活動")
        
        activities_data = activities_response.data
        
        # 2. 取得前置關係
        activity_ids = [act['id'] for act in activities_data]
        precedences_response = supabase.table("activity_precedences").select("*").in_("activity_id", activity_ids).execute()
        precedences = [(p['activity_id'], p['predecessor_id']) for p in precedences_response.data]
        
        # 3. 建立 Activity 物件
        activities = [
            Activity(
                activity_id=act['id'],
                name=act['name'],
                normal_duration=act['normal_duration'],
                normal_cost=Decimal(str(act['normal_cost'])),
                crash_duration=act['crash_duration'],
                crash_cost=Decimal(str(act['crash_cost']))
            )
            for act in activities_data
        ]
        
        # 4. 處理可選參數，將 None 轉換為預設值
        indirect_cost = request.indirect_cost if request.indirect_cost is not None else Decimal('0.0')
        contract_amount = request.contract_amount if request.contract_amount is not None else Decimal('0.0')
        
        # 5. 建立優化器並求解
        optimizer = BiddingOptimizer(activities, precedences)
        
        if request.mode == 'budget_to_duration':
            if not request.budget_constraint:
                raise HTTPException(status_code=400, detail="模式一需要提供預算約束")
            result = optimizer.solve_budget_to_duration(
                budget=request.budget_constraint,
                indirect_cost=indirect_cost,
                penalty_type=request.penalty_type,
                penalty_amount=request.penalty_amount,
                penalty_rate=request.penalty_rate,
                contract_amount=contract_amount,
                contract_duration=request.contract_duration,
                target_duration=request.target_duration
            )
        else:  # duration_to_cost
            if not request.duration_constraint:
                raise HTTPException(status_code=400, detail="模式二需要提供工期約束")
            result = optimizer.solve_duration_to_cost(
                duration=request.duration_constraint,
                indirect_cost=indirect_cost,
                penalty_type=request.penalty_type,
                penalty_amount=request.penalty_amount,
                penalty_rate=request.penalty_rate,
                contract_amount=contract_amount,
                contract_duration=request.contract_duration,
                target_duration=request.target_duration
            )
        
        # 6. 檢查求解結果
        if result['status'] != 'success':
            raise HTTPException(
                status_code=400,
                detail=result.get('error_message', '優化計算失敗')
            )
        
        # 7. 儲存投標情境
        scenario_data = {
            "project_id": str(request.project_id),
            "mode": request.mode,
            "budget_constraint": float(request.budget_constraint) if request.budget_constraint else None,
            "duration_constraint": request.duration_constraint,
            "indirect_cost": float(indirect_cost),
            "penalty_type": request.penalty_type,
            "penalty_amount": float(request.penalty_amount) if request.penalty_amount else None,
            "penalty_rate": float(request.penalty_rate) if request.penalty_rate else None,
            "contract_amount": float(contract_amount),
            "contract_duration": request.contract_duration,
            "target_duration": request.target_duration
        }
        scenario_response = supabase.table("bidding_scenarios").insert(scenario_data).execute()
        scenario_id = scenario_response.data[0]['id']
        
        # 8. 儲存優化結果
        result_data = {
            "scenario_id": scenario_id,
            "optimal_duration": result['optimal_duration'],
            "optimal_cost": float(result['optimal_cost']),
            "indirect_cost": float(result['indirect_cost']),
            "penalty_amount": float(result['penalty_amount']),
            "bonus_amount": float(result['bonus_amount']),
            "total_cost": float(result['total_cost']),
            "calculation_time": result['calculation_time'],
            "status": result['status']
        }
        result_response = supabase.table("optimization_results").insert(result_data).execute()
        result_id = result_response.data[0]['id']
        
        # 9. 儲存作業排程
        schedules_data = [
            {
                "result_id": result_id,
                "activity_id": s['activity_id'],
                "start_time": s['start_time'],
                "end_time": s['end_time'],
                "is_crashed": s['is_crashed'],
                "duration": s['duration'],
                "cost": float(s['cost'])
            }
            for s in result['schedules']
        ]
        supabase.table("activity_schedules").insert(schedules_data).execute()
        
        # 10. 建立回應
        schedules = [
            ActivitySchedule(
                activity_id=UUID(s['activity_id']),
                activity_name=s['activity_name'],
                start_time=s['start_time'],
                end_time=s['end_time'],
                duration=s['duration'],
                is_crashed=s['is_crashed'],
                cost=s['cost']
            )
            for s in result['schedules']
        ]
        
        # 11. 準備優化輸入參數
        optimization_data = OptimizationData(
            mode=request.mode,
            budget_constraint=request.budget_constraint,
            duration_constraint=request.duration_constraint,
            indirect_cost=indirect_cost,
            penalty_type=request.penalty_type,
            penalty_amount=request.penalty_amount,
            penalty_rate=request.penalty_rate,
            contract_amount=contract_amount,
            contract_duration=request.contract_duration,
            target_duration=request.target_duration
        )
        
        # 12. 準備作業資訊
        activities_info = [
            ActivityInfo(
                id=act['id'],
                name=act['name'],
                normal_duration=act['normal_duration'],
                normal_cost=Decimal(str(act['normal_cost'])),
                crash_duration=act['crash_duration'],
                crash_cost=Decimal(str(act['crash_cost']))
            )
            for act in activities_data
        ]
        
        # 13. 準備前置關係資訊
        precedences_info = [
            PrecedenceInfo(successor=p[0], predecessor=p[1])
            for p in precedences
        ]
        
        # 14. 返回最佳化結果
        return OptimizationResult(
            scenario_id=UUID(scenario_id),
            result_id=UUID(result_id),
            optimal_duration=result['optimal_duration'],
            optimal_cost=result['optimal_cost'],
            indirect_cost=result['indirect_cost'],
            penalty_amount=result['penalty_amount'],
            bonus_amount=result['bonus_amount'],
            total_cost=result['total_cost'],
            calculation_time=result['calculation_time'],
            status=result['status'],
            error_message=None,
            schedules=schedules,
            created_at=datetime.now(),
            optimization_data=optimization_data,
            activities=activities_info,
            precedences=precedences_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"優化計算失敗：{str(e)}")


@router.get("/scenarios/{scenario_id}/results", response_model=OptimizationResult)
async def get_optimization_result(scenario_id: UUID):
    """取得優化結果"""
    try:
        # 取得投標情境（包含優化輸入參數）
        scenario_response = supabase.table("bidding_scenarios").select("*").eq("id", str(scenario_id)).execute()
        if not scenario_response.data:
            raise HTTPException(status_code=404, detail="投標情境不存在")
        
        scenario_data = scenario_response.data[0]
        project_id = scenario_data['project_id']
        
        # 取得優化結果
        result_response = supabase.table("optimization_results").select("*").eq("scenario_id", str(scenario_id)).execute()
        if not result_response.data:
            raise HTTPException(status_code=404, detail="優化結果不存在")
        
        result_data = result_response.data[0]
        result_id = result_data['id']
        
        # 取得作業排程
        schedules_response = supabase.table("activity_schedules").select(
            "*, project_activities(name)"
        ).eq("result_id", str(result_id)).execute()
        
        schedules = [
            ActivitySchedule(
                activity_id=UUID(s['activity_id']),
                activity_name=s['project_activities']['name'],
                start_time=s['start_time'],
                end_time=s['end_time'],
                duration=s['duration'],
                is_crashed=s['is_crashed'],
                cost=Decimal(str(s['cost']))
            )
            for s in schedules_response.data
        ]
        
        # 取得專案的所有作業活動
        activities_response = supabase.table("project_activities").select("*").eq("project_id", project_id).execute()
        activities_info = [
            ActivityInfo(
                id=act['id'],
                name=act['name'],
                normal_duration=act['normal_duration'],
                normal_cost=Decimal(str(act['normal_cost'])),
                crash_duration=act['crash_duration'],
                crash_cost=Decimal(str(act['crash_cost']))
            )
            for act in activities_response.data
        ]
        
        # 取得前置關係
        activity_ids = [act['id'] for act in activities_response.data]
        precedences_response = supabase.table("activity_precedences").select("*").in_("activity_id", activity_ids).execute()
        precedences_info = [
            PrecedenceInfo(
                successor=p['activity_id'], 
                predecessor=p['predecessor_id']
            )
            for p in precedences_response.data
        ]
        
        # 建立優化輸入參數
        optimization_data = OptimizationData(
            mode=scenario_data['mode'],
            budget_constraint=Decimal(str(scenario_data['budget_constraint'])) if scenario_data.get('budget_constraint') else None,
            duration_constraint=scenario_data.get('duration_constraint'),
            indirect_cost=Decimal(str(scenario_data.get('indirect_cost', 0))),
            penalty_type=scenario_data.get('penalty_type', 'rate'),
            penalty_amount=Decimal(str(scenario_data['penalty_amount'])) if scenario_data.get('penalty_amount') else None,
            penalty_rate=Decimal(str(scenario_data['penalty_rate'])) if scenario_data.get('penalty_rate') else None,
            contract_amount=Decimal(str(scenario_data.get('contract_amount', 0))),
            contract_duration=scenario_data.get('contract_duration'),
            target_duration=scenario_data.get('target_duration')
        )
        
        return OptimizationResult(
            scenario_id=UUID(result_data['scenario_id']),
            result_id=UUID(result_id),
            optimal_duration=result_data['optimal_duration'],
            optimal_cost=Decimal(str(result_data['optimal_cost'])),
            indirect_cost=Decimal(str(result_data.get('indirect_cost', 0))),
            penalty_amount=Decimal(str(result_data['penalty_amount'])),
            bonus_amount=Decimal(str(result_data['bonus_amount'])),
            total_cost=Decimal(str(result_data['total_cost'])),
            calculation_time=result_data.get('calculation_time'),
            status=result_data['status'],
            error_message=result_data.get('error_message'),
            schedules=schedules,
            created_at=datetime.fromisoformat(result_data['created_at'].replace('Z', '+00:00')),
            optimization_data=optimization_data,
            activities=activities_info,
            precedences=precedences_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得優化結果失敗：{str(e)}")

