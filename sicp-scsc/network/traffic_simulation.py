from __future__ import annotations

import random
import time
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class TrafficMetric:
    latency_ms: float
    throughput_mbps: float
    packet_loss: float
    timestamp: float


class TrafficSimulator:
    def sample(self, under_attack: bool = False) -> Dict:
        factor = 2.5 if under_attack else 1.0
        metric = TrafficMetric(
            latency_ms=round(random.uniform(2, 12) * factor, 3),
            throughput_mbps=round(random.uniform(80, 250) / factor, 3),
            packet_loss=round(random.uniform(0.0, 0.8) * factor, 3),
            timestamp=time.time(),
        )
        return asdict(metric)
