#!/bin/bash

# --- Configuration ---
# !!! 修改为你存放模板脚本的目录路径 !!!
TEMPLATE_DIR="./script_templates"
# !!! 修改为你的 TC-Bench 数据集源目录路径 (如果需要复制 testbench/ref) !!!
TC_BENCH_SRC_DIR="/home/haiyan/Research/CircuitMind-v2-Re/TC/Datasets-TC" # 例如 /home/user/TC-Bench
# 定义内部 run.sh 模板的文件名
INNER_RUN_TEMPLATE="run_inner_template.sh"
EVALUATE_INNER_TEMPLATE="evaluate_inner_template.sh"
VALIDATE_TEMPLATE="validate_template.sh"
COMPILE_TEMPLATE="compile_template.ys"

# --- Input Argument ---
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_model_results_base_dir>"
    echo "  Example: $0 ../cleaned-exp/MyCoolModel"
    exit 1
fi
MODEL_RESULTS_DIR="$1"

if [ ! -d "$MODEL_RESULTS_DIR" ]; then
    echo "Error: Model results directory not found: $MODEL_RESULTS_DIR"
    exit 1
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template script directory not found: $TEMPLATE_DIR"
    exit 1
fi
if [ ! -f "$TEMPLATE_DIR/$INNER_RUN_TEMPLATE" ]; then
    echo "Error: Inner run.sh template ('$INNER_RUN_TEMPLATE') not found in $TEMPLATE_DIR"
    exit 1
fi
if [ ! -f "$TEMPLATE_DIR/$EVALUATE_INNER_TEMPLATE" ]; then
    echo "Error: Inner evaluate.sh template ('$EVALUATE_INNER_TEMPLATE') not found in $TEMPLATE_DIR"
    exit 1
fi
if [ ! -f "$TEMPLATE_DIR/$VALIDATE_TEMPLATE" ]; then
    echo "Error: Validate template ('$VALIDATE_TEMPLATE') not found in $TEMPLATE_DIR"
    exit 1
fi
if [ ! -f "$TEMPLATE_DIR/$COMPILE_TEMPLATE" ]; then
    echo "Error: Compile template ('$COMPILE_TEMPLATE') not found in $TEMPLATE_DIR"
    exit 1
fi

# 检查 TC_BENCH_SRC_DIR 是否已配置（如果需要复制）
COPY_TC_FILES=false
if [ ! -z "$TC_BENCH_SRC_DIR" ]; then
    if [ -d "$TC_BENCH_SRC_DIR" ]; then
        COPY_TC_FILES=true
        echo "TC-Bench source directory found: $TC_BENCH_SRC_DIR. Will copy testbench/reference files."
    else
        echo "Warning: TC_BENCH_SRC_DIR is set but directory not found: $TC_BENCH_SRC_DIR. Cannot copy testbench/reference files."
    fi
else
    echo "Info: TC_BENCH_SRC_DIR is not set. Will not copy testbench/reference files."
fi


echo "Setting up scripts for challenges in: $MODEL_RESULTS_DIR"
echo "Using templates from: $TEMPLATE_DIR"

