import asyncio
import time
import random
from datetime import datetime

class FaultToleranceManager:
    def __init__(self, nodes):
        """
        nodes = [
            {"id": "node1", "ip": "127.0.0.1", "port": 8001},
            {"id": "node2", "ip": "127.0.0.1", "port": 8002}
        ]
        """
        self.nodes = {node["id"]: {**node, "status": "alive", "last_check": None} for node in nodes}
        self.replication_factor = 2
        self.task_registry = {}
        self.running = False


    async def check_node(self, node):
        try:
            reader, writer = await asyncio.open_connection(node["ip"], node["port"])
            writer.close()
            await writer.wait_closed()

            self.nodes[node["id"]]["status"] = "alive"
            self.nodes[node["id"]]["last_check"] = datetime.utcnow()

        except:
            self.nodes[node["id"]]["status"] = "dead"
            self.nodes[node["id"]]["last_check"] = datetime.utcnow()

    async def monitor_nodes(self, interval=3):
        self.running = True

        while self.running:
            tasks = []
            for node in self.nodes.values():
                tasks.append(self.check_node(node))

            await asyncio.gather(*tasks)

            self.report_status()
            await asyncio.sleep(interval)


    def report_status(self):
        print("\n📊 Estado del cluster:")
        for node_id, node in self.nodes.items():
            print(f" - {node_id}: {node['status']}")

    def get_alive_nodes(self):
        return [n for n in self.nodes.values() if n["status"] == "alive"]


    def register_task(self, task_id, data):
        alive_nodes = self.get_alive_nodes()

        if len(alive_nodes) < self.replication_factor:
            print(f"[!] No hay suficientes nodos para replicación de {task_id}")
            return

        selected_nodes = random.sample(alive_nodes, self.replication_factor)

        self.task_registry[task_id] = {
            "data": data,
            "nodes": [n["id"] for n in selected_nodes],
            "status": "replicated"
        }

        print(f"[✓] Tarea {task_id} replicada en {[n['id'] for n in selected_nodes]}")


    def recover_tasks(self):
        print("\n🔄 Verificando recuperación de tareas...")

        for task_id, task in self.task_registry.items():
            active_nodes = [
                n for n in task["nodes"]
                if self.nodes[n]["status"] == "alive"
            ]

            if len(active_nodes) < self.replication_factor:
                print(f"[!] Tarea {task_id} perdió redundancia → re-replicando...")

                available_nodes = [
                    n for n in self.get_alive_nodes()
                    if n["id"] not in active_nodes
                ]

                if available_nodes:
                    new_node = random.choice(available_nodes)
                    task["nodes"].append(new_node["id"])

                    print(f"[✓] Tarea {task_id} migrada a {new_node['id']}")


    def rebalance_load(self):
        print("\n⚖️ Rebalanceando carga...")

        alive_nodes = self.get_alive_nodes()
        if not alive_nodes:
            print("[!] No hay nodos activos")
            return

        for task_id, task in self.task_registry.items():
            assigned_nodes = task["nodes"]

            # Si hay nodos muertos → reasignar
            for node_id in assigned_nodes:
                if self.nodes[node_id]["status"] == "dead":
                    replacement = random.choice(alive_nodes)
                    task["nodes"].remove(node_id)
                    task["nodes"].append(replacement["id"])

                    print(f"[✓] Tarea {task_id} reasignada de {node_id} → {replacement['id']}")


    def simulate_failure(self, node_id):
        if node_id in self.nodes:
            self.nodes[node_id]["status"] = "dead"
            print(f"\n💥 Nodo {node_id} FALLÓ (simulación)")

    def simulate_recovery(self, node_id):
        if node_id in self.nodes:
            self.nodes[node_id]["status"] = "alive"
            print(f"\n🟢 Nodo {node_id} RECUPERADO")


    async def self_healing_loop(self, interval=5):
        while True:
            self.recover_tasks()
            self.rebalance_load()
            await asyncio.sleep(interval)


    def stop(self):
        self.running = False



if __name__ == "__main__":
    nodes = [
        {"id": "node1", "ip": "127.0.0.1", "port": 8001},
        {"id": "node2", "ip": "127.0.0.1", "port": 8002},
        {"id": "node3", "ip": "127.0.0.1", "port": 8003},
    ]

    ft = FaultToleranceManager(nodes)

    async def main():
        asyncio.create_task(ft.monitor_nodes())
        asyncio.create_task(ft.self_healing_loop())

        await asyncio.sleep(2)

        # Registrar tareas
        ft.register_task("task_1", {"type": "encryption"})
        ft.register_task("task_2", {"type": "analysis"})

        await asyncio.sleep(5)

        # Simular fallo
        ft.simulate_failure("node1")

        await asyncio.sleep(10)

        # Recuperar nodo
        ft.simulate_recovery("node1")

    asyncio.run(main())