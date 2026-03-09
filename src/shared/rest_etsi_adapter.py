import base64
import requests
from src.shared.constants import ErrorMessages

class RestEtsiAdapter:
    """
    Adapter for the standard ETSI QKD 014.
    It receives the URL to which to send the request and the ID of the target device.
    It forwards the REST request in the ETSI QKD 014 standard to the QKDs.
    """
    def __init__(self, base_url: str, target_id: str):
        self.url = f"{base_url}/api/v1/keys"
        self.target_id = target_id
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def generate_key(self, size: int = 256) -> tuple[str, str, bytes, bytes]:
        url = f"{self.url}/{self.target_id}/enc_keys"
        payload = {"number": 1, "size": size}

        try:
            response = requests.post(url, verify=False, json=payload, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            part_of_key = data["part_of_key"]
            key_id = data["key_ID"]
            key_half_bytes = base64.b64decode(data["key_half_b64"])
            other_half_bytes = base64.b64decode(data["other_half_hash_b64"])

            return part_of_key, key_id, key_half_bytes, other_half_bytes

        except requests.exceptions.RequestException as e:
            print(f"{ErrorMessages.GENERATION_ADAPTER_ERROR}: {e}")
            raise

    def retrieve_key(self, key_id: str) -> tuple[str, bytes, bytes]:
        url = f"{self.url}/{self.target_id}/dec_keys"
        payload = {"key_IDs": [{"key_ID": key_id}]}

        try:
            response = requests.post(url, verify=False, json=payload, headers=self.headers, timeout=5)

            response.raise_for_status()
            data = response.json()

            part_of_key = data["part_of_key"]
            key_half_bytes = base64.b64decode(data["key_half_b64"])
            other_half_bytes = base64.b64decode(data["other_half_hash_b64"])

            return part_of_key, key_half_bytes, other_half_bytes

        except requests.exceptions.RequestException as e:
            print(f"{ErrorMessages.RECOVERY_ADAPTER_ERROR}: {e}")
            raise