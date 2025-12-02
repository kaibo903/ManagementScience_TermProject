"""
投標最佳化決策系統 - MILP 模型實作
使用 PuLP 求解整數線性規劃問題
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import time

import pulp


class Activity:
    """作業活動類別

    Attributes:
        id: 作業 ID（資料表主鍵）
        name: 作業名稱
        normal_duration: 正常工期（天）
        normal_cost: 正常施工成本
        crash_duration: 趕工工期（天）
        crash_cost: 趕工成本
        crash_slope: 單位縮短 1 天的趕工追加成本
    """

    def __init__(
        self,
        activity_id: str,
        name: str,
        normal_duration: int,
        normal_cost: Decimal,
        crash_duration: int,
        crash_cost: Decimal,
    ) -> None:
        self.id = activity_id
        self.name = name
        self.normal_duration = int(normal_duration)
        self.normal_cost = float(normal_cost)
        self.crash_duration = int(crash_duration)
        self.crash_cost = float(crash_cost)

        # 計算趕工成本斜率（若沒有縮短空間則為 0）
        if self.normal_duration > self.crash_duration:
            self.crash_slope = float(crash_cost - normal_cost) / float(
                self.normal_duration - self.crash_duration
            )
        else:
            self.crash_slope = 0.0


class BiddingOptimizer:
    """投標最佳化決策模型

    以 MILP 形式建模兩種模式：
    1. 給定預算，求最短工期（Budget → Duration）
    2. 給定工期，求最低成本（Duration → Cost）
    """

    def __init__(self, activities: List[Activity], precedences: List[Tuple[str, str]]):
        """
        初始化優化器

        Args:
            activities: 作業活動列表
            precedences: 前置關係列表，格式為 [(後續作業ID, 前置作業ID), ...]
        """
        self.activities: Dict[str, Activity] = {act.id: act for act in activities}
        self.precedences = precedences
        self.problem: Optional[pulp.LpProblem] = None

    # ------------------------------------------------------------------
    # 一些輔助：用關鍵路徑法估算正常工期與最短工期（全部趕工）
    # ------------------------------------------------------------------

    def _calculate_normal_duration(self) -> int:
        """計算正常工期（全部使用正常工期）"""
        earliest_start: Dict[str, int] = {}
        visited: set[str] = set()

        def get_earliest_start(act_id: str) -> int:
            if act_id in earliest_start:
                return earliest_start[act_id]
            if act_id in visited:
                # 有循環時直接回 0，避免無窮遞迴
                return 0
            visited.add(act_id)

            if act_id not in self.activities:
                return 0

            act = self.activities[act_id]
            min_start = 0

            # 找出所有前置作業
            for successor_id, predecessor_id in self.precedences:
                if successor_id == act_id and predecessor_id in self.activities:
                    pred_start = get_earliest_start(predecessor_id)
                    pred_act = self.activities[predecessor_id]
                    pred_end = pred_start + pred_act.normal_duration
                    min_start = max(min_start, pred_end)

            earliest_start[act_id] = min_start
            return min_start

        for aid in self.activities.keys():
            get_earliest_start(aid)

        normal_duration = 0
        for aid, act in self.activities.items():
            start_time = earliest_start.get(aid, 0)
            end_time = start_time + act.normal_duration
            normal_duration = max(normal_duration, end_time)
        return normal_duration

    def _calculate_min_duration(self) -> int:
        """計算最短可能工期（全部作業皆趕工）"""
        earliest_start: Dict[str, int] = {}
        visited: set[str] = set()

        def get_earliest_start(act_id: str) -> int:
            if act_id in earliest_start:
                return earliest_start[act_id]
            if act_id in visited:
                return 0
            visited.add(act_id)

            if act_id not in self.activities:
                return 0

            act = self.activities[act_id]
            min_start = 0

            for successor_id, predecessor_id in self.precedences:
                if successor_id == act_id and predecessor_id in self.activities:
                    pred_start = get_earliest_start(predecessor_id)
                    pred_act = self.activities[predecessor_id]
                    pred_end = pred_start + pred_act.crash_duration
                    min_start = max(min_start, pred_end)

            earliest_start[act_id] = min_start
            return min_start

        for aid in self.activities.keys():
            get_earliest_start(aid)

        min_duration = 0
        for aid, act in self.activities.items():
            start_time = earliest_start.get(aid, 0)
            end_time = start_time + act.crash_duration
            min_duration = max(min_duration, end_time)
        return min_duration

    def _calculate_min_cost(self, indirect_cost: Decimal = Decimal("0")) -> Decimal:
        """計算在不趕工情況下的最小可能成本（正常直接成本 + 間接成本）"""
        min_direct_cost = sum(act.normal_cost for act in self.activities.values())
        normal_duration = self._calculate_normal_duration()
        min_total_cost = Decimal(str(min_direct_cost)) + indirect_cost * normal_duration
        return min_total_cost

    # ------------------------------------------------------------------
    # 模式一：預算 → 工期
    # ------------------------------------------------------------------

    def solve_budget_to_duration(
        self,
        budget: Decimal,
        indirect_cost: Decimal = Decimal("0.0"),
        penalty_type: str = "rate",
        penalty_amount: Optional[Decimal] = None,
        penalty_rate: Optional[Decimal] = None,
        contract_amount: Decimal = Decimal("0.0"),
        contract_duration: Optional[int] = None,
        target_duration: Optional[int] = None,
    ) -> Dict:
        """
        模式一：給定預算，求最短工期（同時考慮獎懲）
        """
        start_time = time.time()

        self.problem = pulp.LpProblem("Budget_To_Duration", pulp.LpMinimize)

        # 決策變數
        x = {
            act_id: pulp.LpVariable(f"x_{act_id}", lowBound=0, cat="Integer")
            for act_id in self.activities.keys()
        }
        y = {
            act_id: pulp.LpVariable(f"y_{act_id}", cat="Binary")
            for act_id in self.activities.keys()
        }
        T = pulp.LpVariable("T", lowBound=0, cat="Integer")

        # 目標函數：最小化工期 + 違約金 - 趕工獎金
        penalty_term = 0
        bonus_term = 0

        if target_duration:
            # penalty_days >= max(T - target_duration, 0)
            penalty_days = pulp.LpVariable("penalty_days", lowBound=0, cat="Integer")
            self.problem += penalty_days >= T - target_duration
            self.problem += penalty_days >= 0

            if penalty_type == "fixed" and penalty_amount:
                penalty_term = float(penalty_amount) * penalty_days
            elif penalty_type == "rate" and penalty_rate and contract_amount:
                daily_penalty = float(penalty_rate) * float(contract_amount)
                penalty_term = daily_penalty * penalty_days

            # 趕工獎金：若提前完成
            if contract_amount and contract_duration and contract_duration > 0:
                # 單日獎金率：(契約決標總價 / 契約工期) × 5%
                daily_bonus = (float(contract_amount) / contract_duration) * 0.05
                bonus_days = pulp.LpVariable("bonus_days", lowBound=0, cat="Integer")
                self.problem += bonus_days >= target_duration - T
                self.problem += bonus_days >= 0
                bonus_term = daily_bonus * bonus_days

                # 趕工獎金上限：契約決標總價的 1%
                bonus_limit = float(contract_amount) * 0.01
                self.problem += bonus_term <= bonus_limit

        # 目標：最小化 T + penalty_term - bonus_term
        self.problem += T + penalty_term - bonus_term

        # 約束 1：前置作業
        for successor_id, predecessor_id in self.precedences:
            if successor_id in self.activities and predecessor_id in self.activities:
                pred_act = self.activities[predecessor_id]
                pred_duration = (
                    pred_act.normal_duration * (1 - y[predecessor_id])
                    + pred_act.crash_duration * y[predecessor_id]
                )
                self.problem += x[successor_id] >= x[predecessor_id] + pred_duration

        # 約束 2：工期定義
        for act_id, act in self.activities.items():
            duration_expr = (
                act.normal_duration * (1 - y[act_id])
                + act.crash_duration * y[act_id]
            )
            self.problem += T >= x[act_id] + duration_expr

        # 約束 3：預算約束（直接成本 + 間接成本 <= budget）
        direct_cost_expr = pulp.lpSum(
            (
                act.normal_cost * (1 - y[act_id])
                + act.crash_cost * y[act_id]
                for act_id, act in self.activities.items()
            )
        )
        indirect_cost_term = float(indirect_cost) * T
        total_cost_expr = direct_cost_expr + indirect_cost_term
        self.problem += total_cost_expr <= float(budget)

        # 求解
        self.problem.solve(pulp.PULP_CBC_CMD(msg=0))
        calculation_time = time.time() - start_time

        if self.problem.status != pulp.LpStatusOptimal:
            error_message = f"求解失敗：{pulp.LpStatus[self.problem.status]}"

            if self.problem.status == pulp.LpStatusInfeasible:
                min_cost = self._calculate_min_cost(indirect_cost)
                reasons: List[str] = []
                if min_cost > budget:
                    reasons.append(
                        f"預算不足：即使所有作業都不趕工，最小成本也需要 {min_cost:.2f}，"
                        f"但預算只有 {budget:.2f}（差距：{min_cost - budget:.2f}）"
                    )
                else:
                    reasons.append("預算約束與其他約束條件衝突，無法找到可行解")
                error_message = (
                    f"無可行解（Infeasible）。原因：{'；'.join(reasons)}。"
                    "建議：增加預算或調整作業參數。"
                )

            return {
                "status": "infeasible"
                if self.problem.status == pulp.LpStatusInfeasible
                else "error",
                "error_message": error_message,
                "calculation_time": calculation_time,
            }

        # 取得最優解
        optimal_duration = int(pulp.value(T))

        direct_cost_val = sum(
            act.normal_cost if y[act_id].varValue == 0 else act.crash_cost
            for act_id, act in self.activities.items()
        )
        indirect_cost_amount = indirect_cost * optimal_duration

        calculated_penalty = Decimal("0.0")
        bonus_amount = Decimal("0.0")

        if target_duration:
            if optimal_duration > target_duration:
                overdue_days = optimal_duration - target_duration
                if penalty_type == "fixed" and penalty_amount:
                    calculated_penalty = penalty_amount * overdue_days
                elif penalty_type == "rate" and penalty_rate and contract_amount:
                    daily_penalty = penalty_rate * contract_amount
                    calculated_penalty = daily_penalty * overdue_days

                # 違約金上限：契約價金總額的 20%
                if contract_amount > 0:
                    penalty_limit = contract_amount * Decimal("0.2")
                    calculated_penalty = min(calculated_penalty, penalty_limit)
            elif optimal_duration < target_duration:
                if contract_amount and contract_duration and contract_duration > 0:
                    early_days = target_duration - optimal_duration
                    bonus_amount = (
                        contract_amount
                        * Decimal(str(early_days))
                        / Decimal(str(contract_duration))
                        * Decimal("0.05")
                    )
                    bonus_limit = contract_amount * Decimal("0.01")
                    bonus_amount = min(bonus_amount, bonus_limit)

        optimal_cost = Decimal(str(direct_cost_val)) + indirect_cost_amount
        total_cost = optimal_cost + calculated_penalty - bonus_amount

        schedules: List[Dict] = []
        for act_id, act in self.activities.items():
            start_time_val = int(x[act_id].varValue)
            is_crashed = bool(y[act_id].varValue)
            duration_val = act.crash_duration if is_crashed else act.normal_duration
            cost_val = act.crash_cost if is_crashed else act.normal_cost
            schedules.append(
                {
                    "activity_id": act_id,
                    "activity_name": act.name,
                    "start_time": start_time_val,
                    "end_time": start_time_val + duration_val,
                    "duration": duration_val,
                    "is_crashed": is_crashed,
                    "cost": Decimal(str(cost_val)),
                }
            )

        return {
            "status": "success",
            "optimal_duration": optimal_duration,
            "optimal_cost": Decimal(str(direct_cost_val)),
            "indirect_cost": indirect_cost_amount,
            "penalty_amount": calculated_penalty,
            "bonus_amount": bonus_amount,
            "total_cost": total_cost,
            "calculation_time": calculation_time,
            "schedules": schedules,
        }

    # ------------------------------------------------------------------
    # 模式二：工期 → 成本
    # ------------------------------------------------------------------

    def solve_duration_to_cost(
        self,
        duration: int,
        indirect_cost: Decimal = Decimal("0.0"),
        penalty_type: str = "rate",
        penalty_amount: Optional[Decimal] = None,
        penalty_rate: Optional[Decimal] = None,
        contract_amount: Decimal = Decimal("0.0"),
        contract_duration: Optional[int] = None,
        target_duration: Optional[int] = None,
    ) -> Dict:
        """
        模式二：給定工期，求最低成本
        """
        start_time = time.time()

        self.problem = pulp.LpProblem("Duration_To_Cost", pulp.LpMinimize)

        # 決策變數
        x = {
            act_id: pulp.LpVariable(f"x_{act_id}", lowBound=0, cat="Integer")
            for act_id in self.activities.keys()
        }
        y = {
            act_id: pulp.LpVariable(f"y_{act_id}", cat="Binary")
            for act_id in self.activities.keys()
        }

        # 專案總工期 T：在工期固定模式中，T 會被嚴格固定為使用者輸入的工期
        # 透過將上下界都設為 duration，確保 T = duration
        T = pulp.LpVariable(
            "T",
            lowBound=int(duration),
            upBound=int(duration),
            cat="Integer",
        )

        # 目標：最小化 總成本（直接 + 間接）+ 違約金 - 獎金
        direct_cost_expr = pulp.lpSum(
            (
                act.normal_cost * (1 - y[act_id])
                + act.crash_cost * y[act_id]
                for act_id, act in self.activities.items()
            )
        )
        indirect_cost_term = float(indirect_cost) * T
        total_cost_expr = direct_cost_expr + indirect_cost_term

        penalty_term = 0
        bonus_term = 0

        if target_duration:
            penalty_days = pulp.LpVariable("penalty_days", lowBound=0, cat="Integer")
            self.problem += penalty_days >= T - target_duration
            self.problem += penalty_days >= 0

            if penalty_type == "fixed" and penalty_amount:
                penalty_term = float(penalty_amount) * penalty_days
            elif penalty_type == "rate" and penalty_rate and contract_amount:
                daily_penalty = float(penalty_rate) * float(contract_amount)
                penalty_term = daily_penalty * penalty_days

            if contract_amount and contract_duration and contract_duration > 0:
                daily_bonus = (float(contract_amount) / contract_duration) * 0.05
                bonus_days = pulp.LpVariable("bonus_days", lowBound=0, cat="Integer")
                self.problem += bonus_days >= target_duration - T
                self.problem += bonus_days >= 0
                bonus_term = daily_bonus * bonus_days

                bonus_limit = float(contract_amount) * 0.01
                self.problem += bonus_term <= bonus_limit

        self.problem += total_cost_expr + penalty_term - bonus_term

        # 約束 1：前置作業
        for successor_id, predecessor_id in self.precedences:
            if successor_id in self.activities and predecessor_id in self.activities:
                pred_act = self.activities[predecessor_id]
                pred_duration = (
                    pred_act.normal_duration * (1 - y[predecessor_id])
                    + pred_act.crash_duration * y[predecessor_id]
                )
                self.problem += x[successor_id] >= x[predecessor_id] + pred_duration

        # 約束 2：工期定義
        for act_id, act in self.activities.items():
            duration_expr = (
                act.normal_duration * (1 - y[act_id])
                + act.crash_duration * y[act_id]
            )
            self.problem += T >= x[act_id] + duration_expr

        # 求解
        self.problem.solve(pulp.PULP_CBC_CMD(msg=0))
        calculation_time = time.time() - start_time

        if self.problem.status != pulp.LpStatusOptimal:
            error_message = f"求解失敗：{pulp.LpStatus[self.problem.status]}"

            if self.problem.status == pulp.LpStatusInfeasible:
                min_duration = self._calculate_min_duration()
                reasons: List[str] = []
                if min_duration > duration:
                    reasons.append(
                        "工期約束過緊：即使所有作業都趕工，"
                        f"最短工期也需要 {min_duration} 天，"
                        f"但約束工期只有 {duration} 天（差距：{min_duration - duration} 天）"
                    )
                else:
                    reasons.append("工期約束與其他約束條件衝突，無法找到可行解")
                error_message = (
                    f"無可行解（Infeasible）。原因：{'；'.join(reasons)}。"
                    "建議：放寬工期約束或調整作業參數。"
                )

            return {
                "status": "infeasible"
                if self.problem.status == pulp.LpStatusInfeasible
                else "error",
                "error_message": error_message,
                "calculation_time": calculation_time,
            }

        optimal_duration = int(pulp.value(T))

        direct_cost_val = sum(
            act.normal_cost if y[act_id].varValue == 0 else act.crash_cost
            for act_id, act in self.activities.items()
        )
        indirect_cost_amount = indirect_cost * optimal_duration

        calculated_penalty = Decimal("0.0")
        bonus_amount = Decimal("0.0")

        if target_duration:
            if optimal_duration > target_duration:
                overdue_days = optimal_duration - target_duration
                if penalty_type == "fixed" and penalty_amount:
                    calculated_penalty = penalty_amount * overdue_days
                elif penalty_type == "rate" and penalty_rate and contract_amount:
                    daily_penalty = penalty_rate * contract_amount
                    calculated_penalty = daily_penalty * overdue_days

                if contract_amount > 0:
                    penalty_limit = contract_amount * Decimal("0.2")
                    calculated_penalty = min(calculated_penalty, penalty_limit)
            elif optimal_duration < target_duration:
                if contract_amount and contract_duration and contract_duration > 0:
                    early_days = target_duration - optimal_duration
                    bonus_amount = (
                        contract_amount
                        * Decimal(str(early_days))
                        / Decimal(str(contract_duration))
                        * Decimal("0.05")
                    )
                    bonus_limit = contract_amount * Decimal("0.01")
                    bonus_amount = min(bonus_amount, bonus_limit)

        optimal_cost = Decimal(str(direct_cost_val)) + indirect_cost_amount
        total_cost_value = optimal_cost + calculated_penalty - bonus_amount

        schedules: List[Dict] = []
        for act_id, act in self.activities.items():
            start_time_val = int(x[act_id].varValue)
            is_crashed = bool(y[act_id].varValue)
            duration_val = act.crash_duration if is_crashed else act.normal_duration
            cost_val = act.crash_cost if is_crashed else act.normal_cost
            schedules.append(
                {
                    "activity_id": act_id,
                    "activity_name": act.name,
                    "start_time": start_time_val,
                    "end_time": start_time_val + duration_val,
                    "duration": duration_val,
                    "is_crashed": is_crashed,
                    "cost": Decimal(str(cost_val)),
                }
            )

        return {
            "status": "success",
            "optimal_duration": optimal_duration,
            "optimal_cost": Decimal(str(direct_cost_val)),
            "indirect_cost": indirect_cost_amount,
            "penalty_amount": calculated_penalty,
            "bonus_amount": bonus_amount,
            "total_cost": total_cost_value,
            "calculation_time": calculation_time,
            "schedules": schedules,
        }


