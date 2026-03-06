from enum import Enum

# Error messages used in the program so we don't write string in the code.
class ErrorMessages(str, Enum):
    # Adapter.
    SECURITY_BREACH = "SECURITY ERROR: the payload has been altered"
    GENERATION_ADAPTER_ERROR = "ADAPTER ERROR: key generation failed"
    RECOVERY_ADAPTER_ERROR = "ADAPTER ERROR: key recovery failed"

    # Server facade.
    CLIENT_KDC_NOT_FOUND = "Client KDC not found."
    CLIENT_UNAUTHENTICATED = "SERVER: invalid session ID"
    MISSING_KEY = "Missing one of the half key."
    VALIDATION_CLIENT_SERVER_ERROR = "Server cross-validation failed: mismatch between client and server."
    VALIDATION_KDC_SERVER_ERROR = "Server cross-validation failed: mismatch between KDCs and server."
    SYNC_ERROR = "SERVER: critical error during synchronization."
    NETWORK_CONNECTION_ERROR = "SERVER: can't establish connection to KDCs."
    BUTTERFLY_ERROR = "Butterfly protocol not completed."
    EXCHANGE_ERROR = "SERVER: security breach during encryption/decryption."

# System messages used in the program so we don't write string in the code.
class SystemMessages(str, Enum):
    # Base facade.
    INIT_QKD = "NETWORK: initialization QKD infrastructure."
    COMPLETED_QKD_SETUP = "NETWORK: QKD infrastructure setup completed."
    START_SSH_CONNECTION = "TUNNELING: starting SSH connection to"
    COMPLETED_SSH_CONNECTION = "TUNNELING: routing completed with local url"
    DIRECT_CONNECTION = "NETWORK: direct connection on"
    SSH_CLOSED = "TUNNELING: connection closed."

    # Server facade.
    TOPOLOGY_REQUEST = "SERVER: topology request receive. The client is connected to"
    TOPOLOGY_DONE = "SERVER: the network topology is ready"
    HANDSHAKE_COMPLETED = "SERVER: handshake completed with generated session ID "
    BUTTERFLY_SERVER = "SERVER: starting butterfly protocol on server side."
    BUTTERFLY_COMPLETED = 'SERVER: Butterfly Protocol successfully completed.'
    MESSAGE_RECEIVED = "SERVER: Message received"
    SERVER_RESPONSE = "This is a simulated response, if you can read this everything is ok."

class SystemNames(str, Enum):
    QKD_ORCHESTRATOR = "QKD Orchestrator"

# QKD Topology: names and connection.
class KdcNames(str, Enum):
    AIJA = "AIJA"
    BRENCIS = "BRENCIS"

QKD_TOPOLOGY = {
    KdcNames.AIJA: KdcNames.BRENCIS,
    KdcNames.BRENCIS: KdcNames.AIJA
}