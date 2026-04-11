"""Main orchestration logic for the meta-planning agent."""

from __future__ import annotations

from app.config import config
from app.critic import Critic
from app.llm import LLMClient
from app.planner import Planner
from app.schemas import AgentState
from app.solver import Solver


class Agent:
    """Coordinates Planner -> Solver -> Critic with limited replanning."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        planner: Planner | None = None,
        solver: Solver | None = None,
        critic: Critic | None = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient(model_name=config.MODEL_NAME)
        self.planner = planner or Planner(self.llm_client)
        self.solver = solver or Solver(self.llm_client)
        self.critic = critic or Critic(self.llm_client)

    def run(self, task_id: str, task: str) -> AgentState:
        state = AgentState(task_id=task_id, task=task)
        iteration = 0

        while True:
            iteration += 1
            plan = self.planner.build_plan(task)
            solver_result = self.solver.solve(task, plan)
            critic_result = self.critic.review(task, plan, solver_result.draft_solution)

            state.plan = plan
            state.draft_solution = solver_result.draft_solution
            state.critic_feedback = critic_result.feedback
            state.needs_replan = critic_result.needs_replan
            state.run_history.append(
                {
                    "iteration": iteration,
                    "plan_raw": plan.raw_text,
                    "strategy": plan.strategy,
                    "steps": plan.steps,
                    "draft_solution": solver_result.draft_solution,
                    "critic_feedback": critic_result.feedback,
                    "needs_replan": critic_result.needs_replan,
                }
            )

            if critic_result.needs_replan and state.replan_count < config.MAX_REPLANS:
                state.replan_count += 1
                continue

            state.final_answer = solver_result.draft_solution
            break

        return state
