# SCSC — Sistema de Ciberseguridad Cuántica Experimental

Prototype of a distributed cybersecurity platform that simulates quantum-inspired defense over classical infrastructure.

## Implemented architecture

- **Master Node**: async orchestrator, task scheduler, heartbeat tracking, task aggregation.
- **Worker Nodes**: execute task types (`quantum_simulation`, `crypto_operation`, `attack_response`, `key_distribution`, `status`).
- **Fault tolerance**: heartbeat timeout detection and automatic node availability management.
- **Traffic simulation**: synthetic latency/throughput/packet-loss metrics (normal vs attack mode).
- **Quantum simulation**: BB84-inspired key sifting + Bell-state statevector demo (Qiskit when available).

## Repository layout

- `sicp-scsc/master/orchestrator.py`
- `sicp-scsc/master/scheduler.py`
- `sicp-scsc/worker/worker_node.py`
- `sicp-scsc/worker/crypto_engine.py`
- `sicp-scsc/worker/attack_simulator.py`
- `sicp-scsc/recovery/fault_tolerance.py`
- `sicp-scsc/network/traffic_simulation.py`
- `sicp-scsc/quantum/quantum_simulator.py`

## Run locally (single machine simulation)

```bash
cd sicp-scsc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1: master
python -m master.orchestrator

# Terminal 2..N: workers
python -m worker.worker_node --node-id worker-1 --port 9101
python -m worker.worker_node --node-id worker-2 --port 9102
python -m worker.worker_node --node-id worker-3 --port 9103
```

## Notes

- Designed for Ubuntu deployment in a LAN cluster.
- No quantum hardware required; all quantum behavior is simulated.
- Modules are intentionally decoupled for future extensibility.
