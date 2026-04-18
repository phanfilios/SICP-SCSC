import threading
import time
import queue
import random


MAX_LOAD_PER_NODE = 5

# Simulación de estado de nodos
node_status = {
    "192.168.1.101": {"load": 0},
    "192.168.1.102": {"load": 0},
    "192.168.1.103": {"load": 0},
    "192.168.1.104": {"load": 0},
    "192.168.1.105": {"load": 0},
}



high_priority_queue = queue.Queue()
medium_priority_queue = queue.Queue()
low_priority_queue = queue.Queue()



def select_node():
    # Selecciona nodo con menor carga
    available_nodes = sorted(node_status.items(), key=lambda x: x[1]["load"])

    for node, status in available_nodes:
        if status["load"] < MAX_LOAD_PER_NODE:
            return node

    return None  # todos saturados



def assign_task(task, priority="medium"):
    if priority == "high":
        high_priority_queue.put(task)
    elif priority == "medium":
        medium_priority_queue.put(task)
    else:
        low_priority_queue.put(task)



def process_task(task):
    node = select_node()

    if not node:
        print("[SCHEDULER] No hay nodos disponibles, reintentando...")
        time.sleep(2)
        return False

    # Simular asignación
    node_status[node]["load"] += 1

    print(f"[SCHEDULER] Tarea {task['type']} asignada a {node}")

    # Simulación de ejecución
    threading.Thread(target=execute_task, args=(node, task)).start()

    return True



def execute_task(node, task):
    execution_time = random.uniform(1, 5)
    time.sleep(execution_time)

    print(f"[NODE {node}] completó tarea {task['type']}")

    node_status[node]["load"] -= 1



def scheduler_loop():
    while True:
        try:
            if not high_priority_queue.empty():
                task = high_priority_queue.get()
                process_task(task)

            elif not medium_priority_queue.empty():
                task = medium_priority_queue.get()
                process_task(task)

            elif not low_priority_queue.empty():
                task = low_priority_queue.get()
                process_task(task)

            else:
                time.sleep(1)

        except Exception as e:
            print(f"[ERROR SCHEDULER] {e}")



def generate_random_tasks():
    task_types = ["scan", "attack_response", "data_recovery"]

    while True:
        time.sleep(random.randint(3, 8))

        task = {
            "type": random.choice(task_types)
        }

        priority = random.choice(["high", "medium", "low"])

        print(f"[NEW TASK] {task['type']} ({priority})")

        assign_task(task, priority)



def main():
    print("=== SCHEDULER SCSC INICIADO ===")

    threading.Thread(target=scheduler_loop, daemon=True).start()
    threading.Thread(target=generate_random_tasks, daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()