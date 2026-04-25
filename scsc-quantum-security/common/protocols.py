"""
Protocolos de comunicación entre master y nodos
Define los mensajes, tipos y formato de intercambio
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
import hashlib
import time

class MessageType(Enum):
    """Tipos de mensajes en el cluster"""
    # Heartbeat
    HEARTBEAT = "heartbeat"
    HEARTBEAT_RESPONSE = "heartbeat_response"
    
    # Task management
    TASK_ASSIGN = "task_assign"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    TASK_STATUS = "task_status"
    
    # Quantum tasks
    QUANTUM_SIMULATE = "quantum_simulate"
    QUANTUM_RESULT = "quantum_result"
    
    # Security
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    ENCRYPTED_MESSAGE = "encrypted_message"
    
    # Node management
    NODE_REGISTER = "node_register"
    NODE_UNREGISTER = "node_unregister"
    NODE_STATUS = "node_status"
    
    # Data sync
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    
    # Fault tolerance
    LEADER_ELECTION = "leader_election"
    LEADER_ANNOUNCE = "leader_announce"

@dataclass
class Message:
    """Estructura base de mensaje"""
    type: MessageType
    sender_id: str
    recipient_id: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:16])
    
    def to_json(self) -> str:
        """Serializa mensaje a JSON"""
        data = {
            "type": self.type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserializa mensaje desde JSON"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            message_id=data["message_id"]
        )

class Protocol:
    """Protocolo de comunicación del cluster"""
    
    @staticmethod
    def create_heartbeat(node_id: str, master_id: str) -> Message:
        """Crea mensaje de heartbeat"""
        return Message(
            type=MessageType.HEARTBEAT,
            sender_id=node_id,
            recipient_id=master_id,
            payload={
                "status": "alive",
                "timestamp": time.time()
            }
        )
    
    @staticmethod
    def create_task_assign(task_id: str, task_type: str, task_data: Dict, 
                          node_id: str, master_id: str) -> Message:
        """Crea mensaje de asignación de tarea"""
        return Message(
            type=MessageType.TASK_ASSIGN,
            sender_id=master_id,
            recipient_id=node_id,
            payload={
                "task_id": task_id,
                "task_type": task_type,
                "task_data": task_data,
                "assigned_at": time.time()
            }
        )
    
    @staticmethod
    def create_quantum_task(qubits: int, circuit_data: Dict, 
                           node_id: str, master_id: str) -> Message:
        """Crea tarea de simulación cuántica"""
        return Message(
            type=MessageType.QUANTUM_SIMULATE,
            sender_id=master_id,
            recipient_id=node_id,
            payload={
                "num_qubits": qubits,
                "circuit": circuit_data,
                "shots": 1024,
                "timestamp": time.time()
            }
        )
    
    @staticmethod
    def create_node_register(node_id: str, master_id: str, 
                            capabilities: Dict) -> Message:
        """Registro de nuevo nodo en el cluster"""
        return Message(
            type=MessageType.NODE_REGISTER,
            sender_id=node_id,
            recipient_id=master_id,
            payload={
                "capabilities": capabilities,
                "registered_at": time.time()
            }
        )
    
    @staticmethod
    def create_node_status(node_id: str, master_id: str, 
                          metrics: Dict) -> Message:
        """Reporte de estado del nodo"""
        return Message(
            type=MessageType.NODE_STATUS,
            sender_id=node_id,
            recipient_id=master_id,
            payload={
                "metrics": metrics,
                "cpu_usage": metrics.get("cpu", 0),
                "memory_usage": metrics.get("memory", 0),
                "tasks_completed": metrics.get("tasks", 0)
            }
        )