import re
import csv
import argparse # Import argparse
import os

def extract_delay_path_gates(output):
    """Extract Longest delay, Longest path, Total logic gates, and Total delay from script output."""
    # Make patterns slightly more robust to whitespace variations
    delay_pattern = r"Longest delay:\s*([\d.]+)\s*ns"
    path_pattern = r"Longest path:\s*(.+)" # Greedily match the rest of the line
    gates_pattern = r"Total logic gates:\s*(\d+)"
    total_delay_pattern = r"Total delay:\s*(\d+)" # Assuming 'Total delay' is the key phrase

    delay_match = re.search(delay_pattern, output)
    path_match = re.search(path_pattern, output)
    gates_match = re.search(gates_pattern, output)
    total_delay_match = re.search(total_delay_pattern, output)

    # Extract path carefully, removing potential trailing characters if needed
    longest_path = None
    if path_match:
        # Strip whitespace and potentially remove common trailing noise if necessary
        longest_path = path_match.group(1).strip()
        # Example: if path sometimes includes unwanted trailing text like " (in module...)"
        # longest_path = longest_path.split(" (in module")[0].strip()


    return {
        "Longest delay (ns)": delay_match.group(1) if delay_match else None,
        "Longest path": longest_path,
        "Total logic gates": gates_match.group(1) if gates_match else None,
        "Total delay": total_delay_match.group(1) if total_delay_match else None,
    }

def process_outputs(log_contents):
    """Process multiple outputs from a log file and extract required information."""
    # Split based on the "Executing" line pattern
    executions = re.split(r"--> Executing '.*?' in '(.*?)'", log_contents)
    results = []
    failed_simulations = [] # Store paths/info of failed simulations

    # The split results in: [text_before_first_exec, path1, output1, path2, output2, ...]
    if len(executions) < 3:
        print("Warning: Could not find any '--> Executing' blocks in the log content.")
        return results, failed_simulations

    current_challenge_folder = None

    # Iterate through path/output pairs
    for i in range(1, len(executions), 2):
        full_path = executions[i].strip()
        output = executions[i+1].strip() if (i+1) < len(executions) else ""

        # Extract challenge folder and attempt folder names from the path
        # Assumes path structure like ".../challenge_name/attempt_name"
        path_parts = full_path.replace("\\", "/").strip('/').split('/')
        if len(path_parts) >= 2:
            attempt_folder = path_parts[-1]
            challenge_folder = path_parts[-2]
        else:
            print(f"Warning: Could not determine challenge/attempt from path: {full_path}")
            attempt_folder = os.path.basename(full_path) # Best guess
            challenge_folder = "Unknown" # Best guess

        # Check for simulation failure messages
        # Use elif to avoid adding to failed list multiple times for one block
        is_failure = False
        if "Running simulation..." not in output and "Executing" in log_contents: # Basic check if simulation even started
             # Avoid flagging the very first split part if it lacks "Executing"
             if i > 0 : # Check if it's not the text before the first execution block
                 failed_simulations.append({ "path": full_path, "reason": "Simulation start message not found."})
                 is_failure = True
        elif "Test failed:" in output: # General failure message
            # Try to capture the specific reason if available
            fail_reason_match = re.search(r"Test failed:(.*)", output)
            reason = fail_reason_match.group(1).strip() if fail_reason_match else "No success message found or specific reason missing."
            failed_simulations.append({ "path": full_path, "reason": reason})
            is_failure = True
        elif "ERROR:" in output and "Execution of" in output and "failed" in output: # Check for run-v2.sh error messages
             fail_reason_match = re.search(r"ERROR:.*failed \((.*)\)", output)
             reason = fail_reason_match.group(1).strip() if fail_reason_match else "Script execution failed (run-v2.sh error)."
             failed_simulations.append({ "path": full_path, "reason": reason})
             is_failure = True
        # Add other failure patterns here if needed...


        # Add a separator row when the challenge folder changes
        if challenge_folder != current_challenge_folder:
            # Only add separator if it's not the very first entry
            if current_challenge_folder is not None:
                 results.append({}) # Add an empty dict for a blank row in CSV
            results.append({"Subfolder": challenge_folder, "Child Folder": "", "Longest delay (ns)": "",
                            "Longest path": "", "Total logic gates": "", "Total delay": ""})
            current_challenge_folder = challenge_folder

        extracted_data = extract_delay_path_gates(output)

        # Combine path info with extracted metrics
        row_data = {
            "Subfolder": "", # Keep this blank for data rows
            "Child Folder": attempt_folder,
            "Longest delay (ns)": extracted_data["Longest delay (ns)"],
            "Longest path": extracted_data["Longest path"],
            "Total logic gates": extracted_data["Total logic gates"],
            "Total delay": extracted_data["Total delay"],
            # Optionally add a 'Status' column
            # "Status": "Failed" if is_failure else "Success" # Mark failures explicitly
        }
        results.append(row_data)

    return results, failed_simulations

