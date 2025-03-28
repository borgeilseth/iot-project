import csv
from tabulate import tabulate


def parse(file_list):
    states = []  # Store results for each state

    for file, ranges in file_list:  # Iterate over the files
        with open(file, "r") as f:  # Open the file
            reader = csv.reader(f)  # Import the CSV file
            data = list(reader)  # Convert the reader to a list
            data = data[1:]  # Remove the header

            # Extract the values from the data
            values = [float(row[1]) for row in data]

            # Create empty states for each
            file_states = [
                {"name": range["name"], "values": [], "range": range["range"]}
                for range in ranges
            ]

            # Assign values to the states
            for value in values:
                for state in file_states:
                    # Check if the value is within the range
                    if value >= state["range"][0] and value <= state["range"][1]:
                        state["values"].append(value)  # Add the value to the group
                        break

            # Insert into the global states list
            for state in file_states:
                found = False
                # Check if the state is already in the list
                for s in states:
                    if s["name"] == state["name"]:  # If the state is found
                        s["values"] += state["values"]  # Add the values to the state
                        s["avg"] = sum(s["values"]) / len(s["values"])
                        found = True
                        break

                if not found:  # If the state is not found
                    state["avg"] = sum(state["values"]) / len(state["values"])
                    states.append(state)  # Add the state to the list

    # Print a pretty table
    table = [[group["name"], round(group["avg"], 2)] for group in states]
    print(
        tabulate(
            table,
            headers=["State", "Average Power Consumption (mW)"],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    # Import data from the CSV files
    # Each file has states corresponding to those in the graph
    # From visual inspection of the graphs, we determine the ranges for each state
    data = [
        [
            "./data/deep_sleep.csv",
            [
                {"name": "Deep-Sleep", "range": [0, 100]},
                {"name": "Idle", "range": [300, 350]},
                {"name": "Wi-Fi on", "range": [700, 800]},
            ],
        ],
        [
            "./data/sensor_read.csv",
            [
                {"name": "Sensor Read", "range": [460, 470]},
                {"name": "Idle", "range": [330, 340]},
            ],
        ],
        [
            "./data/transmission_power.csv",
            [
                {"name": "Wi-Fi on", "range": [680, 720]},
                {"name": "Transmission at 2 dBm", "range": [750, 850]},
                {"name": "Transmission at 19.5 dBm", "range": [1200, 1300]},
            ],
        ],
    ]
    parse(data)
