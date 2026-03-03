from enum import Enum

# Error messages used in the program so we don't write string in the code.
class ErrorMessages(str, Enum):
    SECURITY_BREACH = "SECURITY ERROR: the payload has been altered"
    GENERATION_ADAPTER_ERROR = "ADAPTER ERROR: key generation failed"
    RECOVERY_ADAPTER_ERROR = "ADAPTER ERROR: key recovery failed"

# QKD Topology: names and connection.
class KdcTarget(str, Enum):
    AIJA = "AIJA"
    BRENCIS = "BRENCIS"

QKD_TOPOLOGY = {
    KdcTarget.AIJA: KdcTarget.BRENCIS,
    KdcTarget.BRENCIS: KdcTarget.AIJA
}