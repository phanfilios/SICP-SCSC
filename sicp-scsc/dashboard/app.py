from __future__ import annotations

import argparse
import asyncio
import json


async def query_master(host: str, port: int) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    writer.write((json.dumps({"type": "heartbeat", "source": "dashboard", "payload": {}}) + "\n").encode())
    await writer.drain()
    response = await reader.readline()
    print(response.decode().strip())
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCSC minimal dashboard probe")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    asyncio.run(query_master(args.host, args.port))
