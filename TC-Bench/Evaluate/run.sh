#!/bin/bash

# --- Functions ---

# Function to check if a folder contains any non-empty .v files
has_non_empty_v_file() {
    local folder_path="$1"
    if find "$folder_path" -maxdepth 1 -name '*.v' -type f -size +0c -print -quit | grep -q .; then
        return 0 # Found a non-empty .v file
    else
        return 1 # No non-empty .v files found
    fi
}

# Function to execute a script in a given folder
execute_script() {
    local folder_path="$1"
    local script_name="$2"
    local script_path="$folder_path/$script_name"

    if [[ ! -f "$script_path" ]]; then
        # Changed message slightly for clarity
        echo "--> Script '$script_name' not found in '$folder_path'. Skipping execution."
        return 1
    fi

    echo "--> Executing '$script_name' in '$folder_path'"
    # Uncomment if needed, but can be verbose
    # echo "    Script full path: $script_path"

    local start_time end_time duration status
    start_time=$(date +%s)

    # Execute in a subshell to isolate cd
    (
        cd "$folder_path" || exit 1 # Exit subshell if cd fails
        bash "$script_name"
    )
    status=$? # Capture exit status of the subshell/script
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    if [[ $status -ne 0 ]]; then
        # More prominent error message
        echo -e "\033[1;31mERROR:\033[0m Execution of '$script_name' in '$folder_path' failed (Exit code: $status)."
    fi

    if [[ $duration -gt 10 ]]; then
        echo -e "\033[1;33mWARNING:\033[0m Execution of '$script_name' in '$folder_path' took $duration seconds (> 10s)."
    fi

    return $status
}

# Function to process folders and execute appropriate scripts
process_folders() {
    local base_folder="$1"
    shift
    local seq_folders=("$@") # Capture remaining args as seq_folders

    # Use find to iterate through top-level challenge directories
    find "$base_folder" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r challenge_folder; do
        local challenge_name
        challenge_name=$(basename "$challenge_folder")
        echo "Processing challenge: $challenge_name"

        # Determine which script to execute (logic seems fixed to run.sh currently)
        local script_to_run="run.sh"
        # The check `[[ " ${seq_folders[*]} " == *" $subfolder_name "* ]]` was comparing
        # the *base* folder name (like '3_xor_gate') against the seq_folders list.
        # This check seems intended for sequence-dependent scripts, but the example uses 'run.sh' anyway.
        # Keeping the logic, but clarifying the variable name.
        if [[ " ${seq_folders[*]} " =~ " $challenge_name " ]]; then
            # This block currently does nothing different. Adjust if needed.
            echo "    (Challenge $challenge_name is listed in sequence-specific folders - using $script_to_run)"
            script_to_run="run.sh" # Explicitly set, though it's the default
        fi

        # Process attempt sub-folders within the challenge directory
        # Use find again for robustness
        find "$challenge_folder" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r attempt_folder; do
             # Check for non-empty .v files in the attempt folder
            if ! has_non_empty_v_file "$attempt_folder"; then
                echo "    Skipping attempt $(basename "$attempt_folder") (no non-empty .v files found in '$attempt_folder')."
                continue
            fi

            execute_script "$attempt_folder" "$script_to_run"
        done
        echo "Finished processing challenge: $challenge_name"
        echo # Add a blank line for readability between challenges
    done
}

# --- Main script logic ---

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <base_folder_containing_model_results> [seq_folder1 seq_folder2 ...]"
    exit 1
fi

base_folder="$1"
shift # Remove base_folder from argument list
seq_folders=("$@") # Remaining arguments are seq_folders

if [[ ! -d "$base_folder" ]]; then
    echo "Error: Invalid base folder path: $base_folder"
    exit 1
fi

echo "Starting simulation runs in base folder: $base_folder"
process_folders "$base_folder" "${seq_folders[@]}"
echo "Finished all simulation runs."