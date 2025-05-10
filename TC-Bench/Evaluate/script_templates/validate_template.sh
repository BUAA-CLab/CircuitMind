#!/bin/bash
# Template for validate.sh - ##MODULE## will be replaced
# Uses SCRIPT_DIR to find sibling files (_ref.v, testbench.v)

# --- Get Script's Own Directory ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    echo "Error (validate.sh): Could not determine validate.sh script directory."
    exit 1
fi
# --- End Get Script Dir ---

# --- Module Name Placeholder ---
MODULE="##MODULE##" # This line is targeted by sed in setup_challenge_scripts.sh

# --- End Placeholder ---

echo "Validation (validate.sh): MODULE=$MODULE, ScriptDir(ChallengeDir)=$SCRIPT_DIR"

# --- Get Attempt Verilog File from Argument ---
if [ -z "$1" ]; then echo "Error (validate.sh): Path to attempt's Verilog file required."; exit 1; fi
ATTEMPT_VERILOG_FILE="$1"
if [ ! -f "$ATTEMPT_VERILOG_FILE" ]; then echo "Error (validate.sh): Attempt Verilog '$ATTEMPT_VERILOG_FILE' not found."; exit 1; fi
echo "Validation (validate.sh): Processing attempt file: $ATTEMPT_VERILOG_FILE"
# --- End Input Handling ---

# --- Define file paths using SCRIPT_DIR (Challenge Directory) ---
REF_VERILOG_FILE="$SCRIPT_DIR/${MODULE}_ref.v"
TESTBENCH_FILE="$SCRIPT_DIR/testbench.v"
# Intermediate and output files should ideally be in ATTEMPT_DIR or be unique per attempt
ATTEMPT_DIR=$(dirname "$ATTEMPT_VERILOG_FILE")
OUTPUT_VVP="${ATTEMPT_DIR}/${MODULE}_$(basename "$ATTEMPT_VERILOG_FILE" .v).vvp" 
SIM_OUTPUT_TXT="${ATTEMPT_DIR}/${MODULE}_$(basename "$ATTEMPT_VERILOG_FILE" .v)_sim_output.txt"
TIMEOUT=3
# --- End File Paths ---

# --- Check required base files ---
echo "Debug (validate.sh): Checking for Ref: $REF_VERILOG_FILE"
if [ ! -f "$REF_VERILOG_FILE" ]; then echo "Error (validate.sh): Reference file not found at $REF_VERILOG_FILE"; exit 1; fi
echo "Debug (validate.sh): Checking for TB: $TESTBENCH_FILE"
if [ ! -f "$TESTBENCH_FILE" ]; then echo "Error (validate.sh): Testbench file not found at $TESTBENCH_FILE"; exit 1; fi
# --- End Check ---

echo "Compiling attempt ($ATTEMPT_VERILOG_FILE), reference ($REF_VERILOG_FILE), and testbench ($TESTBENCH_FILE)..."
iverilog -o "$OUTPUT_VVP" "$ATTEMPT_VERILOG_FILE" "$REF_VERILOG_FILE" "$TESTBENCH_FILE"
COMPILE_STATUS=$?

# Clean up intermediate files upon exit using trap
# Ensure cleanup happens for this script's intermediates only.
trap 'rm -f "$OUTPUT_VVP" "$SIM_OUTPUT_TXT"' EXIT

if [ $COMPILE_STATUS -ne 0 ]; then
    echo "Compilation failed (iverilog exit status: $COMPILE_STATUS)."
    exit 1
fi

if [ ! -f "$OUTPUT_VVP" ]; then
    echo "Compilation error: Output file $OUTPUT_VVP not created by iverilog."
    exit 1
fi

echo "Running simulation..."
# Clear previous simulation output if it exists
>"$SIM_OUTPUT_TXT"

if command -v timeout &> /dev/null; then
    timeout $TIMEOUT vvp "$OUTPUT_VVP" > "$SIM_OUTPUT_TXT"
    EXIT_CODE=$?
else
    echo "Warning (validate.sh): 'timeout' command not found. Running without time limit."
    vvp "$OUTPUT_VVP" > "$SIM_OUTPUT_TXT"
    EXIT_CODE=$?
fi

# Analyze simulation output
if [ $EXIT_CODE -eq 124 ]; then echo "Test failed: Simulation timed out after $TIMEOUT seconds."; exit 2; fi # Standard timeout exit code
if [ $EXIT_CODE -ne 0 ]; then echo "Test failed: Simulation execution failed with vvp exit code $EXIT_CODE."; exit 1; fi


# Check for success message in the simulation output file
# Make sure the grep pattern exactly matches what your testbench outputs on success.
if grep -i -q "All tests passed: Passed" "$SIM_OUTPUT_TXT"; then
    echo "All tests passed: Passed"
    echo "Validation successful for $ATTEMPT_VERILOG_FILE."
    # rm -f "$OUTPUT_VVP" "$SIM_OUTPUT_TXT" # Clean up on success via trap
    exit 0
else
    echo "Test failed: Success message 'All tests passed: Passed' not found in $SIM_OUTPUT_TXT."
    echo "--- Simulation Output ($SIM_OUTPUT_TXT) ---"
    cat "$SIM_OUTPUT_TXT"
    echo "-------------------------------------"
    # rm -f "$OUTPUT_VVP" "$SIM_OUTPUT_TXT" # Clean up on failure via trap
    exit 1
fi