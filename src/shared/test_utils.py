from pathlib import Path

def print_time_benchmark(butterly_protocol_time: float, data_exchange_time: float):
    folder_name = "benchmark_results"
    file_name = "time_benchmark.txt"
    path = Path(folder_name) / file_name

    if path.exists():
        with open(path, "r", encoding='utf-8') as f:
            content = f.read()
            test_counter = content.count("Test Client") + 1

    with open(path, "a", encoding='utf-8') as f:
        f.write(f"Test Client {test_counter}\n")
        f.write(f"Butterly Protocol time: {butterly_protocol_time:.3f} ms\n")
        f.write(f"Data exchange time: {data_exchange_time:.3f} ms\n")
        f.write("\n\n")