import pandas as pd
import os
import glob
import argparse # Import argparse
from datetime import datetime

# Challenge mapping (kept inside function for now, could be loaded from external JSON/CSV)
CHALLENGE_MAPPING = {
    "1_not_gate": "NOT Gate", "2_second_tick": "Second Tick", "3_xor_gate": "XOR Gate",
    "4_or3_gate": "Bigger OR Gate", "5_and3_gate": "Bigger AND Gate", "6_xnor_gate": "XNOR Gate",
    "7_double_trouble": "Double Trouble", "8_odd_signal": "ODD Number of Signals",
    "9_counting_signals": "Counting Signals", "10_half_adder": "Half Adder",
    "11_full_adder": "Full Adder", "12_odd_change": "Odd Ticks", "13_inverter_1bit": "Bit Inverter",
    "14_or_8bit": "Byte OR", "15_not_8bit": "Byte NOT", "16_adder_8bit": "Adding Bytes",
    "17_mux_8bit": "Input Selector", "18_opposite_number": "Signed Negator",
    "19_elegant_storage": "Saving Gracefully", "20_store_byte": "Saving Bytes",
    "21_decoder_1bit": "1 Bit Decoder", "22_decoder_3bit": "3 Bit Decoder",
    "23_logic_engine": "Logic Engine", "24_box": "Little Box", "25_counter": "Counter",
    "26_arithmetic_engine": "Arithmetic Engine", "27_instruction_decoder": "Instruction Decoder",
    "28_conditional_checker": "Conditions"
    # Add any other challenges here
}

def extract_number(subfolder):
    """Extracts the numeric prefix from a subfolder name for sorting."""
    if pd.isna(subfolder): return float('inf')
    try:
        num_part = str(subfolder).split('_')[0]
        return int(num_part)
    except: return float('inf')

def merge_experiment_results(input_dir, output_csv_path):
    """
    Merges 'Total logic gates' from multiple '*-less.csv' files found in input_dir
    into a single CSV file, mapping challenge names and sorting.

    Args:
        input_dir (str): Directory containing the '*-less.csv' files.
        output_csv_path (str): Path to save the merged output CSV file.
    """
    print(f"Searching for '*-less.csv' files in: {input_dir}")
    search_pattern = os.path.join(input_dir, '**', '*-less.csv') # Recursive search
    csv_files = glob.glob(search_pattern, recursive=True)

    if not csv_files:
        print(f"Error: No '*-less.csv' files found in '{input_dir}' or its subdirectories.")
        return

    print(f"Found {len(csv_files)} files to merge:")
    for f in csv_files:
        print(f"  - {f}")

    dataframes = []

    for csv_file in csv_files:
        # Extract model/file label from filename
        file_label = os.path.basename(csv_file).replace("-less.csv", "")
        print(f"  Processing: {file_label} from {csv_file}")

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Warning: Could not read or process {csv_file}. Skipping. Error: {e}")
            continue

        # Select and rename required columns
        useful_columns = ['Subfolder', 'Total logic gates']
        if not all(col in df.columns for col in useful_columns):
            print(f"Warning: {csv_file} missing required columns ('Subfolder', 'Total logic gates'). Skipped.")
            continue

        # Keep only necessary columns and rename gates column
        df_select = df[useful_columns].copy() # Use copy
        df_select.rename(columns={'Total logic gates': f'{file_label}_gates'}, inplace=True)
        dataframes.append(df_select)

    if not dataframes:
        print("Error: No valid data could be extracted from any input CSV files. Merge aborted.")
        return

    # Merge all dataframes based on 'Subfolder'
    # Start with the first dataframe, then iteratively merge others
    merged_df = dataframes[0]
    for df_to_merge in dataframes[1:]:
        merged_df = pd.merge(merged_df, df_to_merge, on='Subfolder', how='outer')

    # --- Sorting ---
    # Add sorting key and sort by challenge number
    merged_df['sort_key'] = merged_df['Subfolder'].apply(extract_number)
    merged_df = merged_df.sort_values('sort_key').drop(columns=['sort_key'])

    # --- Add Mapped Names ---
    # Add the human-readable challenge name column
    merged_df['游戏关卡名称'] = merged_df['Subfolder'].map(CHALLENGE_MAPPING).fillna("Unknown Challenge") # Add fallback

    # Reorder columns for better readability (optional)
    cols = ['Subfolder', '游戏关卡名称'] + [col for col in merged_df.columns if col not in ['Subfolder', '游戏关卡名称']]
    merged_df = merged_df[cols]


    # --- Saving ---
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    try:
        merged_df.to_csv(output_csv_path, index=False)
        print(f"Merged results saved to: {output_csv_path}")
    except IOError as e:
        print(f"Error writing merged CSV file {output_csv_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges 'Total logic gates' from multiple '*-less.csv' files into a single summary CSV.")
    parser.add_argument("--input-dir", required=True,
                        help="Directory containing the '*-less.csv' files (one per model/run). Can search recursively.")
    parser.add_argument("--output-csv", required=True, help="Path to save the merged output CSV file.")
    args = parser.parse_args()

    merge_experiment_results(args.input_dir, args.output_csv)