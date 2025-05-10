import pandas as pd
import argparse # Import argparse
import os

def extract_number(subfolder):
    """Extracts the numeric prefix from a subfolder name for sorting"""
    if pd.isna(subfolder):
        return float('inf') # Handle potential NaN input
    try:
        # Allow names like '1_...' or '1'
        num_part = str(subfolder).split('_')[0]
        return int(num_part)
    except (ValueError, AttributeError, IndexError):
        # Return infinity for non-numeric prefixes or errors
        return float('inf')

def main(input_csv_path, output_csv_path):
    """
    Reads raw experimental results, calculates a combined metric, finds the
    best non-zero result for each challenge, sorts, and saves to a new CSV.
    """
    print(f"Analyzing results from: {input_csv_path}")

    try:
        df = pd.read_csv(input_csv_path)
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
    required_cols = ['Subfolder', 'Total logic gates', 'Total delay']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Input CSV missing required columns ({', '.join(required_cols)}). Found: {list(df.columns)}")
        return

    # --- Data Processing ---
    # Convert potentially non-numeric data to numeric, coercing errors to NaN
    df['Total logic gates'] = pd.to_numeric(df['Total logic gates'], errors='coerce')
    df['Total delay'] = pd.to_numeric(df['Total delay'], errors='coerce')

    # --- Corrected total calculation method ---
    # Use simple addition (NaN + number = NaN)
    df['total'] = df['Total logic gates'] + df['Total delay']
    # Fill resulting NaN 'total' values with infinity for comparison
    df['total'] = df['total'].fillna(float('inf'))
    # --- End of correction ---

    # Forward fill Subfolder names to associate rows with challenges
    # Using forward fill (ffill) - more efficient than original loop
    df['Subfolder'] = df['Subfolder'].ffill()

    # Filter out rows where Subfolder is still NaN (header rows, separators) or total is inf
    # Note: NaN total has been filled with inf, so checking for inf covers both cases
    df_filtered = df.dropna(subset=['Subfolder'])
    df_filtered = df_filtered[df_filtered['total'] != float('inf')] # Keep only rows with finite total

    # **Filter out zero TOTALS**
    # Ensure only results where gates + delay > 0 are considered
    df_non_zero = df_filtered[df_filtered['total'] > 0].copy() # Use .copy() to avoid SettingWithCopyWarning

    if df_non_zero.empty:
        print("Warning: No valid non-zero 'total' (gates + delay) results found after filtering.")
        # To maintain consistency, save an empty file
        min_results = pd.DataFrame(columns=df.columns) # Create an empty DataFrame with the same columns
        # Ensure 'total' column exists even in an empty DataFrame (if needed downstream)
        if 'total' not in min_results.columns:
             min_results['total'] = pd.Series(dtype='float64')
    else:
        # Get the index of the row with the minimum non-zero 'total' for each Subfolder
        # idxmin() returns the first index in case of ties
        try: # Add try-except for idxmin in case groups become empty after filtering
            min_indices = df_non_zero.loc[df_non_zero.groupby('Subfolder')['total'].idxmin()].index
             # Select the full rows using these indices
            min_results = df_non_zero.loc[min_indices].copy() # Use .copy()
        except KeyError:
             print("Warning: Error during finding minimum 'total' per group. Saving empty results.")
             min_results = pd.DataFrame(columns=df.columns)
             if 'total' not in min_results.columns:
                 min_results['total'] = pd.Series(dtype='float64')

        # --- Sorting (only if results were found) ---
        if not min_results.empty:
            min_results['sort_key'] = min_results['Subfolder'].apply(extract_number)
            min_results = min_results.sort_values('sort_key').drop(columns=['sort_key'])

    # --- Saving ---
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    try:
        # Convert relevant columns to Nullable Integer type before saving
        # 'Longest delay (ns)' might be float, keep as is or convert to Float64
        # 'Total logic gates', 'Total delay' should be integers
        cols_to_int64 = ['Total logic gates', 'Total delay']
        # Child Folder might also be an integer attempt number
        if 'Child Folder' in min_results.columns:
            cols_to_int64.append('Child Folder')

        if not min_results.empty: # Only process if DataFrame is not empty
            for col in cols_to_int64:
                if col in min_results.columns:
                    # Ensure numeric first, coercing errors if somehow non-numeric slipped through
                    min_results[col] = pd.to_numeric(min_results[col], errors='coerce')
                    # Convert to nullable integer (uses pd.NA for missing values)
                    min_results[col] = min_results[col].astype('Int64')

            # Optional: Convert Longest delay (ns) to nullable Float if needed
            # if 'Longest delay (ns)' in min_results.columns:
            #    min_results['Longest delay (ns)'] = pd.to_numeric(min_results['Longest delay (ns)'], errors='coerce')
            #    min_results['Longest delay (ns)'] = min_results['Longest delay (ns)'].astype('Float64')

        # Save the processed DataFrame
        min_results.to_csv(output_csv_path, index=False)

        if not df_non_zero.empty and not min_results.empty:
             print(f"Saved best non-zero 'total' result per challenge (with Int64 types) to: {output_csv_path}")
        else:
             if df_non_zero.empty:
                message = "no valid non-zero 'total' results found after filtering"
             else:
                 message = "error during minimum calculation or no valid results remained"
             print(f"Saved empty results file ({message}) to: {output_csv_path}")

    except IOError as e:
        print(f"Error writing output CSV file {output_csv_path}: {e}")
    except Exception as e: # Catch potential conversion errors too
         print(f"An error occurred during processing or saving {output_csv_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyzes raw simulation results CSV to find the best result per challenge based on 'Total logic gates' + 'Total delay'.")
    parser.add_argument("--input-csv", required=True, help="Path to the raw results CSV file (output of extract-v2.py).")
    parser.add_argument("--output-csv", required=True, help="Path to save the summarized 'best results' CSV file (e.g., model-less.csv).")
    args = parser.parse_args()

    main(args.input_csv, args.output_csv)
