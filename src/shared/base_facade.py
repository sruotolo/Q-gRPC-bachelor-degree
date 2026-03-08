import os
import subprocess
import time
from shared.constants import SystemMessages, ErrorMessages
from shared.rest_etsi_adapter import RestEtsiAdapter


class BaseFacade:
    """
    This is the base class for the client and the server facades, they will inherit from this class.
    It contains the logic for the creation of the network connection, the adapter and to close the active connection.
    """
    def __init__(self, local_kdc: str):
        self.local_kdc_name = local_kdc.upper()
        self.active_tunnels = []

    def setup_adapter_connection(self, primary_name: str, secondary_name: str) -> tuple[RestEtsiAdapter, RestEtsiAdapter]:
        print(SystemMessages.INIT_QKD)
        primary_adapter = self._create_adapter(primary_name, secondary_name)
        secondary_adapter = self._create_adapter(secondary_name, primary_name)
        print(SystemMessages.COMPLETED_QKD_SETUP)

        return primary_adapter, secondary_adapter

    def _create_adapter(self, local_prefix: str, partner_prefix: str) -> RestEtsiAdapter:
        # Reads the .env file, if needed it creates the ssh tunnel, and then it initializes the adapters.
        try:
            target_id = os.getenv(f"{partner_prefix}_SAE_ID")
            need_tunnel = os.getenv(f"{local_prefix}_NEED_TUNNEL") == 'True'
            local_port = int(os.getenv(f"{local_prefix}_LOCAL_PORT"))
            remote_port = int(os.getenv(f"{local_prefix}_REMOTE_PORT"))
        except (TypeError, ValueError) as e:
            raise ValueError(f"{ErrorMessages.ENV_ERROR}: {local_prefix}")

        if need_tunnel:
            print(f"{SystemMessages.START_SSH_CONNECTION}: {local_prefix}")
            bastion_ip = os.getenv(f"{local_prefix}_BASTION_IP")
            bastion_user = os.getenv(f"{local_prefix}_BASTION_USER")
            remote_ip = os.getenv(f"{local_prefix}_REMOTE_IP")
            remote_user = os.getenv(f"{local_prefix}_REMOTE_USER")
            ssh_key = os.getenv("GLOBAL_SSH_KEY")

            try:
                ssh_command = [
                    "ssh", "-N",
                    "-i", ssh_key,
                    "-J", f"{bastion_user}@{bastion_ip}",
                    f"{remote_user}@{remote_ip}",
                    "-L", f"{local_port}:127.0.0.1:{remote_port}"
                ]
                tunnel_process = subprocess.Popen(
                    ssh_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.active_tunnels.append(tunnel_process)
                time.sleep(3)
                
                self.active_tunnels.append(tunnel_process)
            except Exception as e:
                raise ConnectionError(f"{ErrorMessages.SSH_ERROR}: {local_prefix}")

            env_url = os.getenv(f"{local_prefix}_BASE_URL")
            base_url = f"{env_url}:{local_port}"
            print(f"{SystemMessages.COMPLETED_SSH_CONNECTION}: {base_url}")
        else:
            env_url = os.getenv(f"{local_prefix}_BASE_URL")
            base_url = f"{env_url}:{remote_port}"
            print(f"{SystemMessages.DIRECT_CONNECTION}: {base_url}")

        return RestEtsiAdapter(base_url, target_id)

    def close_connection(self):
        for tunnel_process in self.active_tunnels:
            tunnel_process.terminate()
        print(f"{SystemMessages.SSH_CLOSED}")