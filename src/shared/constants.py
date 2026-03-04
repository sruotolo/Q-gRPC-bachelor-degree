from enum import Enum

# Error messages used in the program so we don't write string in the code.
class ErrorMessages(str, Enum):
    SECURITY_BREACH = "SECURITY ERROR: the payload has been altered"
    GENERATION_ADAPTER_ERROR = "ADAPTER ERROR: key generation failed"
    RECOVERY_ADAPTER_ERROR = "ADAPTER ERROR: key recovery failed"

class SystemMessages(str, Enum):
    INIT_QKD = "NETWORK: initialization QKD infrastructure."
    COMPLETED_QKD_SETUP = "NETWORK: QKD infrastructure setup completed."
    START_SSH_CONNECTION = "TUNNELING: starting SSH connection to"
    COMPLETED_SSH_CONNECTION = "TUNNELING: routing completed with local url"
    DIRECT_CONNECTION = "NETWORK: direct connection on"
    SSH_CLOSED = "TUNNELING: connection closed."

# QKD Topology: names and connection.
class KdcTarget(str, Enum):
    AIJA = "AIJA"
    BRENCIS = "BRENCIS"

QKD_TOPOLOGY = {
    KdcTarget.AIJA: KdcTarget.BRENCIS,
    KdcTarget.BRENCIS: KdcTarget.AIJA
}