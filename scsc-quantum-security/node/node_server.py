"""
Servidor del nodo esclavo - Ejecuta tareas asignadas por el master
"""

import sys
import os
import time
import threading
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import config
from common.logger import setup_logger
from common.protocols import Protocol, Message, MessageType
from common.utils import generate_node_id, get_system_metrics

class NodeServer:
    """Servidor del nodo esclavo"""
    
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or generate_node_id()
        self.logger = setup_logger(f"node.{self.node_id}")
        self.running = False
        self.tasks_executed = 0
        self.master_url = f"http://{config.master_host}:{config.master_port}"
        
        # Estado del nodo
        self.status = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "tasks_completed": 0,
            "uptime": 0
        }
        
        self.start_time = time.time()
        
    def initialize(self) -> bool:
        """Inicializa el nodo"""
        try:
            self.logger.info("=" * 50)
            self.logger.info(f"SCSC Node Server Initializing...")
            self.logger.info(f"Node ID: {self.node_id}")
            self.logger.info(f"Master: {self.master_url}")
            self.logger.info("=" * 50)
            
            # Registrar en el master
            self._register_with_master()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> None:
        """Inicia el servidor del nodo"""
        self.logger.info("Starting Node server...")
        self.running = True
        
        # Iniciar threads
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        metrics_thread = threading.Thread(target=self._metrics_loop, daemon=True)
        
        heartbeat_thread.start()
        metrics_thread.start()
        
        self.logger.info(f"Node {self.node_id} started successfully")
        
        # Loop principal
        try:
            while self.running:
                time.sleep(1)
                
                # Aquí iría la lógica para recibir tareas (simulado)
                self._simulate_task_reception()
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Apaga el nodo gracefulmente"""
        self.logger.info(f"Shutting down Node {self.node_id}...")
        self.running = False
        
        # Desregistrar del master
        self._unregister_from_master()
        
        uptime = time.time() - self.start_time
        self.logger.info(f"Node {self.node_id} shutdown after {uptime:.1f}s")
        self.logger.info(f"Total tasks executed: {self.tasks_executed}")
    
    def _register_with_master(self) -> None:
        """Registra el nodo en el master"""
        self.logger.info(f"Registering with master at {self.master_url}")
        
        # Aquí iría la comunicación real con el master
        # Por ahora es simulado
        self.logger.info("✓ Registered with master")
    
    def _unregister_from_master(self) -> None:
        """Desregistra el nodo del master"""
        self.logger.info("Unregistering from master...")
        # Simulado
    
    def _heartbeat_loop(self) -> None:
        """Envía heartbeats al master periódicamente"""
        while self.running:
            try:
                # Actualizar métricas
                metrics = get_system_metrics()
                self.status["cpu_usage"] = metrics.get("cpu_percent", 0)
                self.status["memory_usage"] = metrics.get("memory_percent", 0)
                
                # Simular envío de heartbeat
                self.logger.debug(f"Heartbeat sent to master (CPU: {self.status['cpu_usage']}%)")
                
                time.sleep(config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                time.sleep(1)
    
    def _metrics_loop(self) -> None:
        """Recolecta y reporta métricas del sistema"""
        while self.running:
            try:
                metrics = get_system_metrics()
                self.status.update(metrics)
                
                # Log periódico de métricas
                if int(time.time()) % 30 == 0:
                    self.logger.info(
                        f"Status - CPU: {self.status['cpu_usage']}%, "
                        f"Memory: {self.status['memory_usage']}%, "
                        f"Tasks: {self.tasks_executed}"
                    )
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                time.sleep(5)
    
    def _simulate_task_reception(self) -> None:
        """Simula la recepción y ejecución de tareas"""
        # Simulación simple: cada 10 segundos ejecuta una tarea de prueba
        import random
        
        if int(time.time()) % 10 == 0 and self.running:
            task_type = random.choice(["quantum", "crypto", "analysis"])
            
            self.logger.info(f"Simulating task execution: {task_type}")
            
            # Simular procesamiento
            time.sleep(0.5)
            
            self.tasks_executed += 1
            self.logger.info(f"Task completed. Total: {self.tasks_executed}")

def main():
    """Función principal para el nodo"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SCSC Node Server")
    parser.add_argument("--node-id", type=str, help="Custom node ID")
    args = parser.parse_args()
    
    server = NodeServer(node_id=args.node_id)
    
    if server.initialize():
        server.start()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()