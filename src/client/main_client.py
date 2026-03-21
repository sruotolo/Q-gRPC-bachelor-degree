# Copyright 2026, Samuele Ruotolo
# SPDX-License-Identifier: MIT

import os
from dotenv import load_dotenv
from src.shared.constants import SystemMessages, ErrorMessages, SystemNames
from src.client.client_facade import ClientFacade

def main():
    load_dotenv()

    local_kdc_name = SystemNames.CLIENT_KDC_NAME
    server_address = os.getenv("SERVER_ADDRESS", "localhost:50051")

    ca_cert_path = os.getenv("CA_CERT_PATH")
    cert_path = os.getenv("CLIENT_CERT_PATH")
    key_path = os.getenv("CLIENT_KEY_PATH")

    client = ClientFacade(local_kdc_name=local_kdc_name, server_address=server_address,
                          ca_cert_path=ca_cert_path,
                          client_cert_path=cert_path, client_key_path=key_path)

    print(f"{SystemMessages.CLIENT_CONNECTION_STARTING} {client.server_address} with KDC {local_kdc_name}")
    success = client.setup_connection_and_synchronization()
    if not success:
        print(ErrorMessages.CLIENT_CONNECTION_FAILED)
        return

    print(SystemMessages.ESTABLISHED_CONNECTION)

    user_input = input(SystemMessages.REQUEST_MESSAGE)
    if not user_input.strip():
        print(SystemMessages.BLANK_MESSAGES)

    response = client.send_message(user_input)
    print(f"SERVER RESPONSE -> {response}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(SystemMessages.MANUALLY_INTERRUPTION)
