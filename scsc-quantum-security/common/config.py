"""
Configuración central del sistema SCSC
Carga variables de entorno y configuración global
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

@dataclass
class Config:
    """Configuración central del cluster SCSC"""
    
    # Master configuration
    master_host: str = field(default_factory=lambda: os.getenv("MASTER_HOST", "127.0.0.1"))
    master_port: int = field(default_factory=lambda: int(os.getenv("MASTER_PORT", "8080")))
    master_api_port: int = field(default_factory=lambda: int(os.getenv("MASTER_API_PORT", "8081")))
    
    # Nodes configuration
    node_port: int = field(default_factory=lambda: int(os.getenv("NODE_PORT", "9090")))
    
    @property
    def nodes(self) -> List[Dict[str, Any]]:
        """Lista de nodos esclavos del cluster"""
        nodes = []
        for i in range(1, 6):  # 5 nodos
            node_host = os.getenv(f"NODE_{i}_HOST")
            if node_host:
                nodes.append({
                    "id": f"node_{i}",
                    "host": node_host,
                    "port": self.node_port,
                    "status": "unknown"
                })
        return nodes
    
    # Security
    cluster_secret_key: str = field(default_factory=lambda: os.getenv("CLUSTER_SECRET_KEY", "dev_secret_key"))
    api_key: str = field(default_factory=lambda: os.getenv("API_KEY", "dev_api_key"))
    
    # Quantum configuration
    quantum_backend: str = field(default_factory=lambda: os.getenv("QUANTUM_BACKEND", "aer_simulator"))
    quantum_shots: int = field(default_factory=lambda: int(os.getenv("QUANTUM_SHOTS", "1024")))
    max_qubits: int = field(default_factory=lambda: int(os.getenv("MAX_QUBITS", "24")))
    
    # Monitoring
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    prometheus_port: int = field(default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "8000")))
    
    # Fault tolerance
    heartbeat_interval: int = field(default_factory=lambda: int(os.getenv("HEARTBEAT_INTERVAL", "5")))
    node_timeout: int = field(default_factory=lambda: int(os.getenv("NODE_TIMEOUT", "15")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    
    # Storage
    redis_host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    redis_db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario"""
        return {
            "master": {
                "host": self.master_host,
                "port": self.master_port,
                "api_port": self.master_api_port
            },
            "nodes": self.nodes,
            "quantum": {
                "backend": self.quantum_backend,
                "shots": self.quantum_shots,
                "max_qubits": self.max_qubits
            },
            "monitoring": {
                "log_level": self.log_level,
                "prometheus_port": self.prometheus_port
            }
        }
    
    def validate(self) -> bool:
        """Valida que la configuración sea correcta"""
        if not self.master_host:
            raise ValueError("MASTER_HOST no está configurado")
        
        if not self.nodes:
            raise ValueError("No hay nodos configurados en el cluster")
        
        if self.max_qubits < 1 or self.max_qubits > 30:
            raise ValueError(f"MAX_QUBITS debe estar entre 1 y 30. Actual: {self.max_qubits}")
        
        return True

# Instancia global de configuración
config = Config()