# Copyright 2026, Samuele Ruotolo
# SPDX-License-Identifier: MIT

from pathlib import Path
import csv
import pandas as pd
import matplotlib.pyplot as plt
from src.shared.constants import ErrorMessages
from src.custom_test.test_constants import BenchmarkNumericConstants


# Create the csv file with time datas ready for the graphics.
def print_time_benchmark(butterly_protocol_time: float, data_exchange_time: float, test_counter: int):
    folder_name = "benchmark_results"
    file_name = "time_benchmark.csv"
    path = Path(folder_name) / file_name

    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()

    with open(path, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Test_ID", "Butterfly Protocol time (ms)", "Data exchange time (ms)"])

        writer.writerow([test_counter, round(butterly_protocol_time, 3), round(data_exchange_time, 3)])


# Create a stacked bar graphic and save it into the benchmark result directory.
def plot_stacked_bar():
    folder_name = "benchmark_results"
    file_name = "time_benchmark.csv"
    saving_file_name = "time_stacked_bar.png"
    path = Path(folder_name) / file_name
    saving_path = Path(folder_name) / saving_file_name

    try:
        datas = pd.read_csv(path)

        if datas.empty:
            return

        plt.style.use('seaborn-v0_8-darkgrid')
        plt.figure(figsize=(BenchmarkNumericConstants.STACKED_BAR_GRAPHIC_X, BenchmarkNumericConstants.STACKED_BAR_GRAPHIC_Y))

        test_id_col = "Test_ID"
        butterfly_protocol_col = "Butterfly Protocol time (ms)"
        data_exchange_col = "Data exchange time (ms)"

        plt.bar(datas[test_id_col], datas[butterfly_protocol_col], label='Butterfly Protocol')
        plt.bar(datas[test_id_col], datas[data_exchange_col], label='Data exchange')

        plt.title("Execution time for a test", fontsize=22)
        plt.legend(fontsize=18,loc='upper center',
           bbox_to_anchor=(0.5, 1.02),
           ncol=2,
           frameon=False)
        plt.xlabel("Test number", fontsize=22)
        plt.yscale('log')
        plt.ylabel("Execution time (ms) - logarithmic scale", fontsize=22)
        plt.xticks(ticks=datas[test_id_col], fontsize=18)
        plt.yticks(fontsize=18)
        plt.tight_layout()

        plt.savefig(saving_path)
    except FileNotFoundError:
        print(ErrorMessages.NO_CSV_FILE)
    except KeyError:
        print(ErrorMessages.NO_CSV_COLUMN)
    except Exception as e:
        print(f"{ErrorMessages.GRAPHIC_GENERATION_ERROR}: {e}")