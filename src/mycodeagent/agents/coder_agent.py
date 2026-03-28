"""代码开发Agent"""

from pathlib import Path
from typing import Any

from .base import BaseAgent, AgentResult, LLMMessage


class CoderAgent(BaseAgent):
    """代码开发Agent"""

    @property
    def name(self) -> str:
        return "coder"

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        requirements = input_data.get("requirements", [])
        project_path = input_data.get("project_path", "./output")
        language = input_data.get("language", "python")

        if not requirements:
            return AgentResult.fail("缺少需求列表")

        code_files = []
        for req in requirements[:5]:
            code = await self._generate_code(req, language)
            file_path = self._get_file_path(req, language)
            code_files.append({"path": file_path, "content": code, "requirement": req})

        written_files = []
        base_path = Path(project_path)
        base_path.mkdir(parents=True, exist_ok=True)

        for file_info in code_files:
            try:
                file_full_path = base_path / file_info["path"]
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(file_info["content"], encoding="utf-8")
                written_files.append(str(file_full_path))
            except Exception as e:
                return AgentResult.fail(f"写入文件失败: {e}")

        return AgentResult.ok({"files": written_files, "count": len(written_files)})

    async def _generate_code(self, requirement: str, language: str) -> str:
        if self._llm:
            messages = [
                LLMMessage(role="system", content=f"你是{language}编程专家。"),
                LLMMessage(role="user", content=f"生成{language}代码:\n\n{requirement}")
            ]
            return await self.chat_with_llm(messages)
        return self._generate_template_code(requirement, language)

    def _generate_template_code(self, requirement: str, language: str) -> str:
        if language == "python":
            class_name = "".join(w.capitalize() for w in requirement.split()[:3])
            return f'''"""模块: {requirement}"""

class {class_name}:
    def __init__(self):
        self.name = "{requirement}"

    def process(self) -> dict:
        return {{"status": "success", "message": "{requirement}"}}

if __name__ == "__main__":
    handler = {class_name}()
    print(handler.process())
'''
        return f"// {requirement}\n// TODO: Implement"

    def _get_file_path(self, requirement: str, language: str) -> str:
        ext = ".py" if language == "python" else ".js"
        name = requirement.lower().replace(" ", "_")[:30]
        return f"src/{name}{ext}"
