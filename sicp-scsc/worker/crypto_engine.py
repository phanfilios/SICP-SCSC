from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Dict

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
except Exception:  # pragma: no cover
    AESGCM = None
    Scrypt = None


class CryptoEngine:
    def derive_key(self, secret: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        salt = salt or os.urandom(16)
        if Scrypt is None:
            key = hashlib.sha3_256(secret.encode("utf-8") + salt).digest()
            return key, salt

        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        return kdf.derive(secret.encode("utf-8")), salt

    def encrypt(self, key: bytes, plaintext: str) -> Dict[str, str]:
        nonce = os.urandom(12)
        if AESGCM is None:
            plain = plaintext.encode("utf-8")
            ciphertext = bytes([b ^ key[i % len(key)] for i, b in enumerate(plain)])
        else:
            ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
        return {
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        }

    def decrypt(self, key: bytes, payload: Dict[str, str]) -> str:
        nonce = base64.b64decode(payload["nonce"])
        ciphertext = base64.b64decode(payload["ciphertext"])
        if AESGCM is None:
            plain = bytes([b ^ key[i % len(key)] for i, b in enumerate(ciphertext)])
        else:
            plain = AESGCM(key).decrypt(nonce, ciphertext, None)
        return plain.decode("utf-8")

    def hash_integrity(self, data: str) -> str:
        return hashlib.sha3_256(data.encode("utf-8")).hexdigest()

    def key_distribution(self) -> Dict[str, str]:
        pseudo_lattice_key = [secrets.randbelow(4096) for _ in range(32)]
        serialized = ",".join(map(str, pseudo_lattice_key))
        return {
            "key_id": secrets.token_hex(8),
            "algorithm": "lattice-inspired-sim",
            "fingerprint": self.hash_integrity(serialized)[:24],
        }

    def crypto_operation(self, data: str) -> Dict[str, str]:
        key, salt = self.derive_key("scsc-cluster-secret")
        encrypted = self.encrypt(key, data)
        integrity = self.hash_integrity(data)
        return {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "integrity": integrity,
            **encrypted,
        }
