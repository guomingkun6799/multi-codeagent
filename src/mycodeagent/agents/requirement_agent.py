"""需求分析Agent"""

from typing import Any

from .base import BaseAgent, AgentResult, LLMMessage


class RequirementAgent(BaseAgent):
    """需求分析Agent"""

    @property
    def name(self) -> str:
        return "requirement"

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        project_name = input_data.get("project_name", "未命名项目")
        description = input_data.get("description", "")

        if not description:
            return AgentResult.fail("缺少项目描述")

        if self._llm:
            messages = [
                LLMMessage(role="system", content="你是一个需求分析专家。"),
                LLMMessage(role="user", content=f"分析项目需求:\n\n{project_name}\n{description}")
            ]
            analysis = await self.chat_with_llm(messages)
        else:
            analysis = self._generate_simple_analysis(project_name, description)

        return AgentResult.ok({
            "project_name": project_name,
            "analysis": analysis,
            "requirements": self._extract_requirements(analysis)
        })

    def _generate_simple_analysis(self, project_name: str, description: str) -> str:
        return f"""# {project_name} 需求分析报告

## 项目目标
开发: {description}

## 核心功能
1. 基础功能模块
2. 数据管理
3. 用户界面

## 验收标准
- [ ] 功能完整
- [ ] 运行稳定
"""

    def _extract_requirements(self, analysis: str) -> list[str]:
        requirements = []
        for line in analysis.split("\n"):
            if line.strip().startswith("- [ ]") or line.strip().startswith("-"):
                requirements.append(line.strip().lstrip("-[] ").strip())
        return requirements if requirements else ["基础功能"]
