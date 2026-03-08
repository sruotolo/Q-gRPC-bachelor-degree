import grpc
import qkd_pb2
import qkd_pb2_grpc
from shared.base_facade import BaseFacade
from shared.constants import SystemMessages, ErrorMessages
from shared.rest_etsi_adapter import RestEtsiAdapter
from shared import crypto_utils as crypto_utils

class ClientFacade(BaseFacade):
    """
    It inherits from BaseFacade the methods for the network and adapter initialization.
    It adds all the encryption/decryption logic and the gRPC logic
    """
    def __init__(self, local_kdc_name: str, server_address: str = 'localhost:50051',
                 ca_cert_path: str = None,
                 client_cert_path: str = None, client_key_path: str = None):

        super().__init__(local_kdc_name)

        self.local_kdc_name = local_kdc_name.upper()
        self.server_address = server_address

        self.ca_cert_path = ca_cert_path
        self.client_cert_path = client_cert_path
        self.client_key_path = client_key_path

        self.session_id = None
        self.session_key = None
        self.channel = None
        self.stub: qkd_pb2_grpc.QKDOrchestratorServiceStub | None = None

    # Private method to create the channel and the stub.
    def _setup_channel_and_stub(self):
        # Using mTLS if the client has the certificates.
        if self.ca_cert_path and self.client_cert_path and self.client_key_path:
            try:
                print(SystemMessages.MTLS_ACTIVATED)

                with open(self.ca_cert_path, "rb") as ca:
                    ca_cert = ca.read()
                with open(self.client_cert_path, "rb") as cert:
                    client_cert = cert.read()
                with open(self.client_key_path, "rb") as key:
                    client_key = key.read()

                credentials = grpc.ssl_channel_credentials(
                    root_certificates=ca_cert,
                    private_key=client_key,
                    certificate_chain=client_cert
                )

                self.channel = grpc.secure_channel(self.server_address, credentials)
                print(SystemMessages.CHANNEL_CREATED)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"{ErrorMessages.CERT_NOT_FOUND}: {e}")
            except Exception as e:
                raise RuntimeError(f"{ErrorMessages.GENERIC_ERROR}: {e}")
        else:
            # If the client doesn't have the certificates use an insecure channel without certification.
            print(SystemMessages.INSECURE_CHANNEL_ACTIVATED)
            self.channel = grpc.insecure_channel(self.server_address)

        self.stub = qkd_pb2_grpc.QKDOrchestratorServiceStub(self.channel)

    # Private method to negotiate the network topology with the Server.
    def _negotiate_network_topology(self):
        print(f"{SystemMessages.NETWORK_NEGOTIATION_STARTED}: {self.local_kdc_name}")
        request = qkd_pb2.NetworkTopologyRequest(client_kdc=self.local_kdc_name)
        response = self.stub.NegotiateNetworkTopology(request)

        self.session_id = response.session_id
        partner_kdc_name = response.partner_kdc.upper()

        # Call to the base facade adapter building method to create the connection to the KDCs.
        print(f"{SystemMessages.NETWORK_NEGOTIATION_DONE}: {partner_kdc_name}")
        return self.setup_adapter_connection(self.local_kdc_name, partner_kdc_name)

    # Butterfly protocol on client side.
    def _butterfly_synchronization(self, local_adapter: RestEtsiAdapter, partner_adapter: RestEtsiAdapter):
        keys = {}
        hashes = {}
        try:
            # Retrieve the key from both KDCs.
            print(SystemMessages.BUTTERFLY_CLIENT)
            local_part_of_key, key_id, local_half, local_hash = local_adapter.generate_key()
            keys[local_part_of_key] = local_half
            other_part_of_key = "RIGHT" if local_part_of_key.upper() == 'LEFT' else "LEFT"
            hashes[other_part_of_key] = local_hash

            partner_part_of_key, partner_half, partner_hash = partner_adapter.retrieve_key(key_id)
            keys[partner_part_of_key] = partner_half
            other_part = "RIGHT" if partner_part_of_key.upper() == 'LEFT' else "LEFT"
            hashes[other_part] = partner_hash

            # Check if both KDCs has answered.
            if "LEFT" not in keys or "RIGHT" not in keys:
                raise ValueError(ErrorMessages.MISSING_KEYS)

            # Cross-validation of keys and hashes.
            if (crypto_utils.sha256_hash(keys["LEFT"]) != hashes["LEFT"] or
                    crypto_utils.sha256_hash(keys["RIGHT"]) != hashes["RIGHT"]):
                raise PermissionError(ErrorMessages.VALIDATION_FAILED_BUTTERFLY)

            full_key_bytes = keys["LEFT"] + keys["RIGHT"]

            # Synchronization with the server.
            print(SystemMessages.KEY_SYNC)
            sync_request = qkd_pb2.ButterflySyncRequest(
                session_id=self.session_id,
                key_id=key_id,
                hash_key_L=hashes["LEFT"],
                hash_key_R=hashes["RIGHT"],
            )

            # Cross-validation with the server.
            sync_response = self.stub.ButterflySynchronization(sync_request)
            if not sync_response.success or sync_response.hash_full_key != crypto_utils.sha256_hash(full_key_bytes):
                raise PermissionError(ErrorMessages.SYNC_FAILED_BUTTERFLY)

            self.session_key = full_key_bytes
        except grpc.RpcError as e:
            raise ConnectionError(f"{ErrorMessages.GRPC_ERROR}: {e}")
        except Exception as e:
            raise RuntimeError(f"{ErrorMessages.GENERIC_ERROR}: {e}")

    # Start the connection, create the adapters and start the butterfly protocol.
    def setup_connection_and_synchronization(self) -> bool:
        try:
            self._setup_channel_and_stub()
            local_adapter, partner_adapter = self._negotiate_network_topology()
            self._butterfly_synchronization(local_adapter, partner_adapter)

            print(SystemMessages.CONNECTION_COMPLETED)
            return True
        except Exception as e:
            print(f"{ErrorMessages.CONNECTION_ERROR}: {e}")
            return False

    def send_message(self, plain_message: str) -> str:
        if not self.session_id or not self.session_key:
            raise RuntimeError(ErrorMessages.FAILED_MESSAGE)

        try:
            nonce, tag, ciphertext = crypto_utils.aes_gcm_encrypt(
                plaintext=plain_message.encode('utf-8'),
                key=self.session_key
            )

            message = qkd_pb2.DataRequest(
                session_id=self.session_id,
                encrypted_request_payload=ciphertext,
                nonce=nonce,
                tag=tag
            )

            response = self.stub.DataExchange(message)

            decrypted_response = crypto_utils.aes_gcm_decrypt(
                ciphertext=response.encrypted_response_payload,
                nonce=response.nonce,
                tag=response.tag,
                key=self.session_key
            )

            return decrypted_response.decode('utf-8')
        except grpc.RpcError as e:
            return f"{ErrorMessages.NETWORK_ERROR}: {e}"
        except ValueError as e:
            return f"{ErrorMessages.CRYPTOGRAPHIC_ERROR}: {e}"
        except Exception as e:
            return f"{ErrorMessages.CLIENT_BUG}: {e}"