import hashlib
import json

class HashService:
    """Genera huellas dactilares de los inputs para evitar cálculos redundantes."""

    @staticmethod
    def compute_hash(data: dict) -> str:
        """Crea un hash SHA-256 de un diccionario de inputs."""
        encoded_data = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(encoded_data).hexdigest()