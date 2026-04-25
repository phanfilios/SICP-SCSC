"""
Utilidades generales para el sistema SCSC
"""

import hashlib
import json
import uuid
import time
from typing import Any, Dict
from datetime import datetime

def generate_node_id() -> str:
    """Genera un ID único para un nodo del cluster"""
    return f"node_{uuid.uuid4().hex[:8]}"

def calculate_checksum(data: Any) -> str:
    """Calcula checksum SHA-256 de los datos"""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, (str, bytes)):
        data = str(data)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def format_bytes(bytes_value: int) -> str:
    """Formatea bytes a formato legible (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_timestamp() -> float:
    """Retorna timestamp actual"""
    return time.time()

def serialize_json(data: Any, pretty: bool = False) -> str:
    """Serializa datos a JSON"""
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)

def deserialize_json(json_str: str) -> Dict:
    """Deserializa JSON a diccionario"""
    return json.loads(json_str)

def get_system_metrics() -> Dict[str, Any]:
    """Obtiene métricas del sistema"""
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }
    except ImportError:
        return {
            "error": "psutil not installed",
            "timestamp": time.time()
        }

class Timer:
    """Context manager para medir tiempo de ejecución"""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
        elapsed = self.elapsed_time
        print(f"[TIMER] {self.name} took {elapsed:.4f} seconds")
    
    @property
    def elapsed_time(self) -> float:
        """Retorna tiempo transcurrido en segundos"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time