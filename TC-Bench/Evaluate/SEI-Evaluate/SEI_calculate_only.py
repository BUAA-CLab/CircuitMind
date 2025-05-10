import pandas as pd
import numpy as np
from datetime import datetime

# Define input filename
input_filename = "Reference_Format/SEI_calculate_only_input.csv"
# Extract the base name of the file without extension, e.g., 'data'
input_base_name = input_filename.split('.')[0]

# Get current date and time
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

# Read the CSV file
df = pd.read_csv(input_filename)

# Get all column names
columns = df.columns

# Find all columns containing '_total'
total_columns = [col for col in columns if '_total' in col]

# Create a new DataFrame to store the results
result_df = df.copy()

# Calculate the reciprocal for each total column, handling empty values as 0
reciprocal_columns = []
for col in total_columns:
    reciprocal_col = f'{col}_reciprocal'
    reciprocal_columns.append(reciprocal_col)
    # Calculate reciprocal, handle 0, NaN, or Inf by setting to NaN first
    result_df[reciprocal_col] = np.where(
        (df[col] == 0) | (df[col].isna()) | (df[col] == np.inf),
        np.nan,
        round(1 / df[col], 3)
    )
    # Fill NaN values (from original NaNs or reciprocal calculation issues) with 0
    result_df[reciprocal_col] = result_df[reciprocal_col].fillna(0)

# Create a DataFrame containing only the reciprocal columns
reciprocals_only_df = result_df[['Subfolder'] + reciprocal_columns]

# Save the CSV containing only reciprocal columns
reciprocals_only_filename = f'{input_base_name}_reciprocals_only_{current_datetime}.csv'
reciprocals_only_df.to_csv(reciprocals_only_filename, index=False)

print("\nProcessing complete!")
print(f"Results containing only reciprocal columns saved to '{reciprocals_only_filename}'")
