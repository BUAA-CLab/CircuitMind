#!/bin/bash

# --- Functions ---

# Function to check if a folder contains any non-empty .v files
has_non_empty_v_file() {
    local folder_path="$1"
    # Use find for more robust checking, including hidden files if needed
    if find "$folder_path" -maxdepth 1 -name '*.v' -type f -size +0c -print -quit | grep -q .; then
        return 0 # Found a non-empty .v file
    else
        return 1 # No non-empty .v files found
    fi
}

# Function to execute a script in a given folder and extract Total Logic Gates
execute_script() {
    local folder_path="$1"
    local script_name="$2"
    local temp_results_file="$3" # Added argument for temp file
    local script_path="$folder_path/$script_name"

    if [[ ! -f "$script_path" ]]; then
        echo "Script $script_name not found in $folder_path. Skipping..."
        return 1
    fi

    echo "Executing $script_name in $folder_path"

    local output
    # Capture output safely, handle potential errors during execution
    output=$(cd "$folder_path" && bash "$script_name")
    local exit_status=$?
    if [[ $exit_status -ne 0 ]]; then
         echo "Error executing $script_name in $folder_path (Exit code: $exit_status)"
         # Decide if you want to proceed or exit here based on severity
    fi


    # Extract Total Logic Gates from the output
    local total_gates
    total_gates=$(echo "$output" | grep -i "Total Logic Gates" | awk '{print $NF}')

    if [[ -n "$total_gates" && "$total_gates" =~ ^[0-9]+$ ]]; then
        echo "Total Logic Gates in $folder_path: $total_gates"
        # Append to the specified temp file
        echo "$folder_path $total_gates" >> "$temp_results_file"
    else
        echo "Total Logic Gates value not found or invalid in $folder_path"
        # Optionally append a failure marker if needed for downstream processing
        # echo "$folder_path INVALID" >> "$temp_results_file"
    fi
}

# Function to update the JSON file with the minimum Total Logic Gates
# Writes to a *new* output file instead of modifying in place
update_json_file() {
    local input_json_file="$1"
    local output_json_file="$2" # New argument for output path
    local min_value="$3"

    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo "Error: jq command not found. Please install jq."
        return 1
    fi

    # Ensure the input JSON exists
    if [[ ! -f "$input_json_file" ]]; then
         echo "Error: Input JSON file not found: $input_json_file"
         return 1
    fi

    # Use jq to update the value and write to the output file
    # Create parent directory for output if it doesn't exist
    mkdir -p "$(dirname "$output_json_file")"
    if jq --argjson gate_num "$min_value" '.["__XOR_"].gate_num = $gate_num' "$input_json_file" > "$output_json_file"; then
        echo "Updated JSON file written to: $output_json_file with gate_num: $min_value"
    else
        echo "Error updating JSON file using jq."
        # Optional: clean up partially written output file?
        # rm -f "$output_json_file"
        return 1
    fi
}

# --- Main script logic ---

# Check for the correct number of arguments
if [[ $# -ne 5 ]]; then
    echo "Usage: $0 <base_folder> <script_name> <input_json_file> <output_json_file> <temp_results_file>"
    exit 1
fi

# Assign arguments to variables for clarity
base_folder="$1"
script_name="$2"
input_json_file="$3"
output_json_file="$4"
temp_results_file="$5" # Use the provided path

# Validate inputs
if [[ ! -d "$base_folder" ]]; then
    echo "Invalid base folder path: $base_folder"
    exit 1
fi
if [[ ! -f "$input_json_file" ]]; then
    echo "Invalid input JSON file path: $input_json_file"
    exit 1
fi
# Ensure temp file path directory exists (or handle creation if desired)
mkdir -p "$(dirname "$temp_results_file")"

# Clear or create the temporary results file safely
> "$temp_results_file"

# Iterate over subfolders and execute the script
# Using find is generally safer than globbing, especially with unusual filenames
find "$base_folder" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r subfolder; do
    # Check for non-empty .v files before executing the script
    if ! has_non_empty_v_file "$subfolder"; then
        echo "Skipping $subfolder as it does not contain any non-empty .v files."
        continue
    fi
    execute_script "$subfolder" "$script_name" "$temp_results_file"
done

# Find the folder with the minimum Total Logic Gates value
if [[ -s "$temp_results_file" ]]; then
    # Handle potential "INVALID" lines if added in execute_script
    # Filter valid lines, sort numerically by the second field (gate count), get the first line
    min_result_line=$(grep -E ' [0-9]+$' "$temp_results_file" | sort -k2,2n | head -n 1)

    if [[ -n "$min_result_line" ]]; then
        min_value=$(echo "$min_result_line" | awk '{print $2}')
        min_folder=$(echo "$min_result_line" | awk '{print $1}') # Get the folder path too
        echo "Folder with minimum Total Logic Gates: $min_folder ($min_value gates)"

        # Update the JSON file with the minimum value
        update_json_file "$input_json_file" "$output_json_file" "$min_value"
    else
         echo "No valid numeric Total Logic Gates values found in $temp_results_file."
    fi
else
    echo "No valid results found in $temp_results_file."
fi

# Optional: Clean up temp file? Depends on whether you need it later.
# rm -f "$temp_results_file"