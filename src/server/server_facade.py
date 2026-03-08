import uuid
import requests
import grpc
import qkd_pb2
from qkd_pb2 import NetworkTopologyRequest, NetworkTopologyResponse
from qkd_pb2 import ButterflySyncRequest, ButterflySyncResponse
from qkd_pb2 import DataRequest, DataResponse
from qkd_pb2_grpc import QKDOrchestratorServiceServicer
from shared.base_facade import BaseFacade
from shared.constants import SystemNames, SystemMessages, KdcNames, ErrorMessages, QKD_TOPOLOGY
from shared import crypto_utils

class ServerFacade(BaseFacade, QKDOrchestratorServiceServicer):
    """
    It inherits from BaseFacade the methods for the network and adapter initialization.
    It adds all the encryption/decryption logic and the gRPC logic using a dictionary of active sessions that is used
    to manage the multi-client case.
    """
    def __init__(self):
        BaseFacade.__init__(self, SystemNames.QKD_ORCHESTRATOR)

        self.active_session = {}

    # Negotiate the network topology with the client who asked for a connection only knowing his local kdc.
    # The server facade answers to the client with the connected partner kdc and a uuid for identification.
    # The server facade then prepare its own adapter.
    def NegotiateNetworkTopology(self, request: NetworkTopologyRequest, context: grpc.ServicerContext) -> NetworkTopologyResponse:
        client_kdc_name = request.client_kdc
        print(f"{SystemMessages.TOPOLOGY_REQUEST}: {client_kdc_name}")

        partner_kdc_name = QKD_TOPOLOGY.get(client_kdc_name)
        if not partner_kdc_name:
            context.abort(grpc.StatusCode.NOT_FOUND, ErrorMessages.CLIENT_KDC_NOT_FOUND)

        print(f"{SystemMessages.TOPOLOGY_DONE}: {client_kdc_name} <-> {partner_kdc_name}")
        client_adapter, partner_adapter = self.setup_adapter_connection(client_kdc_name, partner_kdc_name)

        # Memorize the session ID of the client in a dictionary to remember clients.
        session_id = str(uuid.uuid4())
        self.active_session[session_id] = {
            "session_key": None,
            "client_adapter": client_adapter,
            "partner_adapter": partner_adapter
        }

        print(f"{SystemMessages.TOPOLOGY_DONE}: {session_id}")
        return NetworkTopologyResponse(partner_kdc=partner_kdc_name, session_id=session_id)

    # Butterfly protocol on server side.
    def ButterflySynchronization(self, request: ButterflySyncRequest, context: grpc.ServicerContext) -> ButterflySyncResponse:
        # Check if the client is logged.
        session_id = request.session_id
        if session_id not in self.active_session:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, ErrorMessages.CLIENT_UNAUTHENTICATED)

        # Create server adapters to communicate with the KDCs to get the key.
        print(SystemMessages.BUTTERFLY_SERVER)
        client_adapter = self.active_session[session_id]["client_adapter"]
        partner_adapter = self.active_session[session_id]["partner_adapter"]

        # Define the left and right part of the key and the left and right part of the hash.
        # This is needed to be sure that the key is correctly built.
        keys = {}
        hashes = {}
        try:
            for adapter in [client_adapter, partner_adapter]:
                part_of_key, key_half_bytes, other_hash_bytes = adapter.retrieve_key(request.key_id)

                keys[part_of_key] = key_half_bytes

                other_part_of_key = "RIGHT" if part_of_key.upper() == 'LEFT' else "LEFT"
                hashes[other_part_of_key] = other_hash_bytes
        except requests.exceptions.RequestException as e:
            print(ErrorMessages.NETWORK_CONNECTION_ERROR)
            context.abort(grpc.StatusCode.UNAVAILABLE, str(e))

        try:
            # Check if both KDCs has answered.
            if "LEFT" not in keys or "RIGHT" not in keys:
                context.abort(grpc.StatusCode.INTERNAL, ErrorMessages.MISSING_KEY)

            # Cross-validation of hashes and keys.
            if (crypto_utils.sha256_hash(keys["LEFT"]) != request.hash_key_L or
                    crypto_utils.sha256_hash(keys["RIGHT"]) != request.hash_key_R):
                context.abort(grpc.StatusCode.PERMISSION_DENIED, ErrorMessages.VALIDATION_CLIENT_SERVER_ERROR)

            if (crypto_utils.sha256_hash(keys["LEFT"]) != hashes["LEFT"] or
                    crypto_utils.sha256_hash(keys["RIGHT"]) != hashes["RIGHT"]):
                context.abort(grpc.StatusCode.PERMISSION_DENIED, ErrorMessages.VALIDATION_KDC_SERVER_ERROR)

            full_key_bytes = keys["LEFT"] + keys["RIGHT"]
            self.active_session[session_id]["session_key"] = full_key_bytes

            hash_full_key = crypto_utils.sha256_hash(full_key_bytes)

            print(SystemMessages.BUTTERFLY_COMPLETED)
            return qkd_pb2.ButterflySyncResponse(success=True, hash_full_key=hash_full_key)
        except Exception as e:
            print(f"{ErrorMessages.SYNC_ERROR}: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    # Data exchange using encryption and decryption.
    def DataExchange(self, request: DataRequest, context: grpc.ServicerContext) -> DataResponse:
        # Check if the client is logged.
        session_id = request.session_id
        if session_id not in self.active_session:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, ErrorMessages.CLIENT_UNAUTHENTICATED)

        # Check if the client has already done the butterfly protocol.
        session_key = self.active_session[session_id]["session_key"]
        if not session_key:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, ErrorMessages.BUTTERFLY_ERROR)

        try:
            decrypted_request_bytes = crypto_utils.aes_gcm_decrypt(
                ciphertext=request.encrypted_request_payload,
                nonce=request.nonce,
                tag=request.tag,
                key=session_key
            )

            plain_request = decrypted_request_bytes.decode('utf-8')
            print(f"{SystemMessages.MESSAGE_RECEIVED} from {request.session_id} -> {plain_request}")

            plain_response = f"{SystemMessages.SERVER_RESPONSE}"
            if not plain_request:
                plain_response = f"{SystemMessages.SERVER_RESPONSE_TO_BLANK_MESSAGE}"

            response_nonce_bytes, response_tag_bytes, encrypted_response_bytes = crypto_utils.aes_gcm_encrypt(
                plaintext=plain_response.encode('utf-8'),
                key=session_key,
            )

            del self.active_session[session_id]

            return qkd_pb2.DataResponse(
                encrypted_response_payload=encrypted_response_bytes,
                nonce=response_nonce_bytes,
                tag=response_tag_bytes,
            )
        except Exception as e:
            print(f"{ErrorMessages.EXCHANGE_ERROR}: {e}")
            context.abort(grpc.StatusCode.PERMISSION_DENIED, str(e))