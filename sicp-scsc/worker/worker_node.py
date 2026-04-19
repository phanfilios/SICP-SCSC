from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Dict

from quantum.quantum_simulator import QuantumSimulator
from worker.attack_simulator import AttackSimulator
from worker.crypto_engine import CryptoEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class WorkerNode:
    def __init__(self, node_id: str, host: str, port: int, master_host: str, master_port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.master_host = master_host
        self.master_port = master_port
        self.crypto = CryptoEngine()
        self.attack = AttackSimulator()
        self.quantum = QuantumSimulator()

    async def send_to_master(self, message: Dict) -> Dict:
        reader, writer = await asyncio.open_connection(self.master_host, self.master_port)
        writer.write((json.dumps(message) + "\n").encode("utf-8"))
        await writer.drain()
        response = await reader.readline()
        writer.close()
        await writer.wait_closed()
        return json.loads(response.decode("utf-8"))

    async def register(self) -> None:
        response = await self.send_to_master(
            {
                "type": "register",
                "source": self.node_id,
                "payload": {"port": self.port},
            }
        )
        logging.info("Registered: %s", response)

    async def heartbeat_loop(self) -> None:
        while True:
            await self.send_to_master({"type": "heartbeat", "source": self.node_id, "payload": {}})
            await asyncio.sleep(2)

    async def execute_task(self, task: Dict) -> Dict:
        task_type = task.get("type")
        payload = task.get("payload", {})

        if task_type == "quantum_simulation":
            result = self.quantum.statevector_demo().__dict__
        elif task_type == "crypto_operation":
            result = self.crypto.crypto_operation(payload.get("message", "scsc"))
        elif task_type == "attack_response":
            result = self.attack.evaluate("mitm")
        elif task_type == "key_distribution":
            result = self.crypto.key_distribution()
        else:
            result = {"status": "ok", "node": self.node_id, "load": "nominal"}

        await self.send_to_master(
            {
                "type": "result",
                "source": self.node_id,
                "payload": {"task_type": task_type, "result": result},
            }
        )
        return {"accepted": True, "task_type": task_type}

    async def handle_master(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        raw = await reader.readline()
        task = json.loads(raw.decode("utf-8"))
        response = await self.execute_task(task)
        writer.write((json.dumps(response) + "\n").encode("utf-8"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run(self) -> None:
        await self.register()
        server = await asyncio.start_server(self.handle_master, self.host, self.port)
        logging.info("Worker %s listening on %s:%s", self.node_id, self.host, self.port)
        async with server:
            await asyncio.gather(server.serve_forever(), self.heartbeat_loop())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--master-host", default="127.0.0.1")
    parser.add_argument("--master-port", type=int, default=9000)
    args = parser.parse_args()

    asyncio.run(
        WorkerNode(
            node_id=args.node_id,
            host=args.host,
            port=args.port,
            master_host=args.master_host,
            master_port=args.master_port,
        ).run()
    )
