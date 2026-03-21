# Copyright 2026, Samuele Ruotolo
# SPDX-License-Identifier: MIT

from flask import Flask, jsonify, request
import requests
import hashlib
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- AIJA CONSTANTS (1001) ---
AIJA_REAL_IP = os.getenv("AIJA_REAL_IP")
AIJA_REAL_PORT = int(os.getenv("AIJA_REAL_PORT"))
AIJA_CERT_PATH = os.getenv("AIJA_CERT_PATH")
AIJA_KEY_PATH = os.getenv("AIJA_KEY_PATH")
AIJA_CA_PATH = os.getenv("AIJA_CA_PATH")

# --- BUTTERFLY LOGIC ---
key_buffer = {}
RESERVATION_TIME = 90
MAX_READS = 2

# Delete all the keys that are alive for more than the reservation time so the key_buffer doesn't grow too much.
def clean_old_keys():
    current_time = time.time()
    keys_to_delete = [key_id for key_id, data in key_buffer.items() if current_time - data["timestamp"] > RESERVATION_TIME]
    for key in keys_to_delete:
        del key_buffer[key]

# Logic to split and hash the key as needed in the butterfly protocol.
def sha256_hash(data):
    return hashlib.sha256(data).digest()

def split_and_hash(key_id, key):
    full_key_bytes = base64.b64decode(key)
    midpoint = len(full_key_bytes) // 2

    key_L = full_key_bytes[:midpoint]
    key_R = full_key_bytes[midpoint:]
    hash_key_R = sha256_hash(key_R)

    return {
        "key_ID": key_id,
        "part_of_key": "LEFT",
        "key_half_b64": base64.b64encode(key_L).decode('utf-8'),
        "other_half_hash_b64": base64.b64encode(hash_key_R).decode('utf-8')
    }

# Forward the get_key request to the QKD.
@app.route('/api/v1/keys/<slave_sae_id>/enc_keys', methods=['POST'])
def forward_get_key(slave_sae_id):
    clean_old_keys()

    url = f"https://{AIJA_REAL_IP}:{AIJA_REAL_PORT}/api/v1/keys/{slave_sae_id}/enc_keys"

    try:
        response = requests.post(
            url,
            cert=(AIJA_CERT_PATH, AIJA_KEY_PATH),
            verify=AIJA_CA_PATH,
            json=request.get_json(silent=True),
            params=request.args,
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            key_id = data["keys"][0]["key_ID"]
            elaborated_key = split_and_hash(key_id, data["keys"][0]["key"])

            # Save the key and information in the key buffer.
            key_buffer[key_id] = {
                "data": elaborated_key,
                "timestamp": time.time(),
                "reads": 1
            }

            return jsonify(elaborated_key), response.status_code

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Forward the get_key_with_id request to the QKD.
@app.route('/api/v1/keys/<master_sae_id>/dec_keys', methods=['POST'])
def forward_get_key_with_id(master_sae_id):
    clean_old_keys()

    # Get the request key_id to check if the key is in the buffer.
    requested_data = request.get_json(silent=True, force=True)
    requested_key_id = None
    if requested_data and "key_IDs" in requested_data and len(requested_data["key_IDs"]) > 0:
        requested_key_id = requested_data["key_IDs"][0].get("key_ID")

    # Check the buffer to find the key.
    if requested_key_id and requested_key_id in key_buffer:
        key_buffer[requested_key_id]["reads"] += 1

        # Check if the key has reached end of life and if so, delete it.
        if key_buffer[requested_key_id]["reads"] > MAX_READS:
            del key_buffer[requested_key_id]

        return jsonify(key_buffer[requested_key_id]["data"]), 200

    url = f"https://{AIJA_REAL_IP}:{AIJA_REAL_PORT}/api/v1/keys/{master_sae_id}/dec_keys"

    try:
        response =requests.post(
            url,
            cert=(AIJA_CERT_PATH, AIJA_KEY_PATH),
            verify=AIJA_CA_PATH,
            json=request.get_json(silent=True),
            params=request.args,
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            key_id = data["keys"][0]["key_ID"]
            elaborated_key = split_and_hash(key_id, data["keys"][0]["key"])

            # Save the key and information in the key buffer.
            key_buffer[key_id] = {
                "data": elaborated_key,
                "timestamp": time.time(),
                "reads": 1
            }

            return jsonify(elaborated_key), response.status_code

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("AIJA proxy is ready on 0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001)