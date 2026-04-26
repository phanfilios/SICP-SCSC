"""
Punto de entrada principal del Nodo Master
"""

import sys
import os
import signal
import time
from typing import Dict, Any

# Añadir ruta padre para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import config
from common.logger import setup_logger
from common.utils import Timer, get_system_metrics
from master.orchestrator import Orchestrator

class MasterApp:
    """Aplicación principal del Master Node"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.orchestrator = None
        self.running = True
        self.initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el nodo master"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("SCSC Master Node Initializing...")
            self.logger.info("=" * 60)
            
            # Validar configuración
            config.validate()
            self.logger.info(f"✓ Configuration validated")
            self.logger.info(f"  Master: {config.master_host}:{config.master_port}")
            self.logger.info(f"  Nodes: {len(config.nodes)} configured")
            self.logger.info(f"  Quantum: {config.quantum_backend} (max {config.max_qubits} qubits)")
            
            # Inicializar orquestador
            self.logger.info("Initializing orchestrator...")
            self.orchestrator = Orchestrator()
            
            if not self.orchestrator.initialize():
                raise RuntimeError("Failed to initialize orchestrator")
            
            self.initialized = True
            self.logger.info("✓ Master node initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize master: {e}")
            return False
    
    def run(self) -> None:
        """Ejecuta el nodo master"""
        if not self.initialized:
            self.logger.error("Master not initialized. Call initialize() first.")
            return
        
        self.logger.info("Starting Master node...")
        
        # Configurar signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Iniciar orquestador
            self.orchestrator.start()
            
            # Loop principal
            while self.running:
                time.sleep(1)
                
                # Mostrar estado periódicamente
                if int(time.time()) % 30 == 0:  # Cada 30 segundos
                    self._print_status()
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Error in master loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Apaga el nodo master gracefulmente"""
        self.logger.info("Shutting down Master node...")
        self.running = False
        
        if self.orchestrator:
            self.orchestrator.stop()
        
        self.logger.info("Master node shutdown complete")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Maneja señales del sistema"""
        self.logger.info(f"Received signal {signum}")
        self.running = False
    
    def _print_status(self) -> None:
        """Imprime estado actual del sistema"""
        if self.orchestrator:
            status = self.orchestrator.get_cluster_status()
            metrics = get_system_metrics()
            
            self.logger.info("\n" + "=" * 50)
            self.logger.info("CLUSTER STATUS")
            self.logger.info("=" * 50)
            self.logger.info(f"Status: {status.get('status', 'unknown')}")
            self.logger.info(f"Active nodes: {status.get('active_nodes', 0)}/{status.get('total_nodes', 0)}")
            self.logger.info(f"Tasks completed: {status.get('tasks_completed', 0)}")
            self.logger.info(f"CPU: {metrics.get('cpu_percent', 0)}%")
            self.logger.info(f"Memory: {metrics.get('memory_percent', 0)}%")
            self.logger.info("=" * 50 + "\n")

def main():
    """Función principal"""
    app = MasterApp()
    
    if app.initialize():
        app.run()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()