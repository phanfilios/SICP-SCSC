from __future__ import annotations

import itertools
from collections import deque
from typing import Dict, Iterable, List


class TaskScheduler:
    def __init__(self) -> None:
        self._rr = itertools.cycle([])
        self._nodes: List[str] = []
        self.pending: deque[Dict] = deque()

    def refresh_nodes(self, nodes: Iterable[str]) -> None:
        self._nodes = sorted(set(nodes))
        self._rr = itertools.cycle(self._nodes or [None])

    def enqueue(self, task: Dict) -> None:
        self.pending.append(task)

    def next_task(self) -> Dict | None:
        return self.pending.popleft() if self.pending else None

    def select_node(self, current_load: Dict[str, int]) -> str | None:
        alive_nodes = [n for n in self._nodes if n in current_load]
        if not alive_nodes:
            return None

        min_load = min(current_load.get(n, 0) for n in alive_nodes)
        candidates = {n for n in alive_nodes if current_load.get(n, 0) == min_load}

        for _ in range(len(alive_nodes)):
            candidate = next(self._rr)
            if candidate in candidates:
                return candidate

        return alive_nodes[0]
