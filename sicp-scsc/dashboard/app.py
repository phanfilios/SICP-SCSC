import asyncio
import logging
from datetime import datetime


from orchestrator import ClusterOrchestrator
from scheduler import TaskScheduler
from attack_simulator import AttackSimulator
from crypto_engine import CryptoEngine
from traffic_simulation import TrafficSimulator
from fault_tolerance import FaultToleranceManager



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

SYSTEM_NAME = "Project Entropy - Quantum Security Core"



class QuantumSecuritySystem:

    def __init__(self):
        logging.info(f"Iniciando {SYSTEM_NAME}")

        # Inicialización de módulos
        self.cluster = ClusterOrchestrator()
        self.scheduler = TaskScheduler()
        self.crypto = CryptoEngine()
        self.attack_sim = AttackSimulator()
        self.traffic_sim = TrafficSimulator()
        self.fault_manager = FaultToleranceManager(self.cluster)

   
    async def initialize(self):
        logging.info("Inicializando cluster...")
        await self.cluster.initialize_nodes()

        logging.info("Inicializando tolerancia a fallos...")
        self.fault_manager.initialize()

        logging.info("Sistema listo.\n")

    async def simulate_traffic(self):
        while True:
            traffic_data = self.traffic_sim.generate_packet()
            encrypted = self.crypto.encrypt_data(traffic_data)

            logging.info(f"Tráfico cifrado enviado: {encrypted[:50]}...")

            await asyncio.sleep(1)


    async def simulate_attacks(self):
        while True:
            attack = self.attack_sim.launch_attack()

            logging.warning(f"Ataque detectado: {attack}")

            # Activar defensa
            response = self.crypto.defensive_response(attack)
            logging.info(f"Respuesta del sistema: {response}")

            await asyncio.sleep(5)


    async def monitor_system(self):
        while True:
            status = self.cluster.get_status()
            logging.info(f"Estado del cluster: {status}")

            # Verificar fallos
            self.fault_manager.check_health()

            await asyncio.sleep(3)

  
    async def run(self):
        await self.initialize()

        tasks = [
            asyncio.create_task(self.simulate_traffic()),
            asyncio.create_task(self.simulate_attacks()),
            asyncio.create_task(self.monitor_system()),
            asyncio.create_task(self.scheduler.run())
        ]

        await asyncio.gather(*tasks)



if __name__ == "__main__":
    system = QuantumSecuritySystem()

    try:
        asyncio.run(system.run())
    except KeyboardInterrupt:
        logging.info("Sistema detenido manualmente.")