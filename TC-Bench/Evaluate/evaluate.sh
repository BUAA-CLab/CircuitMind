#!/bin/bash

# --- Get the script's own directory ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PARENT_DIR="${SCRIPT_DIR%/*}"

# --- Configuration ---
# Get the model name from the command line argument
if [ -z "$1" ]; then
    echo "Usage: $0 <ModelName>"
    echo "Error: Model name must be provided as the first argument."
    exit 1
fi
MODEL_NAME="$1"

# !! Modify this to be the parent directory where your model results are stored !!
MODEL_SRC_BASE_DIR="${PARENT_DIR}/Exp-Results"
# !! Modify this to be your desired output directory (use absolute path) !!
OUTPUT_BASE_DIR="${SCRIPT_DIR}/Results/Pass-Results"
# !! Modify this to be the actual absolute path to your metric python scripts !!
METRIC_SCRIPT_DIR_ABS="${SCRIPT_DIR}/utils"

# Export environment variables for child scripts
export METRIC_SCRIPT_DIR_ABS
export OUTPUT_BASE_DIR # Needed by evaluate.sh internally to locate device_types JSON

# --- Derived Dirs / Files / Configs ---
MODEL_SRC_DIR="$MODEL_SRC_BASE_DIR/$MODEL_NAME"
MODEL_OUTPUT_DIR="$OUTPUT_BASE_DIR/ModelTest/$MODEL_NAME"
MERGE_DIR="$OUTPUT_BASE_DIR/MergeData"
PASS_RATIO_DIR="$OUTPUT_BASE_DIR/PassRatio"
PLOT_DIR="$OUTPUT_BASE_DIR/Plots"

BASE_JSON="${SCRIPT_DIR}/utils/device_types_simple-base.json"
# !! Modify this to be the path to your base gate cost JSON template/base file !!
XOR_INPUT_JSON="${SCRIPT_DIR}/utils/device_types_simple-base-$MODEL_NAME.json"
cp "$BASE_JSON" "$XOR_INPUT_JSON" # Copy the base JSON file to the model output directory
# Construct output filename using absolute path
XOR_OUTPUT_JSON="$MODEL_OUTPUT_DIR/device_types_simple-$MODEL_NAME.json"
TEMP_XOR_RESULTS="$MODEL_OUTPUT_DIR/.xor_gate_temp_results.txt"
MAIN_LOG_FILE="$MODEL_OUTPUT_DIR/$MODEL_NAME-run.log"
DIVERSITY_LOG_FILE="$MODEL_OUTPUT_DIR/$MODEL_NAME-diversity.log"
RAW_CSV_FILE="$MODEL_OUTPUT_DIR/$MODEL_NAME-raw.csv"
LESS_CSV_FILE="$MODEL_OUTPUT_DIR/$MODEL_NAME-less.csv"
PASS_RATIO_CSV="$PASS_RATIO_DIR/${MODEL_NAME}_Pass_Results.csv"
PASS_RATIO_PLOT_P1="$PASS_RATIO_DIR/${MODEL_NAME}_pass1.png"
PASS_RATIO_PLOT_P5="$PASS_RATIO_DIR/${MODEL_NAME}_pass5.png"
PASS_RATIO_LOG="$PASS_RATIO_DIR/${MODEL_NAME}_PassRatio_calc.log"
MERGED_CSV_FILE="$MERGE_DIR/GATES-merged-$(date +%Y-%m-%d).csv"
COMPARE_PLOT_PNG="$PLOT_DIR/GATES-compared-$(date +%Y-%m-%d).png"

# Script names (assuming they are in the same directory as evaluate.sh)
SETUP_SCRIPT="setup_challenge_scripts.sh"
RUN_SINGLE_SCRIPT="run_single.sh"
# !! Confirm the filename of your batch run script !!
BATCH_RUN_SCRIPT="run.sh" # Or run-v2.sh
# Script name inside the attempt directory (called by run_single and batch run)
INNER_RUN_SCRIPT="run.sh"

# Pass Ratio Config
TOTAL_TRIALS=20
# Process all challenges (leave list empty for batch script to find automatically)
RUN_CHALLENGES=() # Empty array means process all found challenges

# --- Helper Function ---
execute_command() {
    echo "--------------------------------------------------"
    echo "Executing: $@"
    echo "--------------------------------------------------"
    "$@" # Execute the command
    local status=$?
    if [ $status -ne 0 ]; then
        echo "--------------------------------------------------"
        echo -e "\033[1;31mERROR:\033[0m Command failed with status $status: $@"
        echo "--------------------------------------------------"
        # exit $status # Uncomment to exit on error
    fi
    echo "--------------------------------------------------"
    echo # Blank line for separation
    return $status
}

