# Copyright 2026, Samuele Ruotolo
# SPDX-License-Identifier: MIT

import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag
from src.shared.constants import ErrorMessages


# SHA256 used for the cross-validation in the Butterfly Protocol.
def sha256_hash(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# We use HKDF to create an AES-256 key from the QKD key that could be very long.
# The standard length for AES-256 is 32 bytes.
def create_aes_key(full_key: bytes) -> bytes:
    hkdf = HKDF (
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"QKD_to_AES_Session_Key"
    )

    return hkdf.derive(full_key)


# Encrypt a payload with AES-GCM.
def aes_gcm_encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    aes_key = create_aes_key(key)
    aes_gcm = AESGCM(aes_key)
    nonce = os.urandom(12)

    # Generate the encrypted payload and slice it into the cipher text and tag.
    crypto_result = aes_gcm.encrypt(nonce, plaintext, associated_data=None)
    ciphertext = crypto_result[:-16]
    tag = crypto_result[-16:]

    return nonce, tag, ciphertext


# Decrypt a payload with AES-GCM.
def aes_gcm_decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes) -> bytes:
    aes_key = create_aes_key(key)
    aes_gcm = AESGCM(aes_key)

    # Rebuild the original message.
    encrypted_message = ciphertext + tag

    try:
        return aes_gcm.decrypt(nonce, encrypted_message, associated_data=None)
    except InvalidTag:
        raise Exception(ErrorMessages.SECURITY_BREACH)