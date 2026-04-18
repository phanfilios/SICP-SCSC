import asyncio
import random
import time
import psutil
import socket

class AttackSimulator:
    def __init__(self, target_ip="127.0.0.1", target_port=8000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attack_running = False
        self.metrics = []


    async def simulate_dos(self, duration=10, intensity=50):
        print(f"[ATTACK] Iniciando ataque DoS a {self.target_ip}:{self.target_port}")
        self.attack_running = True
        start_time = time.time()

        while time.time() - start_time < duration:
            tasks = []
            for _ in range(intensity):
                tasks.append(self.send_packet())

            await asyncio.gather(*tasks)

        self.attack_running = False
        print("[ATTACK] Ataque finalizado")

    async def send_packet(self):
        try:
            reader, writer = await asyncio.open_connection(self.target_ip, self.target_port)
            payload = self.generate_payload()
            writer.write(payload)
            await writer.drain()
            writer.close()
        except:
            pass  # fallo esperado en simulación

    def generate_payload(self):
        size = random.randint(64, 1024)
        return bytes(random.getrandbits(8) for _ in range(size))


    def simulate_noise(self):
        noise_level = random.uniform(0.1, 1.0)
        print(f"[NOISE] Nivel de interferencia simulado: {noise_level:.3f}")
        return noise_level

 
    def monitor_system(self):
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent

        metric = {
            "cpu": cpu,
            "memory": memory,
            "timestamp": time.time()
        }

        self.metrics.append(metric)
        print(f"[MONITOR] CPU: {cpu}% | RAM: {memory}%")

  
    async def recovery_protocol(self):
        print("[RECOVERY] Iniciando protocolo de recuperación...")
        await asyncio.sleep(2)

        # Simulación de estabilización
        self.metrics.clear()
        print("[RECOVERY] Sistema estabilizado")

   
    async def run_full_simulation(self):
        print("[SIMULATION] Iniciando escenario completo")

        monitor_task = asyncio.create_task(self.monitor_loop())

        # Ejecutar ataque
        await self.simulate_dos(duration=10, intensity=30)

        # Simular interferencia
        self.simulate_noise()

        # Recuperación
        await self.recovery_protocol()

        monitor_task.cancel()
        print("[SIMULATION] Finalizado")

    async def monitor_loop(self):
        while True:
            self.monitor_system()
            await asyncio.sleep(1)



if __name__ == "__main__":
    simulator = AttackSimulator(target_ip="127.0.0.1", target_port=8000)

    try:
        asyncio.run(simulator.run_full_simulation())
    except KeyboardInterrupt:
        print("\n[INFO] Simulación interrumpida por el usuario")