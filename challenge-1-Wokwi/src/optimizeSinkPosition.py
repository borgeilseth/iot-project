import numpy as np

sensor_positions = np.array(
    [
        (1, 2),
        (10, 3),
        (4, 8),
        (15, 7),
        (6, 1),
        (9, 12),
        (14, 4),
        (3, 10),
        (7, 7),
        (12, 14),
    ]
)
sink_fixed_pos = np.array([20, 20])

b = 2000  # bits per packet
Eb = 5 * 10**6  # energy per sensor in nJ
Ec = 50  # TX/RX circuitry energy in nJ/bit
k = 1  # nJ/bit/m^2

### TASK A - Find lifetime of system ###

# Compute distances from each sensor to (20,20) and store in an array
d_list = np.linalg.norm(sensor_positions - sink_fixed_pos, axis=1)

# Compute total energy used by each sensor for 1 transmission, using formula Etx(d) = k * d**2
E_total = (Ec + k * d_list**2) * b  # in nJ

# Compute sensor lifetimes in number of transmissions for each sensor
lifetimes = Eb / E_total

# Find the worst-case sensor – sensor with shortest lifetime
min_lifetime = np.min(lifetimes)
worst_case_sensor = np.argmin(lifetimes) + 1

print(
    f"Shortest sensor lifetime: {min_lifetime:.2f} transmission cycles, which means the lifetime of the system is {min_lifetime:.0f} full transmission cycles."
)
print(
    f"Worst-case sensor with fixed sink position: Sensor nr {worst_case_sensor} with positions {sensor_positions[worst_case_sensor-1]}"
)


### TASK B - Find optimal sink sosition for maximum lifetime of system ###

# Create a list of all possible sink positions, with two decimal precision
x_values = np.arange(0.00, 20.00, 0.01)
y_values = np.arange(0.00, 20.00, 0.01)
test_sink_positions = [(x, y) for x in x_values for y in y_values]

longest_lifetime = 0
optimalPosition = (0, 0)
worst_case_sensor_optimalSink = 0

# Iterate through all the possible sink positions and find an optimal solution, by using brute-force
for xs, ys in test_sink_positions:
    test_sink_pos = np.array([xs, ys])
    test_d_list = np.linalg.norm(sensor_positions - test_sink_pos, axis=1)
    test_E_total = (Ec + k * test_d_list**2) * b  # in nJ
    test_lifetimes = Eb / test_E_total
    test_min_lifetime = np.min(test_lifetimes)
    test_worst_case_sensor = np.argmin(test_lifetimes) + 1

    if test_min_lifetime > longest_lifetime:
        longest_lifetime = test_min_lifetime
        optimalPosition = (xs, ys)
        worst_case_sensor_optimalSink = test_worst_case_sensor

print(f"Optimal sink position: ({optimalPosition[0]}, {optimalPosition[1]})")
print(
    f"Worst-case sensor with optimal sink position: Sensor nr {worst_case_sensor_optimalSink} with positions {sensor_positions[worst_case_sensor_optimalSink-1]}"
)
