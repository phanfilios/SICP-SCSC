import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class Message:
    msg_type: str
    source: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.msg_type,
            "source": self.source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": self.payload,
        }


def encode_message(data: Dict[str, Any]) -> bytes:
    return (json.dumps(data) + "\n").encode("utf-8")


def decode_message(raw: bytes) -> Dict[str, Any]:
    return json.loads(raw.decode("utf-8").strip())
