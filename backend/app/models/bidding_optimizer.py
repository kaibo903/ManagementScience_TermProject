"""
投標最佳化決策系統 - MILP 模型實作
使用 PuLP 求解整數線性規劃問題
"""
import pulp
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
import time


class Activity:
    """作業活動類別"""
    def __init__(self, activity_id: str, name: str, normal_duration: int, 
                 normal_cost: Decimal, crash_duration: int, crash_cost: Decimal):
        self.id = activity_id
        self.name = name
        self.normal_duration = normal_duration
        self.normal_cost = float(normal_cost)
        self.crash_duration = crash_duration
        self.crash_cost = float(crash_cost)
        # 計算趕工成本斜率
        if normal_duration > crash_duration:
            self.crash_slope = (crash_cost - normal_cost) / (normal_duration - crash_duration)
        else:
            self.crash_slope = 0


class BiddingOptimizer:
    """投標最佳化決策模型"""
    
    def __init__(self, activities: List[Activity], precedences: List[Tuple[str, str]]):
        """
        初始化優化器
        
        Args:
            activities: 作業活動列表
            precedences: 前置關係列表，格式為 [(後續作業ID, 前置作業ID), ...]
        """
        self.activities = {act.id: act for act in activities}
        self.precedences = precedences
        self.problem = None
        self.solution = None
        
    def solve_budget_to_duration(self, budget: Decimal, penalty_rate: Decimal = Decimal('0.0'),
                                bonus_rate: Decimal = Decimal('0.0'), 
                                target_duration: Optional[int] = None) -> Dict:
        """
        模式一：給定預算，求最短工期
        
        Args:
            budget: 預算約束
            penalty_rate: 逾期違約金率（每日）
            bonus_rate: 趕工獎金率（每日）
            target_duration: 目標工期（用於計算獎懲）
            
        Returns:
            包含優化結果的字典
        """
        start_time = time.time()
        
        # 建立 MILP 問題
        self.problem = pulp.LpProblem("Budget_To_Duration", pulp.LpMinimize)
        
        # 決策變數
        # x[i]: 作業 i 的開始時間
        x = {act_id: pulp.LpVariable(f"x_{act_id}", lowBound=0, cat='Integer') 
             for act_id in self.activities.keys()}
        
        # y[i]: 作業 i 是否趕工（0/1 二元變數）
        y = {act_id: pulp.LpVariable(f"y_{act_id}", cat='Binary') 
             for act_id in self.activities.keys()}
        
        # T: 專案總工期
        T = pulp.LpVariable("T", lowBound=0, cat='Integer')
        
        # 目標函數：最小化工期 + 違約金 - 獎金
        penalty_term = 0
        bonus_term = 0
        
        if target_duration:
            # 如果超過目標工期，計算違約金
            penalty_term = penalty_rate * pulp.LpVariable("penalty_days", lowBound=0, cat='Integer')
            self.problem += penalty_term >= penalty_rate * (T - target_duration)
            
            # 如果提前完成，計算獎金
            bonus_term = bonus_rate * pulp.LpVariable("bonus_days", lowBound=0, cat='Integer')
            self.problem += bonus_term <= bonus_rate * (target_duration - T)
            self.problem += bonus_term >= 0
        
        self.problem += T + penalty_term - bonus_term
        
        # 約束條件
        
        # 1. 前置作業約束：後續作業的開始時間 >= 前置作業的結束時間
        for successor_id, predecessor_id in self.precedences:
            if successor_id in self.activities and predecessor_id in self.activities:
                pred_act = self.activities[predecessor_id]
                # 前置作業的結束時間 = 開始時間 + 工期
                pred_duration = (pred_act.normal_duration * (1 - y[predecessor_id]) + 
                                pred_act.crash_duration * y[predecessor_id])
                self.problem += x[successor_id] >= x[predecessor_id] + pred_duration
        
        # 2. 工期約束：總工期 >= 所有作業的結束時間
        for act_id, act in self.activities.items():
            duration = (act.normal_duration * (1 - y[act_id]) + 
                        act.crash_duration * y[act_id])
            self.problem += T >= x[act_id] + duration
        
        # 3. 預算約束：總成本 <= 預算
        total_cost = pulp.lpSum([
            (act.normal_cost * (1 - y[act_id]) + act.crash_cost * y[act_id])
            for act_id, act in self.activities.items()
        ])
        self.problem += total_cost <= float(budget)
        
        # 求解
        self.problem.solve(pulp.PULP_CBC_CMD(msg=0))
        
        calculation_time = time.time() - start_time
        
        # 檢查求解狀態
        if self.problem.status != pulp.LpStatusOptimal:
            return {
                'status': 'infeasible' if self.problem.status == pulp.LpStatusInfeasible else 'error',
                'error_message': f'求解失敗：{pulp.LpStatus[self.problem.status]}',
                'calculation_time': calculation_time
            }
        
        # 提取結果
        optimal_duration = int(pulp.value(T))
        optimal_cost = sum([
            (act.normal_cost if y[act_id].varValue == 0 else act.crash_cost)
            for act_id, act in self.activities.items()
        ])
        
        # 計算獎懲金額
        penalty_amount = Decimal('0.0')
        bonus_amount = Decimal('0.0')
        if target_duration:
            if optimal_duration > target_duration:
                penalty_amount = penalty_rate * (optimal_duration - target_duration)
            elif optimal_duration < target_duration:
                bonus_amount = bonus_rate * (target_duration - optimal_duration)
        
        total_cost = Decimal(str(optimal_cost)) + penalty_amount - bonus_amount
        
        # 提取作業排程
        schedules = []
        for act_id, act in self.activities.items():
            start_time = int(x[act_id].varValue)
            is_crashed = bool(y[act_id].varValue)
            duration = act.crash_duration if is_crashed else act.normal_duration
            cost = act.crash_cost if is_crashed else act.normal_cost
            
            schedules.append({
                'activity_id': act_id,
                'activity_name': act.name,
                'start_time': start_time,
                'end_time': start_time + duration,
                'duration': duration,
                'is_crashed': is_crashed,
                'cost': Decimal(str(cost))
            })
        
        return {
            'status': 'success',
            'optimal_duration': optimal_duration,
            'optimal_cost': Decimal(str(optimal_cost)),
            'penalty_amount': penalty_amount,
            'bonus_amount': bonus_amount,
            'total_cost': total_cost,
            'calculation_time': calculation_time,
            'schedules': schedules
        }
    
    def solve_duration_to_cost(self, duration: int, penalty_rate: Decimal = Decimal('0.0'),
                               bonus_rate: Decimal = Decimal('0.0'),
                               target_duration: Optional[int] = None) -> Dict:
        """
        模式二：給定工期，求最低成本
        
        Args:
            duration: 工期約束
            penalty_rate: 逾期違約金率（每日）
            bonus_rate: 趕工獎金率（每日）
            target_duration: 目標工期（用於計算獎懲）
            
        Returns:
            包含優化結果的字典
        """
        start_time = time.time()
        
        # 建立 MILP 問題
        self.problem = pulp.LpProblem("Duration_To_Cost", pulp.LpMinimize)
        
        # 決策變數
        x = {act_id: pulp.LpVariable(f"x_{act_id}", lowBound=0, cat='Integer') 
             for act_id in self.activities.keys()}
        
        y = {act_id: pulp.LpVariable(f"y_{act_id}", cat='Binary') 
             for act_id in self.activities.keys()}
        
        T = pulp.LpVariable("T", lowBound=0, cat='Integer')
        
        # 目標函數：最小化總成本 + 違約金 - 獎金
        total_cost = pulp.lpSum([
            (act.normal_cost * (1 - y[act_id]) + act.crash_cost * y[act_id])
            for act_id, act in self.activities.items()
        ])
        
        penalty_term = 0
        bonus_term = 0
        
        if target_duration:
            penalty_term = penalty_rate * pulp.LpVariable("penalty_days", lowBound=0, cat='Integer')
            self.problem += penalty_term >= penalty_rate * (T - target_duration)
            
            bonus_term = bonus_rate * pulp.LpVariable("bonus_days", lowBound=0, cat='Integer')
            self.problem += bonus_term <= bonus_rate * (target_duration - T)
            self.problem += bonus_term >= 0
        
        self.problem += total_cost + penalty_term - bonus_term
        
        # 約束條件
        
        # 1. 前置作業約束
        for successor_id, predecessor_id in self.precedences:
            if successor_id in self.activities and predecessor_id in self.activities:
                pred_act = self.activities[predecessor_id]
                pred_duration = (pred_act.normal_duration * (1 - y[predecessor_id]) + 
                                pred_act.crash_duration * y[predecessor_id])
                self.problem += x[successor_id] >= x[predecessor_id] + pred_duration
        
        # 2. 工期約束
        for act_id, act in self.activities.items():
            duration_var = (act.normal_duration * (1 - y[act_id]) + 
                           act.crash_duration * y[act_id])
            self.problem += T >= x[act_id] + duration_var
        
        # 3. 工期約束：總工期 <= 目標工期
        self.problem += T <= duration
        
        # 求解
        self.problem.solve(pulp.PULP_CBC_CMD(msg=0))
        
        calculation_time = time.time() - start_time
        
        # 檢查求解狀態
        if self.problem.status != pulp.LpStatusOptimal:
            return {
                'status': 'infeasible' if self.problem.status == pulp.LpStatusInfeasible else 'error',
                'error_message': f'求解失敗：{pulp.LpStatus[self.problem.status]}',
                'calculation_time': calculation_time
            }
        
        # 提取結果
        optimal_duration = int(pulp.value(T))
        optimal_cost = sum([
            (act.normal_cost if y[act_id].varValue == 0 else act.crash_cost)
            for act_id, act in self.activities.items()
        ])
        
        # 計算獎懲金額
        penalty_amount = Decimal('0.0')
        bonus_amount = Decimal('0.0')
        if target_duration:
            if optimal_duration > target_duration:
                penalty_amount = penalty_rate * (optimal_duration - target_duration)
            elif optimal_duration < target_duration:
                bonus_amount = bonus_rate * (target_duration - optimal_duration)
        
        total_cost_value = Decimal(str(optimal_cost)) + penalty_amount - bonus_amount
        
        # 提取作業排程
        schedules = []
        for act_id, act in self.activities.items():
            start_time = int(x[act_id].varValue)
            is_crashed = bool(y[act_id].varValue)
            duration_var = act.crash_duration if is_crashed else act.normal_duration
            cost = act.crash_cost if is_crashed else act.normal_cost
            
            schedules.append({
                'activity_id': act_id,
                'activity_name': act.name,
                'start_time': start_time,
                'end_time': start_time + duration_var,
                'duration': duration_var,
                'is_crashed': is_crashed,
                'cost': Decimal(str(cost))
            })
        
        return {
            'status': 'success',
            'optimal_duration': optimal_duration,
            'optimal_cost': Decimal(str(optimal_cost)),
            'penalty_amount': penalty_amount,
            'bonus_amount': bonus_amount,
            'total_cost': total_cost_value,
            'calculation_time': calculation_time,
            'schedules': schedules
        }

