import os
from dotenv import load_dotenv
import src.custom_test.test_constants as test_constants
from src.client.client_facade import ClientFacade
from src.shared.constants import SystemMessages, SystemNames, ErrorMessages
from src.custom_test.test_utils import plot_stacked_bar


def run_test():
    print(f"{SystemMessages.RUNNING_TEST}: {test_constants.NUMBER_OF_TESTS} clients")
    load_dotenv()

    for test_counter in range(1, test_constants.NUMBER_OF_TESTS + 1):
        local_kdc_name = SystemNames.CLIENT_KDC_NAME
        server_address = os.getenv("SERVER_ADDRESS", "localhost:50051")

        ca_cert_path = os.getenv("CA_CERT_PATH")
        cert_path = os.getenv("CLIENT_CERT_PATH")
        key_path = os.getenv("CLIENT_KEY_PATH")

        client = ClientFacade(local_kdc_name=local_kdc_name, server_address=server_address,
                              ca_cert_path=ca_cert_path,
                              client_cert_path=cert_path, client_key_path=key_path)

        print(f"Starting test number {test_counter}")
        print(f"{SystemMessages.CLIENT_CONNECTION_STARTING} {client.server_address} with KDC {local_kdc_name}")
        success = client.setup_connection_and_synchronization()
        if not success:
            print(ErrorMessages.CLIENT_CONNECTION_FAILED)
            return

        print(SystemMessages.ESTABLISHED_CONNECTION)

        message = SystemMessages.TEST_MESSAGE

        response = client.send_message(message)
        print(f"SERVER RESPONSE -> {response}")

        client.print_time_result(test_counter)

    print(SystemMessages.ENDED_TEST)
    plot_stacked_bar()

if __name__ == "__main__":
    run_test()