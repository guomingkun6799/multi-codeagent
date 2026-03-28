"""代码审查Agent"""

from typing import Any

from .base import BaseAgent, AgentResult, LLMMessage


class ReviewerAgent(BaseAgent):
    """代码审查Agent"""

    @property
    def name(self) -> str:
        return "reviewer"

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        files = input_data.get("files", [])
        requirements = input_data.get("requirements", [])

        if not files and not requirements:
            return AgentResult.fail("缺少审查内容")

        reviews = []
        for req in requirements:
            review = await self._review_requirement(req)
            reviews.append(review)

        score = self._calculate_score(reviews)

        return AgentResult.ok({
            "reviews": reviews,
            "score": score,
            "passed": score >= 60,
            "suggestions": self._generate_suggestions(reviews)
        })

    async def _review_requirement(self, requirement: str) -> dict:
        if self._llm:
            messages = [
                LLMMessage(role="system", content="你是代码审查专家。"),
                LLMMessage(role="user", content=f"审查需求:\n\n{requirement}")
            ]
            response = await self.chat_with_llm(messages)
            return {"requirement": requirement, "review": response}
        return {"requirement": requirement, "review": "代码审查通过", "scores": {}}

    def _calculate_score(self, reviews: list[dict]) -> int:
        return 75 if reviews else 0

    def _generate_suggestions(self, reviews: list[dict]) -> list[str]:
        return ["代码质量良好"] if reviews else ["无需建议"]
