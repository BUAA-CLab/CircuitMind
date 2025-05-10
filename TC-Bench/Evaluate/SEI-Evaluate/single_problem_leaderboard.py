import pandas as pd
import numpy as np

# Load data from two CSV files
summary_df = pd.read_csv(
    'summary_input.csv')
combined_df = pd.read_csv('combined_input.csv')

# Define performance levels (from lowest to highest)
levels = ['Poor (1000)', 'Average (750)', 'Good (500)', 'Excellent (250)']
ranks = [1000, 750, 500, 250]  # Corresponding RANK values

# Mapping between Subfolder and Source_File
subfolder_to_file = {
    '1_not_gate': 'NOT Gate.csv',
    '2_second_tick': 'Second Tick.csv',
    '3_xor_gate': 'XOR Gate.csv',
    '4_or3_gate': 'Bigger OR Gate.csv',
    '5_and3_gate': 'Bigger AND Gate.csv',
    '6_xnor_gate': 'XNOR Gate.csv',
    '7_double_trouble': 'Double Trouble.csv',
    '8_odd_signal': 'ODD Number of Signals.csv',
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


# Extract SEI thresholds for each problem (strictly using RANK and SEI from combined_results.csv)
def get_sei_thresholds(problem):
    source_file = subfolder_to_file.get(problem, None)
    if source_file is None:
        print(f"Error: Source_File not found for problem {problem}")
        return [0.0, 0.05, 0.15, 0.25]  # Default thresholds
    problem_data = combined_df[combined_df['Source_File'] == source_file]
    if problem_data.empty:
        print(f"Error: {source_file} not found in combined_results.csv")
        return [0.0, 0.05, 0.15, 0.25]

    sei_values = problem_data['SEI'].values
    if len(set(sei_values)) == 1:  # If all SEI values are equal
        equal_sei = sei_values[0]
        return [0.0, equal_sei, equal_sei, equal_sei]

    # If not equal, extract SEI corresponding to RANK
    sei_250 = problem_data[problem_data['RANK'] == 250]['SEI'].iloc[0] if not problem_data[
        problem_data['RANK'] == 250].empty else 0.0
    sei_500 = problem_data[problem_data['RANK'] == 500]['SEI'].iloc[0] if not problem_data[
        problem_data['RANK'] == 500].empty else sei_250
    sei_750 = problem_data[problem_data['RANK'] == 750]['SEI'].iloc[0] if not problem_data[
        problem_data['RANK'] == 750].empty else sei_500
    sei_1000 = problem_data[problem_data['RANK'] == 1000]['SEI'].iloc[0] if not problem_data[
        problem_data['RANK'] == 1000].empty else sei_750

    # Construct thresholds: [Poor, Average/Good, Excellent]
    return [sei_1000, sei_750, sei_500, sei_250]


# Determine performance level based on SEI value and problem-specific thresholds
def get_level(sei, thresholds):
    if sei >= thresholds[3]:  # Greater than or equal to the Excellent threshold
        return levels[3]  # Excellent (250)
    elif sei >= thresholds[2]:  # Greater than or equal to the Good threshold
        return levels[2]  # Good (500)
    elif sei >= thresholds[1]:  # Greater than or equal to the Average threshold
        return levels[1]  # Average (750)
    else:  # Less than the Average threshold
        return levels[0]  # Poor (1000)


# Prepare data
problems = summary_df['Subfolder'].tolist()
models = summary_df.columns[1:]  # Exclude 'Subfolder' column

# Categorize problems for each model and count them
model_rankings = {model: {'Top_250': [], '250_to_750': [], 'Below_750': []} for model in models}
csv_ranking_data = []

for model in models:
    for problem in problems:
        # Get problem-specific SEI thresholds
        thresholds = get_sei_thresholds(problem)
        # Get the SEI value for the current model and problem
        sei_value = summary_df[summary_df['Subfolder'] == problem][model].iloc[0]
        # Determine the performance level
        level = get_level(sei_value, thresholds)
        # Append the problem to the corresponding category
        if level == 'Excellent (250)':
            model_rankings[model]['Top_250'].append(problem)
        elif level in ['Good (500)', 'Average (750)']:
            model_rankings[model]['250_to_750'].append(problem)
        else:
            model_rankings[model]['Below_750'].append(problem)

    # Add to CSV data, including counts
    csv_ranking_data.append({
        'Model': model,
        'Problems_Top_250': ','.join(model_rankings[model]['Top_250']),
        'Count_Top_250': len(model_rankings[model]['Top_250']),
        'Problems_250_to_750': ','.join(model_rankings[model]['250_to_750']),
        'Count_250_to_750': len(model_rankings[model]['250_to_750']),
        'Problems_Below_750': ','.join(model_rankings[model]['Below_750']),
        'Count_Below_750': len(model_rankings[model]['Below_750'])
    })

# Verify total count
for model in models:
    total_problems = (len(model_rankings[model]['Top_250']) +
                      len(model_rankings[model]['250_to_750']) +
                      len(model_rankings[model]['Below_750']))
    if total_problems != len(problems):
        print(f"Warning: Total problems for model {model} ({total_problems}) does not equal {len(problems)}")

# Print classification results
print("Ranking classification results for each model:")
for model, rankings in model_rankings.items():
    print(f"\nModel: {model}")
    print(f"Top 250 ({len(rankings['Top_250'])} problems): {rankings['Top_250']}")
    print(f"250 to 750 ({len(rankings['250_to_750'])} problems): {rankings['250_to_750']}")
    print(f"Below 750 ({len(rankings['Below_750'])} problems): {rankings['Below_750']}")

# Save ranking classification to CSV
ranking_df = pd.DataFrame(csv_ranking_data)
ranking_df.to_csv('output.csv', index=False, encoding='utf-8-sig')
print("\nCSV file generated: output.csv")