def save_to_csv(data, csv_filename):
    """Save extracted data to a CSV file, converting None to empty strings."""
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    fieldnames = ["Subfolder", "Child Folder", "Longest delay (ns)", "Longest path", "Total logic gates", "Total delay"]

    try:
        # Preprocess data: Convert None to '' for specific columns before writing
        processed_data = []
        cols_to_process_for_none = ["Longest delay (ns)", "Total logic gates", "Total delay"] # Columns where None might appear and should be ''
        for row_dict in data:
            new_row = row_dict.copy() # Work on a copy
            for col in fieldnames: # Ensure all fields exist even if empty
                if col not in new_row:
                     new_row[col] = '' # Or None, depending on desired output for completely missing columns

            for col in cols_to_process_for_none:
                if col in new_row and new_row[col] is None:
                    new_row[col] = '' # Replace None with empty string

            # Child Folder should be integer if present
            if 'Child Folder' in new_row and new_row['Child Folder'] is not None:
                 try:
                     # Attempt conversion, keep original if error (e.g., it's already a header row's empty string)
                     new_row['Child Folder'] = int(new_row['Child Folder'])
                 except (ValueError, TypeError):
                     pass # Keep original value if conversion fails

            processed_data.append(new_row)

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            # Write the processed data
            writer.writerows(processed_data)
        print(f"Data successfully saved to {csv_filename}")
    except IOError as e:
        print(f"Error writing to CSV file {csv_filename}: {e}")
    except Exception as e:
         print(f"An unexpected error occurred during CSV writing: {e}")


# Main function
if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Extracts simulation results from a log file generated by run-v2.sh.")
    parser.add_argument("--log-file", required=True, help="Path to the input log file containing simulation outputs.")
    parser.add_argument("--output-csv", required=True, help="Path to save the extracted results in CSV format.")
    args = parser.parse_args()

    log_file = args.log_file
    csv_file = args.output_csv

    print(f"Processing log file: {log_file}")

    try:
        # Read with robust encoding handling
        with open(log_file, "r", encoding='utf-8', errors='ignore') as file:
            log_contents = file.read()

        if not log_contents:
            print(f"Warning: Log file '{log_file}' is empty.")
            results, failed_simulations = [], []
        else:
            results, failed_simulations = process_outputs(log_contents)

        # Save results to CSV
        if results:
            save_to_csv(results, csv_file)
        else:
            print("No results were extracted from the log file.")

        # Print paths of failed simulations
        if failed_simulations:
            print("\n--- Failed Simulations Detected ---")
            # Use a set to show unique paths if the same path failed multiple ways
            unique_failed_paths = {failure['path'] for failure in failed_simulations}
            for path in sorted(list(unique_failed_paths)):
                 reasons = [f['reason'] for f in failed_simulations if f['path'] == path]
                 print(f"Path: {path}\n  Reason(s): {'; '.join(reasons)}")
            print("---------------------------------")
        else:
            print("\nNo simulation failures detected in the log.")

    except FileNotFoundError:
        print(f"Error: Input log file '{log_file}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")