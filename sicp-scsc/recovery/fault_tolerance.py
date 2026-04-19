from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NodeState:
    node_id: str
    host: str
    port: int
    last_heartbeat: float = field(default_factory=time.time)
    alive: bool = True
    failures: int = 0


class FaultToleranceManager:
    def __init__(self, heartbeat_timeout: float = 8.0) -> None:
        self.heartbeat_timeout = heartbeat_timeout
        self.nodes: Dict[str, NodeState] = {}

    def register(self, node_id: str, host: str, port: int) -> None:
        self.nodes[node_id] = NodeState(node_id=node_id, host=host, port=port)

    def heartbeat(self, node_id: str) -> None:
        if node_id in self.nodes:
            state = self.nodes[node_id]
            state.last_heartbeat = time.time()
            state.alive = True

    def evaluate(self) -> List[str]:
        now = time.time()
        recovered_or_failed: List[str] = []

        for node_id, state in self.nodes.items():
            missed = now - state.last_heartbeat > self.heartbeat_timeout
            if missed and state.alive:
                state.alive = False
                state.failures += 1
                recovered_or_failed.append(node_id)
        return recovered_or_failed

    def alive_nodes(self) -> List[str]:
        return [node_id for node_id, state in self.nodes.items() if state.alive]

    def status(self) -> Dict[str, Dict]:
        return {
            node_id: {
                "alive": st.alive,
                "last_heartbeat": st.last_heartbeat,
                "failures": st.failures,
            }
            for node_id, st in self.nodes.items()
        }
