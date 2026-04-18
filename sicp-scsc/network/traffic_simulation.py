import asyncio
import random
import time
import json
import socket
from datetime import datetime

class TrafficSimulator:
    def __init__(self, nodes):
        """
        nodes = [
            {"ip": "127.0.0.1", "port": 8001},
            {"ip": "127.0.0.1", "port": 8002}
        ]
        """
        self.nodes = nodes
        self.running = False

    def generate_packet(self):
        packet = {
            "timestamp": datetime.utcnow().isoformat(),
            "payload": f"data_{random.randint(1000,9999)}",
            "size": random.randint(64, 2048),  # bytes simulados
            "type": random.choice(["normal", "control", "heartbeat"])
        }
        return json.dumps(packet)


    async def send_packet(self, node, packet):
        try:
            reader, writer = await asyncio.open_connection(
                node["ip"], node["port"]
            )

            start_time = time.time()

            writer.write(packet.encode())
            await writer.drain()

            writer.close()
            await writer.wait_closed()

            latency = (time.time() - start_time) * 1000  # ms

            print(f"[→] Enviado a {node['ip']}:{node['port']} | Latencia: {latency:.2f} ms")

            return latency

        except Exception as e:
            print(f"[!] Error enviando a {node['ip']}:{node['port']} → {e}")
            return None


    async def normal_traffic(self, rate=1):
        """
        rate = paquetes por segundo
        """
        self.running = True

        while self.running:
            packet = self.generate_packet()
            node = random.choice(self.nodes)

            asyncio.create_task(self.send_packet(node, packet))

            await asyncio.sleep(1 / rate)


    async def high_load_traffic(self, rate=50):
        """
        rate alto = estrés del sistema
        """
        self.running = True

        while self.running:
            tasks = []
            for _ in range(rate):
                packet = self.generate_packet()
                node = random.choice(self.nodes)
                tasks.append(self.send_packet(node, packet))

            await asyncio.gather(*tasks)


    async def flood_attack(self, target_node, duration=10):
        print(f"\n🚨 INICIANDO ATAQUE FLOOD a {target_node['ip']}:{target_node['port']}")

        end_time = time.time() + duration

        while time.time() < end_time:
            packet = {
                "timestamp": datetime.utcnow().isoformat(),
                "payload": "ATTACK_PACKET",
                "size": 4096,
                "type": "flood"
            }

            asyncio.create_task(
                self.send_packet(target_node, json.dumps(packet))
            )

            await asyncio.sleep(0.001)  # ultra agresivo

        print("🛑 Ataque finalizado\n")


    async def latency_test(self, samples=10):
        print("\n📊 TEST DE LATENCIA")

        results = []

        for _ in range(samples):
            node = random.choice(self.nodes)
            packet = self.generate_packet()

            latency = await self.send_packet(node, packet)

            if latency:
                results.append(latency)

            await asyncio.sleep(0.5)

        if results:
            avg = sum(results) / len(results)
            print(f"\n📈 Latencia promedio: {avg:.2f} ms")
        else:
            print("⚠ No se pudo medir latencia")

 
    def stop(self):
        self.running = False
        print("\n🛑 Simulación detenida")



async def start_node_server(port):
    async def handle_client(reader, writer):
        data = await reader.read(4096)
        message = data.decode()

        print(f"[←] Recibido en puerto {port}: {message[:50]}...")

        writer.close()

    server = await asyncio.start_server(handle_client, '0.0.0.0', port)

    print(f"🟢 Nodo escuchando en puerto {port}")
    async with server:
        await server.serve_forever()



if __name__ == "__main__":
    nodes = [
        {"ip": "127.0.0.1", "port": 8001},
        {"ip": "127.0.0.1", "port": 8002}
    ]

    simulator = TrafficSimulator(nodes)

    async def main():
        # Levantar nodos simulados
        asyncio.create_task(start_node_server(8001))
        asyncio.create_task(start_node_server(8002))

        await asyncio.sleep(2)

        # Ejecutar pruebas
        await simulator.latency_test()

        await simulator.normal_traffic(rate=5)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        simulator.stop()