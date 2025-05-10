import numpy as np
import pandas as pd

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

# Read input CSV file
input_file = 'input.csv'
df = pd.read_csv(input_file)

# Set Subfolder as index
df.set_index('Subfolder', inplace=True)


# Calculate geometric mean
def compute_geometric_mean(values):
    # Replace zero values with 1e-5
    adjusted_values = [max(x, 1e-5) for x in values]
    log_values = [np.log(x) for x in adjusted_values]
    log_mean = np.mean(log_values)
    return np.exp(log_mean)


# Initialize result DataFrame
models = df.columns
result = pd.DataFrame(index=models, columns=['Easy_GM', 'Medium_GM', 'Hard_GM', 'Overall_GM'])

# Calculate geometric mean for each model
for model in models:
    # Easy group
    easy_values = df.loc[groups['Easy'], model].values
    result.loc[model, 'Easy_GM'] = compute_geometric_mean(easy_values)

    # Medium group
    medium_values = df.loc[groups['Medium'], model].values
    result.loc[model, 'Medium_GM'] = compute_geometric_mean(medium_values)

    # Hard group
    hard_values = df.loc[groups['Hard'], model].values
    result.loc[model, 'Hard_GM'] = compute_geometric_mean(hard_values)

    # Overall (all subfolders)
    overall_values = df[model].values
    result.loc[model, 'Overall_GM'] = compute_geometric_mean(overall_values)

# Reset index and rename column
result.reset_index(inplace=True)
result.rename(columns={'index': 'Model'}, inplace=True)

# Save to new CSV file
output_file = 'output.csv'
result.to_csv(output_file, index=False)

print(f"Geometric mean calculated and saved to {output_file}")
print(result)
