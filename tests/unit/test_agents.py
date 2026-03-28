"""Agent测试"""

import pytest
from mycodeagent.agents.base import BaseAgent, AgentResult


class TestAgentResult:
    def test_ok(self):
        result = AgentResult.ok({"key": "value"})
        assert result.success is True

    def test_fail(self):
        result = AgentResult.fail("error")
        assert result.success is False
