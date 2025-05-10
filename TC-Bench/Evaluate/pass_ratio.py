import pandas as pd
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import math
import argparse
import os

# Function to calculate binomial coefficient safely
def binomial_coefficient(n, k):
    if k < 0 or k > n:
        return 0
    try:
        # math.comb is preferred and available in Python 3.8+
        return math.comb(int(n), int(k))
    except AttributeError:
        # Fallback for older Python versions (less efficient)
        return math.factorial(int(n)) // (math.factorial(int(k)) * math.factorial(int(n - k)))
    except ValueError: # Handle potential non-integer inputs if necessary
         print(f"Warning: Non-integer input to binomial_coefficient: n={n}, k={k}")
         return 0


def extract_number(subfolder):
    """Extracts the numeric prefix from a subfolder name for sorting."""
    if pd.isna(subfolder): return float('inf')
    try:
        num_part = str(subfolder).split('_')[0]
        return int(num_part)
    except: return float('inf')


def calculate_pass_k(total_trials, successful_trials, k):
    """Calculates pass@k using the formula 1 - C(failed, k) / C(total, k)."""
    total_trials = int(total_trials)
    successful_trials = int(successful_trials)
    k = int(k)

    if total_trials <= 0 or k <= 0:
        return 0.0 # Cannot pass if no trials or k is non-positive

    failed_trials = total_trials - successful_trials
    if failed_trials < 0: failed_trials = 0 # Ensure non-negative

    # Denominator: C(total, k)
    c_total_k = binomial_coefficient(total_trials, k)
    if c_total_k == 0:
        # This happens if k > total_trials. If there are enough successful trials (>=k), pass rate is 1.
        # Otherwise, it's 0. More simply, if you can't pick k total, you can't pick k failures.
        # If k > total_trials, it's impossible to *not* pass if you have >=k successes (vacuously true?).
        # Let's define pass@k = 0 if k > total_trials for simplicity, unless successful_trials >= k?
        # The standard definition implies you need at least k trials.
        # print(f"Debug: C({total_trials}, {k}) = 0")
        return 0.0 # Pass@k is typically 0 if k > n

    # Numerator: C(failed, k)
    c_failed_k = binomial_coefficient(failed_trials, k)

    # Calculate pass@k: 1 - (Numerator / Denominator)
    pass_k_ratio = 1.0 - (c_failed_k / c_total_k)

    # Clamp result between 0 and 1 due to potential float inaccuracies
    return max(0.0, min(1.0, pass_k_ratio))


