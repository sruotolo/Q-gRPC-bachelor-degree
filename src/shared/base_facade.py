import os
from sshtunnel import SSHTunnelForwarder
import rest_etsi_adapter
from constants import SystemMessages

class BaseFacade:
    """
    This is the base class for the client and the server facades, they will inherit from this class.
    It contains the logic for the creation of the network connection, the adapter and to close the active connection.
    """
    def __init__(self, local_kdc_ip: str):
        self.local_kdc_ip = local_kdc_ip.upper()
        self.active_tunnels = []

        self.primary_adapter = None
        self.secondary_adapter = None

    def setup_network_connection(self, primary_ip: str, secondary_ip: str):
        print(SystemMessages.INIT_QKD)
        self.primary_adapter = self._create_adapter(primary_ip)
        self.secondary_adapter = self._create_adapter(secondary_ip)
        print(SystemMessages.COMPLETED_QKD_SETUP)

    def _create_adapter(self, prefix: str):
        # Reads the .env file, if needed it creates the ssh tunnel, and then it initializes the adapters.

        target_id = os.getenv(f"{prefix}_SAE_ID")
        need_tunnel = os.getenv(f"{prefix}_SAE_NEED_TUNNEL") == 'True'
        local_port = int(os.getenv(f"{prefix}_LOCAL_PORT"))
        remote_port = int(os.getenv(f"{prefix}_REMOTE_PORT"))

        if need_tunnel:
            print(f"{SystemMessages.START_SSH_CONNECTION}: {prefix}")
            bastion_ip = os.getenv(f"{prefix}_BASTION_IP")
            bastion_user = os.getenv(f"{prefix}_BASTION_USER")
            remote_ip = os.getenv(f"{prefix}_REMOTE_IP")
            ssh_key = os.getenv(f"GLOBAL_SSH_KEY")

            tunnel = SSHTunnelForwarder(
                (bastion_ip, 22),
                ssh_username=bastion_user,
                ssh_password=ssh_key,
                local_bind_address=('127.0.0.1', local_port),
                remote_bind_address=(remote_ip, remote_port),
            )
            tunnel.start()
            self.active_tunnels.append(tunnel)

            env_url = os.getenv(f"{prefix}_BASE_URL")
            base_url = os.getenv(f"{env_url}:{local_port}")
            print(f"{SystemMessages.COMPLETED_SSH_CONNECTION}: {base_url}")
        else:
            env_url = os.getenv(f"{prefix}_BASE_URL")
            base_url = f"{env_url}:{remote_port}"
            print(f"{SystemMessages.DIRECT_CONNECTION}: {base_url}")

        return rest_etsi_adapter.RestEtsiAdapter(base_url, target_id)

    def close_connection(self):
        for tunnel in self.active_tunnels:
            tunnel.stop()
        print(f"{SystemMessages.SSH_CLOSED}")