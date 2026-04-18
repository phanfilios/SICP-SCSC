import os
import hashlib
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import secrets

class CryptoEngine:
    def __init__(self):
        self.backend = "SCSC_CRYPTO_CORE_v1"

  
    def derive_key(self, password: str, salt: bytes = None):
        if salt is None:
            salt = os.urandom(16)

        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
        )

        key = kdf.derive(password.encode())
        return key, salt


    def encrypt(self, key: bytes, plaintext: str):
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

        return {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode()
        }

    def decrypt(self, key: bytes, nonce_b64: str, ciphertext_b64: str):
        aesgcm = AESGCM(key)

        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()


    def hash_data(self, data: str):
        digest = hashlib.sha3_256(data.encode()).hexdigest()
        return digest


    def generate_keypair(self):
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        return private_key, public_key

    def sign_data(self, private_key, data: str):
        signature = private_key.sign(data.encode())
        return base64.b64encode(signature).decode()

    def verify_signature(self, public_key, data: str, signature_b64: str):
        signature = base64.b64decode(signature_b64)
        try:
            public_key.verify(signature, data.encode())
            return True
        except:
            return False


    def export_private_key(self, private_key):
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def export_public_key(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )


    def generate_lattice_key(self, dimension=256):
        # Simulación conceptual
        return [secrets.randbelow(1000) for _ in range(dimension)]

    def lattice_encrypt(self, message: str, key):
        encoded = [ord(c) + key[i % len(key)] for i, c in enumerate(message)]
        return encoded

    def lattice_decrypt(self, ciphertext, key):
        decoded = ''.join(chr(ciphertext[i] - key[i % len(key)]) for i in range(len(ciphertext)))
        return decoded


    def generate_secure_token(self):
        return secrets.token_hex(32)


    def secure_package(self, key, private_key, message: str):
        encrypted = self.encrypt(key, message)
        signature = self.sign_data(private_key, message)

        package = {
            "payload": encrypted,
            "signature": signature
        }

        return json.dumps(package)

    def unpack_secure_package(self, key, public_key, package_json):
        package = json.loads(package_json)

        decrypted = self.decrypt(
            key,
            package["payload"]["nonce"],
            package["payload"]["ciphertext"]
        )

        valid = self.verify_signature(
            public_key,
            decrypted,
            package["signature"]
        )

        return decrypted, valid



if __name__ == "__main__":
    crypto = CryptoEngine()

    # Derivar clave
    key, salt = crypto.derive_key("clave_super_segura")

    # Generar claves de firma
    priv, pub = crypto.generate_keypair()

    # Mensaje
    msg = "Sistema SCSC activo"

    # Empaquetar
    package = crypto.secure_package(key, priv, msg)
    print("\n📦 PAQUETE:", package)

    # Desempaquetar
    decrypted, valid = crypto.unpack_secure_package(key, pub, package)

    print("\n🔓 MENSAJE:", decrypted)
    print("✅ FIRMA VÁLIDA:", valid)

    # Lattice (simulación)
    lattice_key = crypto.generate_lattice_key()
    enc = crypto.lattice_encrypt(msg, lattice_key)
    dec = crypto.lattice_decrypt(enc, lattice_key)

    print("\n⚛️ LATTICE:", dec)