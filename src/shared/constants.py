from enum import StrEnum

# Error messages used in the program so we don't write string in the code.
class ErrorMessages(StrEnum):
    # Adapter.
    SECURITY_BREACH = "SECURITY ERROR: the payload has been altered"
    GENERATION_ADAPTER_ERROR = "ADAPTER ERROR: key generation failed"
    RECOVERY_ADAPTER_ERROR = "ADAPTER ERROR: key recovery failed"

    # Base facade.
    ENV_ERROR = "There is a configuration problem in the .env file for the node"
    SSH_ERROR = "Failed to establish the SSH connection fot the node"

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

    # Client facade.
    CERT_NOT_FOUND = "Certificate not found."
    GENERIC_ERROR = "Generic error"
    MISSING_KEYS = "Missing one of the half keys."
    VALIDATION_FAILED_BUTTERFLY = "Cross-validation failed: Butterfly protocol failed."
    SYNC_FAILED_BUTTERFLY = "Critical error: client and server have different keys."
    GRPC_ERROR = "GRPC error"
    CONNECTION_ERROR = "Critical error during connection"
    FAILED_MESSAGE = "Can't send the message: connection not established."
    NETWORK_ERROR = "Network error."
    CRYPTOGRAPHIC_ERROR = "Cryptographic error."
    CLIENT_BUG = "Something went wrong with the client."

    # Server main.
    SERVER_MAIN_NO_CERTS = "Certificates files missing"

    # Client main.
    CLIENT_CONNECTION_FAILED = "CLIENT: connection failed."


# System messages used in the program so we don't write string in the code.
class SystemMessages(StrEnum):
    # Base facade.
    INIT_QKD = "NETWORK: initialization QKD infrastructure."
    COMPLETED_QKD_SETUP = "NETWORK: QKD infrastructure setup completed."
    START_SSH_CONNECTION = "TUNNELING: starting SSH connection to"
    COMPLETED_SSH_CONNECTION = "TUNNELING: routing completed with local url"
    DIRECT_CONNECTION = "NETWORK: direct connection on"
    SSH_CLOSED = "TUNNELING: connection closed."

    # Server facade.
    TOPOLOGY_REQUEST = "SERVER: topology request receive. The client is connected to"
    TOPOLOGY_DONE = "SERVER: network topology is ready"
    HANDSHAKE_COMPLETED = "SERVER: handshake completed with generated session ID "
    BUTTERFLY_SERVER = "SERVER: starting butterfly protocol on server side."
    BUTTERFLY_COMPLETED = 'SERVER: Butterfly Protocol successfully completed.'
    MESSAGE_RECEIVED = "SERVER: Message received"
    SERVER_RESPONSE = "This is a simulated response, if you can read this then everything is ok."
    SERVER_RESPONSE_TO_BLANK_MESSAGE = "The client hasn't send any message, connection closed without response."

    # Client facade.
    MTLS_ACTIVATED = "CLIENT: mTLS mode activated."
    CHANNEL_CREATED = "CLIENT: certificates uploaded successfully -> channel is ready"
    NETWORK_NEGOTIATION_STARTED = "CLIENT: starting topology network negotiation with local KDC"
    NETWORK_NEGOTIATION_DONE = "CLIENT: topology network negotiation completed with partner KDC"
    INSECURE_CHANNEL_ACTIVATED = "CLIENT: certificates not found, using insecure channel."
    BUTTERFLY_CLIENT = "CLIENT: starting butterfly protocol on client side."
    KEY_SYNC = "CLIENT: key synchronization with server."
    CONNECTION_COMPLETED = "CLIENT: connection established without error."

    # Server main.
    SERVER_MAIN_MTLS_START = "SERVER: starting MTLS mode."
    SERVER_MAIN_MTLS_DONE = "SERVER: certificates loaded successfully, MTLS mode completed."
    SERVER_INSECURE_CONNECTION = "SERVER: certificates not found, using insecure connection."
    SERVER_CLOSING = "SERVER: closing the server."
    SERVER_STARTING = "--- STARTING THE Q-GRPC SERVER. ---"

    # Client main.
    CLIENT_CONNECTION_STARTING = "CLIENT: trying to connect to server"
    ESTABLISHED_CONNECTION = "CLIENT: connection established."
    REQUEST_MESSAGE = "CLIENT: write the message you want to send or leave it blank to exit.\n"
    BLANK_MESSAGES = "CLIENT: no message written, closing the connection."
    MANUALLY_INTERRUPTION = "CLIENT: execution manually interrupted."


class SystemNames(StrEnum):
    QKD_ORCHESTRATOR = "QKD Orchestrator"
    CLIENT_KDC_NAME = "AIJA"