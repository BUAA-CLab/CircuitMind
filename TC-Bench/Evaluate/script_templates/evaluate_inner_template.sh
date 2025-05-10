#!/bin/bash
# Template for inner evaluate.sh - Runs inside the Challenge Directory
# Uses SCRIPT_DIR to find compile.ys template
# Uses METRIC_SCRIPT_DIR_ABS env var for python scripts
# Uses OUTPUT_BASE_DIR env var to find device_types json

# --- Get Script's Own Directory ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then echo "Error: Could not determine evaluate.sh script directory."; exit 1; fi
# --- End Get Script Dir ---

# --- Dynamic Name & Input Handling ---
CHALLENGE_DIR_NAME=$(basename "$SCRIPT_DIR")
MODULE=${CHALLENGE_DIR_NAME#*_}
MODEL_NAME=$(basename "$(dirname "$SCRIPT_DIR")") # Assumes challenge_dir is inside model_dir

if [ -z "$1" ]; then echo "Error (evaluate.sh): Path to attempt's Verilog file required."; exit 1; fi
ATTEMPT_VERILOG_FILE="$1" # This is a relative or absolute path passed as an argument
if [ ! -f "$ATTEMPT_VERILOG_FILE" ]; then echo "Error (evaluate.sh): Attempt Verilog '$ATTEMPT_VERILOG_FILE' not found."; exit 1; fi

ATTEMPT_DIR=$(dirname "$ATTEMPT_VERILOG_FILE")
# Ensure SPICE_FILE is created within the ATTEMPT_DIR to keep attempt-specific files together
SPICE_FILE="${ATTEMPT_DIR}/${MODULE}_$(basename "$ATTEMPT_VERILOG_FILE" .v).sp"


# Get Env Vars set by outer evaluate.sh (the main one that calls run_single.sh or run.sh)
if [ -z "$METRIC_SCRIPT_DIR_ABS" ]; then echo "Error (evaluate.sh): Env var METRIC_SCRIPT_DIR_ABS not set."; exit 1; fi
if [ ! -d "$METRIC_SCRIPT_DIR_ABS" ]; then echo "Error (evaluate.sh): Metric dir '$METRIC_SCRIPT_DIR_ABS' not found."; exit 1; fi
if [ -z "$OUTPUT_BASE_DIR" ]; then echo "Error (evaluate.sh): Env var OUTPUT_BASE_DIR not set."; exit 1; fi

if [ -z "$MODULE" ] || [ -z "$MODEL_NAME" ]; then echo "Error (evaluate.sh): Could not determine MODULE/MODEL name from path structure."; exit 1; fi
echo "Evaluation (evaluate.sh): MODULE=$MODULE, MODEL=$MODEL_NAME, ScriptDir(ChallengeDir)=$SCRIPT_DIR"
echo "Evaluation (evaluate.sh): Processing attempt file: $ATTEMPT_VERILOG_FILE"
echo "Evaluation (evaluate.sh): Metric script directory: $METRIC_SCRIPT_DIR_ABS"
echo "Evaluation (evaluate.sh): Output base directory: $OUTPUT_BASE_DIR"
# --- End Dynamic Name & Input Handling ---

# --- Yosys Synthesis ---
YOSYS_SCRIPT_TEMPLATE="$SCRIPT_DIR/compile.ys" # Use compile.ys from script's own dir (challenge dir)
# TEMP_YOSYS_SCRIPT should also be in ATTEMPT_DIR to avoid clashes if evaluate.sh is run in parallel for different attempts
TEMP_YOSYS_SCRIPT="${ATTEMPT_DIR}/.compile_temp_${MODULE}_$(basename "$ATTEMPT_VERILOG_FILE" .v).ys"


if [ ! -f "$YOSYS_SCRIPT_TEMPLATE" ]; then echo "Error (evaluate.sh): Yosys template script '$YOSYS_SCRIPT_TEMPLATE' not found."; exit 1; fi

echo "Generating temporary Yosys script $TEMP_YOSYS_SCRIPT..."
# Convert to absolute paths for sed, as relative paths can be tricky depending on PWD
ATTEMPT_VERILOG_FILE_ABS=$(realpath "$ATTEMPT_VERILOG_FILE")
# Ensure SPICE_FILE_ABS directory exists before trying to use realpath on the non-existent file
mkdir -p "$(dirname "$SPICE_FILE")" || { echo "Error (evaluate.sh): Cannot create dir for SPICE file $(dirname "$SPICE_FILE")"; exit 1; }
SPICE_FILE_ABS=$(realpath "$SPICE_FILE") # Now SPICE_FILE_ABS can be determined as dir exists

# Debugging before sed for Yosys script
echo "DEBUG (evaluate.sh): Variables for Yosys script sed replacement:"
echo "DEBUG (evaluate.sh): MODULE='$MODULE'"
echo "DEBUG (evaluate.sh): ATTEMPT_VERILOG_FILE_ABS='$ATTEMPT_VERILOG_FILE_ABS'"
echo "DEBUG (evaluate.sh): SPICE_FILE_ABS='$SPICE_FILE_ABS'"
echo "DEBUG (evaluate.sh): YOSYS_SCRIPT_TEMPLATE path is '$YOSYS_SCRIPT_TEMPLATE'"


sed -e "s|##MODULE##|$MODULE|g" \
    -e "s|##VERILOG_FILE##|$ATTEMPT_VERILOG_FILE_ABS|g" \
    -e "s|##SPICE_FILE##|$SPICE_FILE_ABS|g" \
    "$YOSYS_SCRIPT_TEMPLATE" > "$TEMP_YOSYS_SCRIPT"
SED_YS_EXIT_CODE=$?

if [ $SED_YS_EXIT_CODE -ne 0 ]; then
    echo "FATAL ERROR (evaluate.sh): sed command for Yosys script failed with code $SED_YS_EXIT_CODE."
    # Consider exiting if sed fails as Yosys will likely fail too
    # exit 1 
fi

echo "--- Content of TEMP_YOSYS_SCRIPT ($TEMP_YOSYS_SCRIPT) AFTER sed ---"
if [ -f "$TEMP_YOSYS_SCRIPT" ]; then
    cat "$TEMP_YOSYS_SCRIPT"
else
    echo "ERROR (evaluate.sh): TEMP_YOSYS_SCRIPT file was not created: $TEMP_YOSYS_SCRIPT"
fi
echo "---------------------------------------------------------------------"


if [ ! -f "$TEMP_YOSYS_SCRIPT" ]; then echo "Error (evaluate.sh): Failed to create temp Yosys script '$TEMP_YOSYS_SCRIPT'."; exit 1; fi
# trap 'rm -f "$TEMP_YOSYS_SCRIPT" "$SPICE_FILE_ABS" ' EXIT # Use SPICE_FILE_ABS here
# It's better to clean up at the end or if specific conditions are met. Trap EXIT can sometimes hide errors.

echo "Running Yosys synthesis for $MODULE using $TEMP_YOSYS_SCRIPT..."
yosys -q -q -s "$TEMP_YOSYS_SCRIPT"
YOSYS_EXIT_CODE=$?

if [ $YOSYS_EXIT_CODE -ne 0 ]; then 
    echo "Error (evaluate.sh): Yosys failed (Code: $YOSYS_EXIT_CODE)."; 
    rm -f "$TEMP_YOSYS_SCRIPT" # Clean up temp script
    exit 1; 
fi
if [ ! -f "$SPICE_FILE_ABS" ]; then # Check for SPICE_FILE_ABS
    echo "Error (evaluate.sh): Yosys did not generate SPICE file '$SPICE_FILE_ABS'."; 
    rm -f "$TEMP_YOSYS_SCRIPT" # Clean up temp script
    exit 1; 
fi
echo "Yosys synthesis completed, generated $SPICE_FILE_ABS."
# --- End Yosys Synthesis ---

# --- Run Python Evaluation Scripts ---
echo "Running Python evaluation scripts using metrics from $METRIC_SCRIPT_DIR_ABS..."

DEVICE_JSON_PATH="$METRIC_SCRIPT_DIR_ABS/device_types_simple-$MODEL_NAME.json"
JSON_ARG=""
if [ -f "$DEVICE_JSON_PATH" ]; then
    JSON_ARG="--device_json $DEVICE_JSON_PATH"
    echo "Debug (evaluate.sh): Found device JSON: $DEVICE_JSON_PATH"
else
    echo "Warning (evaluate.sh): Device types JSON not found at '$DEVICE_JSON_PATH'. Gate counts might use defaults."
fi

PYTHON_SCRIPT1="$METRIC_SCRIPT_DIR_ABS/not-and2nand.py" 
if [ -f "$PYTHON_SCRIPT1" ]; then
    python3 "$PYTHON_SCRIPT1" --sp_file "$SPICE_FILE_ABS" 
    if [ $? -ne 0 ]; then echo "Warning (evaluate.sh): $PYTHON_SCRIPT1 failed."; fi
else
    echo "Info (evaluate.sh): Python script $PYTHON_SCRIPT1 not found. Skipping."
fi

PYTHON_SCRIPT2="$METRIC_SCRIPT_DIR_ABS/Gates-delay-calulate.py"
if [ -f "$PYTHON_SCRIPT2" ]; then
    python3 "$PYTHON_SCRIPT2" --sp_file "$SPICE_FILE_ABS" --device_type_file "$DEVICE_JSON_PATH" 
    PY2_EXIT_CODE=$?
    if [ $PY2_EXIT_CODE -ne 0 ]; then 
        echo "Error (evaluate.sh): $PYTHON_SCRIPT2 failed (Code: $PY2_EXIT_CODE)."; 
        rm -f "$TEMP_YOSYS_SCRIPT" "$SPICE_FILE_ABS" # Clean up
        exit 1; 
    fi
else
    echo "Error (evaluate.sh): Required Python script $PYTHON_SCRIPT2 not found in $METRIC_SCRIPT_DIR_ABS."
    rm -f "$TEMP_YOSYS_SCRIPT" "$SPICE_FILE_ABS" # Clean up
    exit 1
fi
# --- End Python Evaluation Scripts ---

# Clean up temporary Yosys script if everything was successful up to this point
rm -f "$TEMP_YOSYS_SCRIPT"
# SPICE_FILE_ABS is an output, typically not removed here unless it's intermediate to a final result not handled by this script.

echo "Performance evaluation completed for $ATTEMPT_VERILOG_FILE."
exit 0