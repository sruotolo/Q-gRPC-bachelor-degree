# Copyright 2026, Samuele Ruotolo
# SPDX-License-Identifier: MIT

from enum import StrEnum

# QKD Topology: names and connection.
class KdcNames(StrEnum):
    AIJA = "AIJA"
    BRENCIS = "BRENCIS"

QKD_TOPOLOGY = {
    KdcNames.AIJA: KdcNames.BRENCIS,
    KdcNames.BRENCIS: KdcNames.AIJA
}
