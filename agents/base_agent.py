# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: agents/base_agent.py (private repository)
# Excerpt: the contract every agent implements. Logging, health checks,
# metrics and real-time status broadcasting are omitted.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""Abstract base class for all Nova AI agents."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class BaseAgent(ABC):
    """Common interface and lifecycle for Discovery, Reasoning, Implementation,
    Quality, Deployment and Monitoring agents."""

    def __init__(self, agent_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}
        self.state: Dict[str, Any] = {}
        self.status = AgentStatus.IDLE
        self.error_history: List[Dict[str, Any]] = []
        self.execution_count = 0
        self.created_at = datetime.now()

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent's main task and return a structured result."""

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Reject malformed input before any model or database call."""

    # ... update_state(), get_state(), reset_state(), health_check(),
    #     run-log persistence and WebSocket status updates ...
