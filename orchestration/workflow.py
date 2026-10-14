# ─────────────────────────────────────────────────────────────────────────────
# Nova AI · showcase excerpt
# Source: orchestration/workflow.py (private repository, ~1,100 lines)
# Excerpt: the shared state, the graph wiring and the quality-gated retry loop.
# Node bodies, persistence and WebSocket broadcasting are omitted.
# © Apex Intelligence. Shown for demonstration only; all rights reserved.
# ─────────────────────────────────────────────────────────────────────────────

"""LangGraph workflow that orchestrates the Nova AI agents.

Discovery → Implementation → Quality → Deployment → Monitoring,
with a Reasoning-guided repair loop when the quality gate fails.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agents.deployment_agent import DeploymentAgent
from agents.discovery_agent import DiscoveryAgent
from agents.implementation_agent import ImplementationAgent
from agents.monitoring_agent import MonitoringAgent
from agents.quality_agent import QualityAgent
from agents.reasoning_agent import ReasoningAgent


class PipelineState(TypedDict, total=False):
    """Everything the agents share while one pipeline request runs."""

    workflow_id: str
    current_stage: str
    user_requirements: Dict[str, Any]
    discovery_result: Optional[Dict[str, Any]]
    reasoning_result: Optional[Dict[str, Any]]
    implementation_result: Optional[Dict[str, Any]]
    quality_result: Optional[Dict[str, Any]]
    deployment_result: Optional[Dict[str, Any]]
    monitoring_result: Optional[Dict[str, Any]]
    errors: List[str]
    retry_count: Dict[str, int]
    metadata: Dict[str, Any]
    final_result: Optional[Dict[str, Any]]
    pipeline_id: Optional[str]


class PipelineWorkflow:
    """Builds and runs the agent graph for one pipeline request."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.max_retries = self.config.get("max_retries", 3)
        self.agents = {
            "discovery": DiscoveryAgent(),
            "reasoning": ReasoningAgent(),
            "implementation": ImplementationAgent(),
            "quality": QualityAgent(),
            "deployment": DeploymentAgent(),
            "monitoring": MonitoringAgent(),
        }
        self._build_workflow()

    def _build_workflow(self) -> None:
        workflow = StateGraph(PipelineState)

        workflow.add_node("discovery", self._discovery_node)
        workflow.add_node("reasoning", self._reasoning_node)
        workflow.add_node("implementation", self._implementation_node)
        workflow.add_node("quality", self._quality_node)
        workflow.add_node("deployment", self._deployment_node)
        workflow.add_node("monitoring", self._monitoring_node)
        workflow.add_node("error_handler", self._error_handler_node)

        workflow.set_entry_point("discovery")
        workflow.add_edge("discovery", "implementation")
        workflow.add_edge("implementation", "quality")

        # The quality gate decides: ship it, repair it, or stop.
        workflow.add_conditional_edges(
            "quality",
            self._route_after_quality,
            {"deploy": "deployment", "retry": "reasoning", "fail": "error_handler"},
        )
        # Reasoning proposes a fix, then implementation tries again.
        workflow.add_conditional_edges(
            "reasoning",
            self._route_after_reasoning,
            {"implement": "implementation", "fail": "error_handler"},
        )

        workflow.add_edge("deployment", "monitoring")
        workflow.add_edge("monitoring", END)
        workflow.add_edge("error_handler", END)

        # Checkpointing lets a run be inspected and resumed stage by stage.
        self.graph = workflow.compile(checkpointer=MemorySaver())

    def _route_after_quality(self, state: PipelineState) -> Literal["deploy", "retry", "fail"]:
        quality_result = state.get("quality_result", {})
        if not quality_result or quality_result.get("status") != "success":
            return "fail"
        if quality_result.get("passed", False):
            return "deploy"
        if state["retry_count"].get("implementation", 0) < self.max_retries:
            return "retry"
        return "fail"

    # ... _discovery_node, _reasoning_node, _implementation_node, _quality_node,
    #     _deployment_node, _monitoring_node, _error_handler_node, _route_after_reasoning,
    #     execute(), and per-stage persistence of PipelineRun / AgentLog records ...
