import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import argparse # Import argparse
from datetime import datetime

def extract_number(subfolder):
    """Extracts the numeric prefix from a subfolder name for sorting."""
    if pd.isna(subfolder): return float('inf')
    try:
        num_part = str(subfolder).split('_')[0]
        return int(num_part)
    except: return float('inf')

def plot_experiment_results(input_dir, output_png_path):
    """
    Reads multiple *-less.csv files from an input directory, plots 'Total logic gates'
    for each model against challenge names (sorted numerically) on a single scatter plot.

    Args:
        input_dir (str): Directory containing the '*-less.csv' files for different models.
        output_png_path (str): Path to save the output PNG plot.
    """
    print(f"Searching for '*-less.csv' files in: {input_dir}")
    # Use recursive=True if files might be nested deeper (e.g., input_dir/model_name/model-less.csv)
    # Adjust pattern if needed. Assuming structure: input_dir/model_name-less.csv
    search_pattern = os.path.join(input_dir, '**', '*-less.csv') # Search recursively
    csv_files = glob.glob(search_pattern, recursive=True)

    if not csv_files:
        print(f"Error: No '*-less.csv' files found in '{input_dir}' or its subdirectories.")
        return

    print(f"Found {len(csv_files)} files to compare:")
    for f in csv_files:
        print(f"  - {f}")

    plt.figure(figsize=(15, 7)) # Adjusted figure size for potentially many levels

    all_data = []  # Store data for plotting

    for csv_file in csv_files:
        # Extract model name from filename (more robustly)
        base_name = os.path.basename(csv_file)
        model_name = base_name.replace("-less.csv", "") # Simple replacement
        print(f"  Processing model: {model_name} from {csv_file}")

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Warning: Could not read or process {csv_file}. Skipping. Error: {e}")
            continue

        # Ensure required columns exist
        if not all(col in df.columns for col in ['Subfolder', 'Total logic gates']):
            print(f"Warning: {csv_file} missing 'Subfolder' or 'Total logic gates' column. Skipped.")
            continue

        # Convert gates to numeric, coercing errors
        df['Total logic gates'] = pd.to_numeric(df['Total logic gates'], errors='coerce')

        # Filter out rows with invalid Subfolder or missing gate counts
        df_valid = df.dropna(subset=['Subfolder', 'Total logic gates']).copy() # Use copy

        if not df_valid.empty:
            # Add sorting key and sort by challenge number
            df_valid['level_number'] = df_valid['Subfolder'].apply(extract_number)
            df_valid = df_valid.sort_values('level_number')
            all_data.append({'name': model_name, 'data': df_valid})
        else:
            print(f"Warning: No valid data found in {csv_file} after cleaning.")

    if not all_data:
        print("Error: No valid data could be extracted from any input CSV file. Plot cannot be generated.")
        plt.close() # Close the empty figure
        return

    # --- Plotting ---
    # Collect all unique, sorted challenge names for the x-axis
    all_challenges = pd.concat([d['data']['Subfolder'] for d in all_data]).unique()
    # Create a temporary series for sorting, apply extract_number, then get sorted names
    challenge_series = pd.Series(all_challenges)
    sorted_challenges = challenge_series.iloc[challenge_series.apply(extract_number).argsort()].tolist()


    # Plot data for each model
    markers = ['o', 's', '^', 'D', 'v', '>', '<', 'p', '*', 'h'] # Cycle through markers
    for i, model_info in enumerate(all_data):
        model_name = model_info['name']
        df_plot = model_info['data']
        marker = markers[i % len(markers)]
        # Plot only the points for challenges present in this model's data
        plt.scatter(df_plot['Subfolder'], df_plot['Total logic gates'],
                    marker=marker, label=model_name, alpha=0.7, s=50) # Increased size slightly

    # --- Formatting ---
    plt.title('Model Comparison: Logic Gates per Challenge (Best Results)')
    plt.xlabel('Challenge (Sorted Numerically)')
    plt.ylabel('Total Logic Gates (Lower is Better)')

    # Set x-ticks explicitly to ensure correct order and spacing
    plt.xticks(ticks=range(len(sorted_challenges)), labels=sorted_challenges, rotation=75, ha='right') # Rotate more for long names
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.) # Move legend outside plot

    plt.grid(True, axis='y', linestyle='--', alpha=0.6) # Grid lines for y-axis only
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend

    # --- Saving ---
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    try:
        plt.savefig(output_png_path, bbox_inches='tight') # Use bbox_inches='tight'
        print(f"Comparison plot saved as: {output_png_path}")
    except Exception as e:
        print(f"Error saving plot to {output_png_path}: {e}")
    finally:
         plt.close() # Close the plot figure


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compares 'Total logic gates' from multiple '*-less.csv' result files and generates a scatter plot.")
    parser.add_argument("--input-dir", required=True,
                        help="Directory containing the '*-less.csv' files (one per model/run). Can search recursively.")
    parser.add_argument("--output-png", required=True, help="Path to save the output comparison plot PNG file.")
    args = parser.parse_args()

    plot_experiment_results(args.input_dir, args.output_png)