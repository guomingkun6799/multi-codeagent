"""核心Orchestrator模块"""

from enum import Enum
from typing import Any

from ..agents.base import BaseAgent, AgentResult


class WorkflowStage(Enum):
    REQUIREMENT = "requirement"
    CODE = "code"
    REVIEW = "review"


class Orchestrator:
    """中央调度器"""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._llm_client: Any = None
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def register_agent(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def set_llm_client(self, client: Any) -> None:
        self._llm_client = client
        for agent in self._agents.values():
            agent._llm = client

    async def initialize(self) -> None:
        from ..agents import RequirementAgent, CoderAgent, ReviewerAgent
        self.register_agent(RequirementAgent())
        self.register_agent(CoderAgent())
        self.register_agent(ReviewerAgent())
        if self._llm_client:
            self.set_llm_client(self._llm_client)
        self._initialized = True

    async def run_workflow(self, context: dict[str, Any], stages: list[WorkflowStage] = None) -> dict[str, Any]:
        if not self._initialized:
            await self.initialize()

        if stages is None:
            stages = list(WorkflowStage)

        results: dict[str, Any] = {"stages": {}}

        for stage in stages:
            result = await self._execute_stage(stage, context)
            results["stages"][stage.value] = result

            if not result.success:
                results["failed"] = stage.value
                results["error"] = result.error
                break

            context.update(result.data)

        results["success"] = "failed" not in results
        return results

    async def _execute_stage(self, stage: WorkflowStage, context: dict[str, Any]) -> AgentResult:
        agent = self._agents.get(stage.value)
        if not agent:
            return AgentResult.fail(f"Agent不存在: {stage.value}")

        try:
            return await agent.execute(context)
        except Exception as e:
            return AgentResult.fail(str(e))

    async def run_single_agent(self, agent_name: str, context: dict[str, Any]) -> AgentResult:
        if not self._initialized:
            await self.initialize()
        agent = self._agents.get(agent_name)
        if not agent:
            return AgentResult.fail(f"Agent不存在: {agent_name}")
        return await agent.execute(context)