# --- Iterate through Challenge Directories ---
find "$MODEL_RESULTS_DIR" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r challenge_path; do
    challenge_name=$(basename "$challenge_path")
    echo "" # Blank line for readability
    echo "Processing challenge: $challenge_name ($challenge_path)"

    module_name=${challenge_name#*_}
    if [ -z "$module_name" ] || [ "$module_name" == "$challenge_name" ]; then
        echo "  Warning: Could not extract module name from $challenge_name. Skipping script setup for this challenge."
        continue
    fi
    echo "  Module Name: $module_name"

    # --- Setup files in Challenge Directory ---
    echo "  Setting up challenge level scripts..."
    
    # Setup evaluate.sh
    cp "$TEMPLATE_DIR/$EVALUATE_INNER_TEMPLATE" "$challenge_path/evaluate.sh" && chmod +x "$challenge_path/evaluate.sh" || { echo "  Error: Failed to copy/chmod evaluate.sh for $challenge_name"; continue; }
    
    # Setup validate.sh with enhanced debugging
    echo "  Debug (setup_script): Preparing to generate $challenge_path/validate.sh for module '$module_name'"
    sed "s|##MODULE##|$module_name|g" "$TEMPLATE_DIR/$VALIDATE_TEMPLATE" > "$challenge_path/validate.sh"
    SED_EXIT_CODE=$? 

    if [ $SED_EXIT_CODE -ne 0 ]; then
        echo "    FATAL ERROR (setup_script): sed command failed for $challenge_path/validate.sh with exit code $SED_EXIT_CODE."
        echo "    Skipping further setup for $challenge_name."
        continue 
    fi

    # 更精确地检查 validate.sh 的内容中是否还存在未替换的占位符行
    if grep -Fq 'MODULE="##MODULE##"' "$challenge_path/validate.sh"; then 
        echo "    FATAL ERROR (setup_script): Line 'MODULE=\"##MODULE##\"' still exists in $challenge_path/validate.sh"
        echo "    --- Content of faulty $challenge_path/validate.sh ---"
        cat "$challenge_path/validate.sh"
        echo "    ----------------------------------------------------"
        echo "    Skipping further setup for $challenge_name."
        continue
    else
        echo "    DEBUG (setup_script): grep check for 'MODULE=\"##MODULE##\"' passed for $challenge_path/validate.sh."
    fi
    chmod +x "$challenge_path/validate.sh" || { echo "  Error: Failed to chmod validate.sh for $challenge_name"; continue; }

    # Setup compile.ys (direct copy, no sed replacement here)
    cp "$TEMPLATE_DIR/$COMPILE_TEMPLATE" "$challenge_path/compile.ys" || { echo "  Error: Failed to copy compile.ys for $challenge_name"; continue; }

    # --- Optional: Copy testbench and reference files ---
    if $COPY_TC_FILES; then
        TC_CHALLENGE_SRC_DIR="$TC_BENCH_SRC_DIR/$challenge_name"
        if [ -d "$TC_CHALLENGE_SRC_DIR" ]; then
            TB_SRC="$TC_CHALLENGE_SRC_DIR/testbench.v"
            REF_SRC="$TC_CHALLENGE_SRC_DIR/${module_name}_ref.v" # Assuming ref file is named module_name_ref.v
            TB_DEST="$challenge_path/testbench.v"
            REF_DEST="$challenge_path/${module_name}_ref.v"

            if [ -f "$TB_SRC" ]; then 
                cp "$TB_SRC" "$TB_DEST" || echo "  Warning: Failed to copy $TB_SRC"
            else 
                echo "  Warning: Testbench source not found: $TB_SRC"
            fi
            if [ -f "$REF_SRC" ]; then 
                cp "$REF_SRC" "$REF_DEST" || echo "  Warning: Failed to copy $REF_SRC"
            else 
                echo "  Warning: Reference Verilog source not found: $REF_SRC (tried ${module_name}_ref.v)"
            fi
        else
            echo "  Warning: TC-Bench source directory for $challenge_name not found: $TC_CHALLENGE_SRC_DIR"
        fi
    fi

    # --- Setup inner run.sh in Attempt Directories ---
    echo "  Setting up inner run.sh for attempts..."
    
    # Corrected way to count and iterate attempts to avoid subshell issues with ATTEMPT_COUNT
    attempt_dirs=$(find "$challenge_path" -mindepth 1 -maxdepth 1 -type d)
    attempt_count_actual=0
    if [ -n "$attempt_dirs" ]; then
        for attempt_path in $attempt_dirs; do
            attempt_num=$(basename "$attempt_path")
            echo "    Setting up attempt: $attempt_num in $attempt_path"
            cp "$TEMPLATE_DIR/$INNER_RUN_TEMPLATE" "$attempt_path/run.sh" && chmod +x "$attempt_path/run.sh" || echo "    Error: Failed to copy/chmod inner run.sh for attempt $attempt_num"
            attempt_count_actual=$((attempt_count_actual + 1))
        done
    fi
    echo "  Finished setting up $attempt_count_actual attempts for $challenge_name."

    echo "  Successfully finished setup for challenge $challenge_name."
done

echo ""
echo "Script setup process finished for $MODEL_RESULTS_DIR."