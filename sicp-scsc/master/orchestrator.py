import socket
import threading
import json
import time
import random


NODES = [
    {"host": "192.168.1.101", "port": 5000},
    {"host": "192.168.1.102", "port": 5000},
    {"host": "192.168.1.103", "port": 5000},
    {"host": "192.168.1.104", "port": 5000},
    {"host": "192.168.1.105", "port": 5000},
]

MASTER_LOG = []



def send_task(node, task):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((node["host"], node["port"]))
        s.send(json.dumps(task).encode())
        response = s.recv(4096).decode()
        s.close()
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "error": str(e)}



def monitor_nodes():
    while True:
        print("\n[MONITOR] Estado del cluster:")
        for node in NODES:
            response = send_task(node, {"type": "status"})
            print(f"{node['host']} -> {response}")
        time.sleep(5)



def simulate_attack():
    attack_types = ["DDoS", "Intrusion", "Data Corruption"]
    while True:
        time.sleep(random.randint(10, 20))

        target = random.choice(NODES)
        attack = random.choice(attack_types)

        print(f"\n[ATAQUE] {attack} detectado en {target['host']}")

        task = {
            "type": "attack",
            "attack_type": attack
        }

        response = send_task(target, task)

        MASTER_LOG.append({
            "node": target["host"],
            "attack": attack,
            "response": response,
            "timestamp": time.time()
        })


def global_defense():
    while True:
        time.sleep(15)

        if len(MASTER_LOG) > 0:
            last_event = MASTER_LOG[-1]

            print("\n[DEFENSA GLOBAL] Coordinando respuesta...")

            for node in NODES:
                task = {
                    "type": "defense_sync",
                    "origin": last_event["node"],
                    "attack": last_event["attack"]
                }
                send_task(node, task)



def main():
    print("=== SCSC ORCHESTRATOR INICIADO ===")

    threading.Thread(target=monitor_nodes, daemon=True).start()
    threading.Thread(target=simulate_attack, daemon=True).start()
    threading.Thread(target=global_defense, daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()