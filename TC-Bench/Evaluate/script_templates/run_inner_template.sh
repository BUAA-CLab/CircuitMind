#!/bin/bash
# This script runs inside the Attempt Directory

# Get the absolute path to the Verilog file for this attempt
ATTEMPT_DIR=$(pwd)
CHALLENGE_DIR_NAME=$(basename "$(dirname "$ATTEMPT_DIR")")
MODULE=${CHALLENGE_DIR_NAME#*_}
VERILOG_FILE="${ATTEMPT_DIR}/${MODULE}.v" # Assumes Verilog file is named MODULE.v

if [ -z "$MODULE" ]; then echo "Error: Cannot determine module name."; exit 1; fi
if [ ! -f "$VERILOG_FILE" ]; then echo "Error: Verilog file '$VERILOG_FILE' not found."; exit 1; fi

# Define paths to scripts in the parent (Challenge) directory
VALIDATE_SCRIPT="../validate.sh"
EVALUATE_SCRIPT="../evaluate.sh"

# Check if parent scripts exist
if [ ! -f "$VALIDATE_SCRIPT" ]; then echo "Error: validate.sh not found in parent directory."; exit 1; fi
if [ ! -f "$EVALUATE_SCRIPT" ]; then echo "Error: evaluate.sh not found in parent directory."; exit 1; fi

# Run Validation, pass the Verilog file path
echo "Attempt $(basename $ATTEMPT_DIR): Running Validation..."
bash "$VALIDATE_SCRIPT" "$VERILOG_FILE" # Use bash
VALIDATE_STATUS=$?

# Use robust check for non-zero exit status
if [ "$VALIDATE_STATUS" != "0" ]; then
    echo "Attempt $(basename $ATTEMPT_DIR): Validation failed (Exit code: $VALIDATE_STATUS)."
    exit 1
fi

# Run Performance Evaluation, pass the Verilog file path
echo "Attempt $(basename $ATTEMPT_DIR): Running Performance Evaluation..."
bash "$EVALUATE_SCRIPT" "$VERILOG_FILE" # Use bash
EVALUATE_STATUS=$?

# Use robust check for non-zero exit status
if [ "$EVALUATE_STATUS" != "0" ]; then
     echo "Attempt $(basename $ATTEMPT_DIR): Performance evaluation failed (Exit code: $EVALUATE_STATUS)."
     exit 1
fi

echo "Attempt $(basename $ATTEMPT_DIR): Processing completed successfully."
exit 0