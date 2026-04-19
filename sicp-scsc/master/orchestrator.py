from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Dict, List

from master.scheduler import TaskScheduler
from network.traffic_simulation import TrafficSimulator
from quantum.quantum_simulator import QuantumSimulator
from recovery.fault_tolerance import FaultToleranceManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ClusterOrchestrator:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000) -> None:
        self.host = host
        self.port = port
        self.scheduler = TaskScheduler()
        self.faults = FaultToleranceManager()
        self.traffic = TrafficSimulator()
        self.quantum = QuantumSimulator()
        self.node_load: Dict[str, int] = {}
        self.results: List[Dict] = []
        self._worker_endpoints: Dict[str, tuple[str, int]] = {}

    async def handle_node(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info("peername")
        raw = await reader.readline()
        if not raw:
            writer.close()
            await writer.wait_closed()
            return

        message = json.loads(raw.decode("utf-8"))
        msg_type = message.get("type")
        node_id = message.get("source", f"{addr[0]}:{addr[1]}")

        if msg_type == "register":
            node_port = message["payload"]["port"]
            self.faults.register(node_id, addr[0], node_port)
            self.node_load.setdefault(node_id, 0)
            self._worker_endpoints[node_id] = (addr[0], node_port)
            self.scheduler.refresh_nodes(self.faults.alive_nodes())
            response = {"status": "ok", "registered": node_id}

        elif msg_type == "heartbeat":
            self.faults.heartbeat(node_id)
            response = {"status": "ok", "alive_nodes": self.faults.alive_nodes()}

        elif msg_type == "result":
            payload = message.get("payload", {})
            self.results.append(payload)
            self.node_load[node_id] = max(0, self.node_load.get(node_id, 1) - 1)
            response = {"status": "stored", "results": len(self.results)}

        else:
            response = {"status": "error", "reason": "unknown message type"}

        writer.write((json.dumps(response) + "\n").encode("utf-8"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def send_task(self, node_id: str, task: Dict) -> Dict:
        host, port = self._worker_endpoints[node_id]
        reader, writer = await asyncio.open_connection(host, port)
        writer.write((json.dumps(task) + "\n").encode("utf-8"))
        await writer.drain()
        response = await reader.readline()
        writer.close()
        await writer.wait_closed()
        return json.loads(response.decode("utf-8"))

    async def dispatch_loop(self) -> None:
        task_types = [
            "quantum_simulation",
            "crypto_operation",
            "attack_response",
            "key_distribution",
            "status",
        ]
        attack_toggle = False

        while True:
            failed = self.faults.evaluate()
            if failed:
                logging.warning("Detected failed nodes: %s", failed)
                self.scheduler.refresh_nodes(self.faults.alive_nodes())

            if not self.faults.alive_nodes():
                await asyncio.sleep(1)
                continue

            task = {
                "type": task_types[int(time.time()) % len(task_types)],
                "payload": {
                    "message": "cluster-cycle",
                    "traffic": self.traffic.sample(under_attack=attack_toggle),
                    "quantum_hint": self.quantum.simulate_bb84_round(8),
                },
            }
            attack_toggle = not attack_toggle
            self.scheduler.enqueue(task)

            pending = self.scheduler.next_task()
            if pending is None:
                await asyncio.sleep(0.5)
                continue

            node_id = self.scheduler.select_node(self.node_load)
            if node_id is None:
                await asyncio.sleep(0.5)
                continue

            self.node_load[node_id] = self.node_load.get(node_id, 0) + 1
            response = await self.send_task(node_id, pending)
            logging.info("Task %s -> %s: %s", pending["type"], node_id, response)
            await asyncio.sleep(1)

    async def run(self) -> None:
        server = await asyncio.start_server(self.handle_node, self.host, self.port)
        logging.info("Master listening on %s:%s", self.host, self.port)
        async with server:
            await asyncio.gather(server.serve_forever(), self.dispatch_loop())


if __name__ == "__main__":
    asyncio.run(ClusterOrchestrator().run())
