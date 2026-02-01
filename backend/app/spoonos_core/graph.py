from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
import copy


@dataclass
class TraceEvent:
    node: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    started_at: str
    ended_at: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node": self.node,
            "input": self.input,
            "output": self.output,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "status": self.status,
        }


class Node:
    name = "node"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Node.run must be implemented")


class GraphAgent:
    def __init__(
        self,
        nodes: Dict[str, Node],
        edges: Dict[str, List[str]],
        entry_node: str,
        exit_nodes: List[str],
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.entry_node = entry_node
        self.exit_nodes = set(exit_nodes)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        trace: List[Dict[str, Any]] = []
        current = self.entry_node
        ctx = dict(context)

        while current:
            node = self.nodes[current]
            ctx["trace"] = trace
            started_at = _utc_now()
            try:
                output = node.run(ctx) or {}
                status = "ok"
            except Exception as exc:  # pragma: no cover - surfaced in trace
                output = {"error": str(exc)}
                status = "error"
            ended_at = _utc_now()

            trace_event = TraceEvent(
                node=node.name,
                input=copy.deepcopy(ctx),
                output=copy.deepcopy(output),
                started_at=started_at,
                ended_at=ended_at,
                status=status,
            )
            trace.append(trace_event.to_dict())

            ctx.update(output)
            ctx["trace"] = trace

            if current in self.exit_nodes:
                break

            next_nodes = self.edges.get(current, [])
            current = next_nodes[0] if next_nodes else None

        ctx["trace"] = trace
        return ctx


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
