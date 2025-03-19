# Plot csv data from the files each file is (Timestamp, Data)
# File is given as a command line argument

import csv
import os
from tabulate import tabulate

script_dir = os.path.dirname(__file__)


def parse(file_list):
    groups = []

    for file, ranges in file_list:
        with open(file, "r") as f:
            reader = csv.reader(f)  # Read the csv file
            data = list(reader)  # Convert the reader to a list
            data = data[1:]  # Remove the header

            # Extract the values from the data
            values = [float(row[1]) for row in data]

            # Group the values based on the ranges
            tmp_groups = [
                {"name": range["name"], "values": [], "range": range["range"]}
                for range in ranges
            ]
            for value in values:
                for group in tmp_groups:
                    if value >= group["range"][0] and value <= group["range"][1]:
                        group["values"].append(value)
                        break

            # Insert into the groups
            for group in tmp_groups:
                group["avg"] = sum(group["values"]) / len(group["values"])
                found = False
                for g in groups:
                    if g["name"] == group["name"]:
                        g["values"] += group["values"]
                        g["avg"] = sum(g["values"]) / len(g["values"])
                        found = True
                        break

                if not found:
                    groups.append(group)

    # Print the table
    table = [[group["name"], group["avg"]] for group in groups]
    print(
        tabulate(
            table,
            headers=["State", "Average Power Consumption (mW)"],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    parse(
        [
            [
                os.path.join(script_dir, "instructions", "deep_sleep.csv"),
                [
                    {"name": "Deep-Sleep", "range": [0, 100]},
                    {"name": "Idle", "range": [300, 350]},
                    {"name": "Wi-Fi on", "range": [700, 800]},
                ],
            ],
            [
                os.path.join(script_dir, "instructions", "sensor_read.csv"),
                [
                    {"name": "Sensor Read", "range": [460, 470]},
                    {"name": "Idle", "range": [330, 340]},
                ],
            ],
            [
                os.path.join(script_dir, "instructions", "transmission_power.csv"),
                [
                    {"name": "Wi-Fi on", "range": [680, 720]},
                    {"name": "Transmission at 2 dBm", "range": [750, 850]},
                    {"name": "Transmission at 19.5 dBm", "range": [1200, 1300]},
                ],
            ],
        ]
    )
