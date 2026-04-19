from __future__ import annotations

import random
import time
from typing import Dict


class AttackSimulator:
    def evaluate(self, attack_type: str) -> Dict[str, str | float]:
        base_latency = random.uniform(2, 8)
        if attack_type == "dos":
            mitigation = "rate-limit + traffic shaping"
            severity = "high"
        elif attack_type == "mitm":
            mitigation = "channel rekey + signature validation"
            severity = "critical"
        elif attack_type == "data_corruption":
            mitigation = "integrity hash rollback"
            severity = "medium"
        else:
            mitigation = "generic containment"
            severity = "low"

        time.sleep(0.05)
        return {
            "attack_type": attack_type,
            "severity": severity,
            "mitigation": mitigation,
            "response_time_ms": round(base_latency, 3),
        }
