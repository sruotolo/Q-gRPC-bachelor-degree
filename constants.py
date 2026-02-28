from enum import Enum

class ErrorMessages(str, Enum):
    SECURITY_BREACH = "SECURITY ERROR: the payload has been altered"

class KdcTarget(str, Enum):
    AIJA = "AIJA"
    BRENCIS = "BRENCIS"

QKD_TOPOLOGY = {
    KdcTarget.AIJA: KdcTarget.BRENCIS,
    KdcTarget.BRENCIS: KdcTarget.AIJA
}