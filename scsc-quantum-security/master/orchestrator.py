"""
Orquestador del cluster - Coordina nodos y tareas
"""

import threading
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import config
from common.logger import setup_logger
from common.protocols import Protocol, Message, MessageType
from common.utils import generate_node_id, calculate_checksum, Timer

class Orchestrator:
    """Orquestador principal del cluster SCSC"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.nodes: Dict[str, Dict] = {}  # node_id -> node_info
        self.tasks: Dict[str, Dict] = {}  # task_id -> task_info
        self.task_queue = deque()
        self.running = False
        self.master_id = generate_node_id()
        
        # Threads
        self.heartbeat_thread = None
        self.task_dispatcher_thread = None
        self.monitor_thread = None
        
    def initialize(self) -> bool:
        """Inicializa el orquestador"""
        try:
            self.logger.info("Initializing Orchestrator...")
            
            # Registrar nodos configurados
            for node_config in config.nodes:
                node_id = node_config["id"]
                self.nodes[node_id] = {
                    "id": node_id,
                    "host": node_config["host"],
                    "port": node_config["port"],
                    "status": "pending",
                    "last_heartbeat": None,
                    "tasks_assigned": 0,
                    "tasks_completed": 0,
                    "capabilities": {
                        "max_qubits": config.max_qubits,
                        "quantum_backend": config.quantum_backend
                    }
                }
                self.logger.info(f"✓ Registered node: {node_id} ({node_config['host']})")
            
            self.logger.info(f"Total nodes registered: {len(self.nodes)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Orchestrator initialization failed: {e}")
            return False
    
    def start(self) -> None:
        """Inicia el orquestador"""
        self.logger.info("Starting Orchestrator...")
        self.running = True
        
        # Iniciar threads
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.task_dispatcher_thread = threading.Thread(target=self._task_dispatcher_loop, daemon=True)
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        
        self.heartbeat_thread.start()
        self.task_dispatcher_thread.start()
        self.monitor_thread.start()
        
        self.logger.info("Orchestrator started successfully")
        
        # Mantener vivo
        while self.running:
            time.sleep(1)
    
    def stop(self) -> None:
        """Detiene el orquestador"""
        self.logger.info("Stopping Orchestrator...")
        self.running = False
        
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        if self.task_dispatcher_thread:
            self.task_dispatcher_thread.join(timeout=5)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Orchestrator stopped")
    
    def submit_task(self, task_type: str, task_data: Dict) -> str:
        """Envía una tarea al cluster"""
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        self.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "data": task_data,
            "status": "queued",
            "submitted_at": time.time(),
            "assigned_node": None,
            "result": None
        }
        
        self.task_queue.append(task_id)
        self.logger.info(f"Task {task_id} queued (type: {task_type})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Obtiene estado de una tarea"""
        return self.tasks.get(task_id)
    
    def get_cluster_status(self) -> Dict:
        """Obtiene estado completo del cluster"""
        active_nodes = sum(1 for n in self.nodes.values() if n.get("status") == "active")
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.get("status") == "completed")
        
        return {
            "status": "operational" if active_nodes > 0 else "degraded",
            "master_id": self.master_id,
            "total_nodes": len(self.nodes),
            "active_nodes": active_nodes,
            "tasks_total": total_tasks,
            "tasks_completed": completed_tasks,
            "tasks_pending": len(self.task_queue),
            "timestamp": time.time()
        }
    
    def _heartbeat_loop(self) -> None:
        """Envía heartbeats periódicos a los nodos"""
        while self.running:
            try:
                for node_id, node_info in self.nodes.items():
                    # Simular heartbeat (aquí iría comunicación real)
                    node_info["last_heartbeat"] = time.time()
                    node_info["status"] = "active"
                    
                    self.logger.debug(f"Heartbeat sent to {node_id}")
                
                time.sleep(config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                time.sleep(1)
    
    def _task_dispatcher_loop(self) -> None:
        """Despacha tareas a los nodos disponibles"""
        while self.running:
            try:
                # Buscar nodos activos
                active_nodes = [
                    (node_id, node_info) 
                    for node_id, node_info in self.nodes.items() 
                    if node_info.get("status") == "active"
                ]
                
                if active_nodes and self.task_queue:
                    # Tomar tarea pendiente
                    task_id = self.task_queue.popleft()
                    task = self.tasks.get(task_id)
                    
                    if task:
                        # Asignar al nodo con menos carga
                        node_id, node_info = min(
                            active_nodes,
                            key=lambda x: x[1].get("tasks_assigned", 0)
                        )
                        
                        task["assigned_node"] = node_id
                        task["status"] = "assigned"
                        node_info["tasks_assigned"] += 1
                        
                        self.logger.info(f"Task {task_id} assigned to {node_id}")
                        
                        # Simular ejecución de tarea (thread separado)
                        threading.Thread(
                            target=self._simulate_task_execution,
                            args=(task_id, node_id)
                        ).start()
                
                time.sleep(0.1)  # Pequeña pausa para evitar CPU 100%
                
            except Exception as e:
                self.logger.error(f"Task dispatcher error: {e}")
                time.sleep(1)
    
    def _simulate_task_execution(self, task_id: str, node_id: str) -> None:
        """Simula la ejecución de una tarea en un nodo"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        # Simular tiempo de procesamiento
        time.sleep(2)
        
        # Marcar como completada
        task["status"] = "completed"
        task["completed_at"] = time.time()
        task["result"] = {
            "status": "success",
            "node": node_id,
            "execution_time": 2.0,
            "data": f"Result for {task_id}"
        }
        
        # Actualizar métricas del nodo
        if node_id in self.nodes:
            self.nodes[node_id]["tasks_assigned"] -= 1
            self.nodes[node_id]["tasks_completed"] += 1
        
        self.logger.info(f"Task {task_id} completed on {node_id}")
    
    def _monitor_loop(self) -> None:
        """Monitorea la salud del cluster"""
        while self.running:
            try:
                now = time.time()
                timeout = config.node_timeout
                
                for node_id, node_info in self.nodes.items():
                    last_hb = node_info.get("last_heartbeat", 0)
                    
                    if last_hb and (now - last_hb) > timeout:
                        if node_info.get("status") == "active":
                            node_info["status"] = "failed"
                            self.logger.warning(f"Node {node_id} timed out (no heartbeat for {now - last_hb:.1f}s)")
                
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(5)