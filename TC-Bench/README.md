# TC-Bench: Gate-Level Circuit Generation Benchmark

Welcome to TC-Bench! This is a gate-level circuit generation benchmark dataset designed based on the [TuringComplete game](https://turingcomplete.game/), aiming to evaluate and compare the performance of digital circuits designed by AI or humans. The core objective of TC-Bench is to measure design performance in terms of functional correctness and physical efficiency (gate count, delay), and to compare it against human expert levels.

## Dataset Structure

This benchmark dataset (`TC-Bench`) contains a series of circuit design challenges, categorized into three difficulty levels:

* **`Easy/`**: Contains basic combinational logic problems.
* **`Medium/`**: Includes more complex components such as adders, multiplexers, etc.
* **`Hard/`**: Features advanced designs like Arithmetic Logic Units (ALU), logic engines, etc.

Within each difficulty level directory, there are subfolders for the corresponding challenges, for example, `Easy/NAND/`. Each challenge subfolder typically includes:

* **`description.md` / `README.md`**: A text description and requirements for the challenge task.
* **`solution.circ` / `reference.circ` (or other formats)**: One or more efficient reference solutions (gate-level netlists) written by human experts.
* **`test.circ` / `testbench.v`**: Test code or a testbench used to verify the functional correctness of the circuit.

*Note: Specific filenames may vary depending on the challenge.*

## Evaluation Method

The evaluation of submitted circuit designs (typically a gate-level netlist file, such as `.circ` or Verilog files) primarily consists of two aspects: functional correctness and performance efficiency.

### 1. Functional Correctness Check

We use [Icarus Verilog (`iverilog`)](http://iverilog.icarus.com/) to compile and simulate the submitted design, and run the testbench (`testbench.v` or similar file) provided for each challenge to verify if its logical function meets the requirements.

* **Passing Criteria**: Only designs that fully pass all test cases are considered functionally correct and proceed to performance evaluation.

### 2. Performance Efficiency Evaluation

For functionally correct designs, we calculate the following metrics:

* **Gate Count**:
    * We count the total number of basic logic gates used in the design (AND, OR, NOT, XOR, NAND).
    * The counting rule follows the settings in the TuringComplete game, where each basic logic gate counts as 1 gate.
    * The counting logic is implemented by scripts located in the `evaluate/` directory.
* **Critical Path Delay**:
    * We calculate the longest path delay for a signal to propagate through the circuit. This typically depends on the depth of the circuit.
    * The calculation logic is implemented by custom scripts in the `evaluate/` directory.
* **Solution Efficiency Index (SEI)**:
    * This is a comprehensive metric that combines gate count and delay to assess overall efficiency. Please refer to our main paper (link in the main README) for the calculation formula. A higher SEI indicates better efficiency.
* **Comparison with Human Experts**:
    * The calculated SEI score can be compared against the performance tiers (Top/Mid/Low Tiers) collected from the TuringComplete community of human experts to gauge the relative skill level of the design.

## Evaluation Tools (`evaluate/` Directory)

The scripts used to perform the evaluation described above (gate count calculation, delay calculation, SEI calculation, etc.) are located in the `evaluate/` subfolder within this directory.

### How to Run Evaluation

*(Please add the specific commands and steps to run your evaluation scripts here)*

```bash
# Example:
# 1. Ensure iverilog and Python 3 are installed in your environment

# 2. Navigate to the evaluate directory
# cd evaluate

# 3. Run the functionality check (assuming a check_functionality.sh script)
# ./check_functionality.sh <path_to_submitted_design.v> <path_to_testbench.v>

# 4. If functionality is correct, run the performance evaluation (assuming an evaluate_performance.py script)
# python evaluate_performance.py <path_to_submitted_design.v>

# 5. View the output results (e.g., Gate Count, Delay, SEI)
# ...

# --- Please replace the example above with your actual execution commands ---