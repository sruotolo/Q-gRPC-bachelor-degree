import os
from dotenv import load_dotenv
from concurrent import futures
import grpc
from generated import qkd_pb2_grpc
from src.server.server_facade import ServerFacade
from src.shared.constants import SystemMessages, ErrorMessages

def serve():
    load_dotenv()

    # Create the listening address.
    port = os.getenv("SERVER_PORT", "50051")
    address = f"[::]:{port}"

    ca_cert_path = os.getenv("CA_CERT_PATH")
    cert_path = os.getenv("SERVER_CERT_PATH")
    key_path = os.getenv("SERVER_KEY_PATH")

    # Create the grpc server (can handle maximum 10 client, but it's just a simulation).
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add our logic (the facade) to the gRPC server.
    facade = ServerFacade()
    qkd_pb2_grpc.add_QKDOrchestratorServiceServicer_to_server(facade, server)

    if ca_cert_path and cert_path and key_path:
        try:
            print(SystemMessages.SERVER_MAIN_MTLS_START)
            with open(ca_cert_path, "rb") as ca:
                ca_cert = ca.read()
            with open(cert_path, "rb") as server_cert:
                cert = server_cert.read()
            with open(key_path, "rb") as server_key:
                key = server_key.read()

            credentials = grpc.ssl_server_credentials(
                [(key, cert)],
                root_certificates=ca_cert,
                require_client_auth=True
            )
            server.add_secure_port(address, credentials)
            print(SystemMessages.SERVER_MAIN_MTLS_DONE)
        except FileNotFoundError as e:
            print(f"{ErrorMessages.SERVER_MAIN_NO_CERTS}: {e}")
            return
    else:
        print(SystemMessages.SERVER_INSECURE_CONNECTION)
        server.add_insecure_port(address)

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print(SystemMessages.SERVER_CLOSING)
        server.stop(0)

if __name__ == "__main__":
    print(SystemMessages.SERVER_STARTING)
    serve()