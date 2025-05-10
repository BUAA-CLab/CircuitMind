import os
import pandas as pd
import numpy as np

# Folder path for leaderboard data
folder_path = "leaderboard_data"
# Folder path to save the output
save_path = "Results"

# Define the RANK values to process
target_ranks = list(range(1, 1001))

# File name mapping from task ID to CSV filename
file_mapping = {
    '1_not_gate': 'NOT Gate.csv',
    '2_second_tick': 'Second Tick.csv',
    '3_xor_gate': 'XOR Gate.csv',
    '4_or3_gate': 'Bigger OR Gate.csv',
    '5_and3_gate': 'Bigger AND Gate.csv',
    '6_xnor_gate': 'XNOR Gate.csv',
    '7_double_trouble': 'Double Trouble.csv',
    '9_counting_signals': 'Counting Signals.csv',
    '10_half_adder': 'Half Adder.csv',
    '11_full_adder': 'Full Adder.csv',
    '12_odd_change': 'Odd Ticks.csv',
    '13_inverter_1bit': 'Bit Inverter.csv',
    '14_or_8bit': 'Byte OR.csv',
    '15_not_8bit': 'Byte NOT.csv',
    '16_adder_8bit': 'Adding Bytes.csv',
    '17_mux_8bit': 'Input Selector.csv',
    '18_opposite_number': 'Signed Negator.csv',
    '19_elegant_storage': 'Saving Gracefully.csv',
    '20_store_byte': 'Saving Bytes.csv',
    '21_decoder_1bit': '1 Bit Decoder.csv',
    '22_decoder_3bit': '3 Bit Decoder.csv',
    '23_logic_engine': 'Logic Engine.csv',
    '24_box': 'Little Box.csv',
    '25_counter': 'Counter.csv',
    '26_arithmetic_engine': 'Arithmetic Engine.csv',
    '27_instruction_decoder': 'Instruction Decoder.csv',
    '28_conditional_checker': 'Conditions.csv'
}

# Group information
groups = {
    "Easy": [
        "13_inverter_1bit", "14_or_8bit", "15_not_8bit", "1_not_gate",
        "21_decoder_1bit", "2_second_tick", "3_xor_gate", "4_or3_gate",
        "5_and3_gate", "6_xnor_gate"
    ],
    "Medium": [
        "10_half_adder", "16_adder_8bit", "18_opposite_number",
        "27_instruction_decoder", "8_odd_signal", "11_full_adder",
        "17_mux_8bit", "22_decoder_3bit", "7_double_trouble",
        "9_counting_signals"
    ],
    "Hard": [
        "12_odd_change", "19_elegant_storage", "20_store_byte",
        "23_logic_engine", "24_box", "25_counter",
        "26_arithmetic_engine", "28_conditional_checker"
    ]
}

# Dictionary to store SEI values for all files
sei_values = {}

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    # Process only CSV files that don't end with '-less.csv'
    if filename.endswith(".csv") and not filename.endswith("-less.csv"):
        file_path = os.path.join(folder_path, filename)

        try:
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Check if required columns exist
            if "RANK" in df.columns and "TOTAL" in df.columns:
                # Calculate SEI value (reciprocal of TOTAL) for target ranks
                df.loc[df["RANK"].isin(target_ranks), "SEI"] = 1 / df["TOTAL"]
                # Filter rows for target ranks
                target_rows = df[df["RANK"].isin(target_ranks)]

                # Store SEI values for each target RANK
                for rank in target_ranks:
                    if rank in target_rows["RANK"].values:
                        # Get the SEI value for the specific rank
                        sei = target_rows[target_rows["RANK"] == rank]["SEI"].iloc[0]
                        # Initialize dictionary for filename if not exists
                        if filename not in sei_values:
                            sei_values[filename] = {}
                        # Store the SEI value
                        sei_values[filename][rank] = sei
                    else:
                        # Warning if data for a specific rank is missing in a file
                        print(f"Warning: Data for RANK {rank} is missing in file {filename}")
            else:
                # Error if required columns are missing
                print(f"Error: File {filename} is missing required columns 'RANK' or 'TOTAL'")

        except Exception as e:
            # Error handling for file reading
            print(f"Error reading file {filename}: {e}")

# Calculate geometric mean
def compute_geometric_mean(values):
    # Replace zero values with 1e-4 to avoid log(0)
    adjusted_values = [max(x, 1e-4) for x in values]
    # Calculate log of adjusted values
    log_values = [np.log(x) for x in adjusted_values]
    # Calculate the mean of log values
    log_mean = np.mean(log_values)
    # Return the exponent of the log mean
    return np.exp(log_mean)

# Calculate overall geometric mean across all files for each rank
geometric_mean_all = {}
for rank in target_ranks:
    # Collect SEI values for the current rank from all files
    sei_list = [sei_values[filename][rank] for filename in sei_values if rank in sei_values[filename]]
    # Calculate geometric mean if the list is not empty
    if sei_list:
        geometric_mean_all[rank] = round(compute_geometric_mean(sei_list), 3)
    else:
        # Set to None if no valid data for the rank
        geometric_mean_all[rank] = None
        print(f"Warning: No valid SEI data for RANK {rank} across all files")

# Calculate geometric mean for each group for each rank
geometric_mean_groups = {group: {} for group in groups}
for group, task_ids in groups.items():
    for rank in target_ranks:
        sei_list = []
        # Collect SEI values for the current rank within the current group
        for task_id in task_ids:
            filename = file_mapping.get(task_id)
            # Check if filename exists in mapping, is in sei_values, and rank data exists
            if filename and filename in sei_values and rank in sei_values[filename]:
                sei_list.append(sei_values[filename][rank])
        # Calculate geometric mean if the list is not empty
        if sei_list:
            geometric_mean_groups[group][rank] = round(compute_geometric_mean(sei_list), 3)
        else:
            # Set to None if no valid data for the group and rank
            geometric_mean_groups[group][rank] = None
            print(f"Warning: No valid SEI data for group {group} at RANK {rank}")

# Print overall geometric mean
print("\nGeometric mean for all files:")
for rank in target_ranks:
    if geometric_mean_all[rank] is not None:
        print(f"RANK {rank}: {geometric_mean_all[rank]:.3f}")
    else:
        print(f"RANK {rank}: No valid data")

# Print geometric mean for each group
for group in groups:
    print(f"\nGeometric mean for group {group}:")
    for rank in target_ranks:
        if geometric_mean_groups[group][rank] is not None:
            print(f"RANK {rank}: {geometric_mean_groups[group][rank]:.3f}")
        else:
            print(f"RANK {rank}: No valid data")

# Prepare and save results to a CSV file
output_data = {"RANK": target_ranks}
# Add overall geometric mean to output data
output_data["All_Files"] = [f"{geometric_mean_all[rank]:.3f}" if geometric_mean_all[rank] is not None else "N/A" for rank in target_ranks]
# Add geometric mean for each group to output data
for group in groups:
    output_data[group] = [
        f"{geometric_mean_groups[group][rank]:.3f}" if geometric_mean_groups[group][rank] is not None else "N/A" for rank in target_ranks]

# Create output DataFrame
output_df = pd.DataFrame(output_data)
# Ensure the save directory exists
os.makedirs(save_path, exist_ok=True)
# Save the output DataFrame to CSV
output_df.to_csv(os.path.join(save_path, "output.csv"), index=False)
print("\nResults saved to 'output.csv'")