# --- Pre-Checks ---
if [ ! -d "$MODEL_SRC_DIR" ]; then
    echo "Error: Model source directory not found: $MODEL_SRC_DIR"
    exit 1
fi
if [ -z "$METRIC_SCRIPT_DIR_ABS" ] || [ ! -d "$METRIC_SCRIPT_DIR_ABS" ]; then
    echo "Error: METRIC_SCRIPT_DIR_ABS path is invalid: $METRIC_SCRIPT_DIR_ABS"
    exit 1
fi
echo "Using Metric Scripts from: $METRIC_SCRIPT_DIR_ABS"
echo "Output will be saved under: $OUTPUT_BASE_DIR"

# --- Main Execution Flow ---
echo "Starting evaluation for model: $MODEL_NAME"

# 1. Create necessary output directories
echo "Creating output directories..."
mkdir -p "$MODEL_OUTPUT_DIR"
mkdir -p "$MERGE_DIR"
mkdir -p "$PASS_RATIO_DIR"
mkdir -p "$PLOT_DIR"
if [ $? -ne 0 ]; then echo "Error creating output directories."; exit 1; fi
echo "Output directories ready."

# (Assuming setup_challenge_scripts.sh has been run beforehand)

# 2. Run simulation for the specific XOR gate case (if needed/present)
XOR_CHALLENGE_DIR="$MODEL_SRC_DIR/3_xor_gate"
echo -e "\nRunning single evaluation for XOR gate (if exists)..."
if [ ! -d "$XOR_CHALLENGE_DIR" ]; then
     echo "Warning: XOR gate directory not found: $XOR_CHALLENGE_DIR. Skipping run_single."
elif [ ! -f "$XOR_INPUT_JSON" ]; then
     echo "Warning: XOR Input JSON not found at $XOR_INPUT_JSON. Skipping run_single."
else
    execute_command "$SCRIPT_DIR/$RUN_SINGLE_SCRIPT" \
        "$XOR_CHALLENGE_DIR" \
        "$INNER_RUN_SCRIPT" \
        "$XOR_INPUT_JSON" \
        "$XOR_OUTPUT_JSON" \
        "$TEMP_XOR_RESULTS"
fi

# 3. Run batch simulations for other challenges
echo -e "\nRunning batch simulations for challenges..."
# Call the batch script located in $SCRIPT_DIR
execute_command "$SCRIPT_DIR/$BATCH_RUN_SCRIPT" \
    "$MODEL_SRC_DIR" \
    "${RUN_CHALLENGES[@]}" \
    | tee "$MAIN_LOG_FILE"

# --- Subsequent Steps (4-9) ---
echo -e "\nAnalyzing Verilog code diversity..."
execute_command python3 "$SCRIPT_DIR/Verilog_Diversity_Test.py" --input-dir "$MODEL_SRC_DIR" | tee "$DIVERSITY_LOG_FILE"

echo -e "\nExtracting results from log file..."
execute_command python3 "$SCRIPT_DIR/extract.py" --log-file "$MAIN_LOG_FILE" --output-csv "$RAW_CSV_FILE"

echo -e "\nAnalyzing raw results to find best per challenge..."
execute_command python3 "$SCRIPT_DIR/analysis_gate.py" --input-csv "$RAW_CSV_FILE" --output-csv "$LESS_CSV_FILE"

echo -e "\nCalculating pass ratios..."
execute_command python3 "$SCRIPT_DIR/pass_ratio.py" \
    --input-csv "$RAW_CSV_FILE" \
    --output-results-csv "$PASS_RATIO_CSV" \
    --output-plot-pass1 "$PASS_RATIO_PLOT_P1" \
    --output-plot-pass5 "$PASS_RATIO_PLOT_P5" \
    --total-trials "$TOTAL_TRIALS" \
    | tee "$PASS_RATIO_LOG"

# --- Comparison/Merging (Note: These are typically run separately after evaluating all models) ---
echo -e "\nMerging results from all models (if other models exist)..."
INPUT_DIR_FOR_MERGE="$OUTPUT_BASE_DIR/ModelTest"
# It might be more user-friendly to check if $INPUT_DIR_FOR_MERGE contains more than one *-less.csv file before executing
execute_command python3 "$SCRIPT_DIR/merge_gates.py" --input-dir "$INPUT_DIR_FOR_MERGE" --output-csv "$MERGED_CSV_FILE"

echo -e "\nGenerating comparison plot (if other models exist)..."
INPUT_DIR_FOR_PLOT="$OUTPUT_BASE_DIR/ModelTest"
execute_command python3 "$SCRIPT_DIR/model_res_compare_gates.py" --input-dir "$INPUT_DIR_FOR_PLOT" --output-png "$COMPARE_PLOT_PNG"

echo -e "\nEvaluation script finished for model: $MODEL_NAME"
