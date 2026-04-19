from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except Exception:  # pragma: no cover - optional dependency at runtime
    QuantumCircuit = None
    Statevector = None


@dataclass
class QuantumResult:
    basis: str
    bitstring: str
    fidelity: float


class QuantumSimulator:
    """Quantum-inspired primitives used by SCSC tasks."""

    def simulate_bb84_round(self, num_bits: int = 16) -> Dict[str, List[int]]:
        alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
        alice_bases = [random.randint(0, 1) for _ in range(num_bits)]
        bob_bases = [random.randint(0, 1) for _ in range(num_bits)]

        bob_bits: List[int] = []
        for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases):
            if a_basis == b_basis:
                bob_bits.append(bit)
            else:
                bob_bits.append(random.randint(0, 1))

        sifted_key = [
            a for a, ab, bb in zip(alice_bits, alice_bases, bob_bases) if ab == bb
        ]

        return {
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_bits": bob_bits,
            "sifted_key": sifted_key,
        }

    def statevector_demo(self) -> QuantumResult:
        if QuantumCircuit is None or Statevector is None:
            return QuantumResult(basis="fallback", bitstring="00", fidelity=1.0)

        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        state = Statevector.from_instruction(circuit)

        probs = state.probabilities_dict()
        winner = max(probs, key=probs.get)
        return QuantumResult(basis="bell", bitstring=winner, fidelity=float(probs[winner]))