def main(input_csv_path, output_csv_path, plot_pass1_path, plot_pass5_path, total_trials_per_challenge):
    """
    Calculates pass@1 and pass@5 from raw results, saves results and plots.
    """
    print(f"Calculating pass ratio from: {input_csv_path}")
    print(f"Assuming {total_trials_per_challenge} total trials per challenge.")

    try:
        data = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found: {input_csv_path}")
        return
    except pd.errors.EmptyDataError:
         print(f"Error: Input CSV file is empty: {input_csv_path}")
         return
    except Exception as e:
        print(f"Error reading CSV file {input_csv_path}: {e}")
        return

    # Ensure required columns exist
    if not all(col in data.columns for col in ['Subfolder', 'Total logic gates']):
         print(f"Error: Input CSV missing required columns ('Subfolder', 'Total logic gates'). Found: {list(data.columns)}")
         return

    # --- Data Preparation ---
    # Forward fill the 'Subfolder' to associate attempts with challenges
    data['Subfolder'] = data['Subfolder'].ffill()
    # Drop rows where Subfolder is still NaN (e.g., empty separator rows)
    data.dropna(subset=['Subfolder'], inplace=True)
    # Keep only rows representing actual attempts (e.g., Child Folder is not empty)
    # This assumes the header rows have empty Child Folder. Adjust if needed.
    data = data[data['Child Folder'].notna() & (data['Child Folder'] != '')]


    # --- Calculation ---
    # Group by challenge (Subfolder)
    # Use observed=True in newer pandas if Subfolder is categorical
    grouped_data = data.groupby('Subfolder')

    results = []
    for experiment_name, group in grouped_data:
        # Count successful trials (where 'Total logic gates' is a valid number)
        # Convert to numeric first, coercing errors
        valid_gates = pd.to_numeric(group['Total logic gates'], errors='coerce')
        successful_trials = valid_gates.notna().sum()

        # Calculate pass@k
        pass_at_1 = calculate_pass_k(total_trials_per_challenge, successful_trials, 1)
        pass_at_5 = calculate_pass_k(total_trials_per_challenge, successful_trials, 5)

        results.append({
            'Challenge': experiment_name,
            'Total Trials': total_trials_per_challenge,
            'Successful Trials': successful_trials,
            'pass@1': pass_at_1,
            'pass@5': pass_at_5
        })

    if not results:
        print("Error: No results could be calculated. Check input data and grouping.")
        return

    # Convert results to DataFrame for sorting and saving
    results_df = pd.DataFrame(results)

    # --- Sorting ---
    # Add sorting key based on numeric prefix and sort
    results_df['sort_key'] = results_df['Challenge'].apply(extract_number)
    sorted_results_df = results_df.sort_values('sort_key').drop(columns=['sort_key'])

    # --- Saving Results CSV ---
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    try:
        # Ensure count columns are standard integers before saving
        # These columns should not have NaNs in the final results_df
        if not sorted_results_df.empty:
            sorted_results_df['Total Trials'] = sorted_results_df['Total Trials'].astype(int)
            sorted_results_df['Successful Trials'] = sorted_results_df['Successful Trials'].astype(int)

        # Save with float formatting for pass rates
        sorted_results_df.to_csv(output_csv_path, index=False, float_format='%.4f')
        print(f"Pass ratio results saved to: {output_csv_path}")
    except IOError as e:
        print(f"Error writing results CSV file {output_csv_path}: {e}")
    except Exception as e:
         print(f"An error occurred during processing or saving {output_csv_path}: {e}")



    # --- Generating Plots ---
    plot_metrics = {
        'pass@1': plot_pass1_path,
        'pass@5': plot_pass5_path
    }

    for metric, plot_path in plot_metrics.items():
        if not plot_path: # Skip if path not provided
             print(f"Skipping plot for {metric} as no output path was given.")
             continue

        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.figure(figsize=(15, 7)) # Wider figure
        plt.bar(sorted_results_df['Challenge'], sorted_results_df[metric], alpha=0.8, width=0.8) # Adjust width
        plt.title(f'{metric.upper()} Performance by Challenge (Sorted)')
        plt.xlabel('Challenge')
        plt.ylabel(metric.upper())
        plt.xticks(rotation=75, ha='right') # Rotate labels
        plt.ylim(0, 1.05) # Set y-axis limit slightly above 1
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        try:
            plt.savefig(plot_path)
            print(f"{metric.upper()} plot saved to: {plot_path}")
        except Exception as e:
            print(f"Error saving {metric} plot to {plot_path}: {e}")
        finally:
            plt.close() # Close plot figure


    # --- PrettyTable Output ---
    print("\n--- Pass Ratio Summary ---")
    table = PrettyTable()
    table.field_names = ["Challenge", "Total Trials", "Successful", "pass@1", "pass@5"]
    table.align = "l" # Align left
    table.align["Total Trials"] = "r"
    table.align["Successful"] = "r"
    table.align["pass@1"] = "r"
    table.align["pass@5"] = "r"


    for _, row in sorted_results_df.iterrows():
        table.add_row([
            row['Challenge'],
            row['Total Trials'],
            row['Successful Trials'],
            f"{row['pass@1']:.4f}", # Format floats
            f"{row['pass@5']:.4f}"
        ])

    print(table)
    print("------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculates pass@1 and pass@5 based on raw simulation results.")
    parser.add_argument("--input-csv", required=True, help="Path to the raw results CSV file (output of extract-v2.py).")
    parser.add_argument("--output-results-csv", required=True, help="Path to save the calculated pass ratio results CSV.")
    parser.add_argument("--output-plot-pass1", required=True, help="Path to save the pass@1 performance plot PNG.")
    parser.add_argument("--output-plot-pass5", required=True, help="Path to save the pass@5 performance plot PNG.")
    parser.add_argument("--total-trials", type=int, default=20, help="Assumed total number of trials per challenge (default: 20).")
    args = parser.parse_args()

    main(args.input_csv, args.output_results_csv, args.output_plot_pass1, args.output_plot_pass5, args.total_trials)