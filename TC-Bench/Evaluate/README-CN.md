
-----

# TC-Bench 模型评估流程

## 简介

本目录包含一系列脚本，用于自动化评估基于 TC-Bench 基准测试集的电路生成模型。评估流程主要包括：

1.  **环境初始化与脚本设置:** 使用 `setup_challenge_scripts.sh` 脚本，为每个挑战的各个尝试自动配置所需的验证和评估脚本及依赖文件（如测试平台）。
2.  **功能正确性验证:** 通过运行由 `setup_challenge_scripts.sh` 配置的 `validate.sh` 脚本（基于 `validate_template.sh`），使用 Icarus Verilog 运行 TC-Bench 提供的测试平台（testbench）来检查模型生成的电路设计的逻辑功能是否正确。
3.  **性能指标提取:** 通过运行由 `setup_challenge_scripts.sh` 配置的 `evaluate.sh` 内部脚本（基于 `evaluate_inner_template.sh`），使用 Yosys进行综合，并调用 Python 脚本从成功的综合和/或仿真中提取关键性能指标，如逻辑门数量（Gate Count）和关键路径延迟（Delay）。
4.  **多样性分析:** 衡量模型为每个挑战生成的不同（基于文件内容）解决方案的数量。
5.  **通过率计算:** 计算 Pass@k 指标（如 Pass@1, Pass@5），评估模型在有限尝试内生成正确方案的概率。
6.  **结果汇总与比较:** 生成汇总表格和对比图表，方便比较不同模型的性能。

## 前提条件 (Prerequisites)

在运行评估脚本之前，请确保满足以下条件：

**1. 软件依赖:**

  * Bash Shell 环境
  * Python 3.x (建议 3.7 或更高版本)
  * [Icarus Verilog (`iverilog`)](https://www.google.com/search?q=%5Bhttp://iverilog.icarus.com/%5D\(http://iverilog.icarus.com/\)): 用于 Verilog 代码的编译和仿真。请确保 `iverilog` 和 `vvp` 命令在您的系统路径中可用。
  * [Yosys Open SYnthesis Suite (`yosys`)](https://www.google.com/search?q=%5Bhttp://www.clifford.at/yosys/%5D\(http://www.clifford.at/yosys/\)): 用于 Verilog 代码的综合以提取门数等信息。请确保 `yosys` 命令在您的系统路径中可用。
  * [jq](https://stedolan.github.io/jq/): 一个命令行 JSON 处理工具（`run_single.sh` 脚本需要）。

**2. Python 库依赖:**

  * 运行以下命令安装所需的 Python 包：
    ```bash
    pip install -r requirements.txt
    ```

**3. TC-Bench 基准测试集:**

  * 您需要拥有完整的 TC-Bench 数据集。`setup_challenge_scripts.sh` 脚本可以配置为从 TC-Bench 源目录复制每个挑战对应的测试平台文件（通常是 `testbench.v`）和参考文件（`${MODULE}_ref.v`）到模型结果目录中相应的挑战文件夹。
  * 请在 `setup_challenge_scripts.sh` 中正确配置 `TC_BENCH_SRC_DIR` 变量。

**4. 模型输出数据结构:**

  * **重要:** 您的模型生成的 Verilog 电路设计文件**必须**按照以下目录结构进行组织，**然后运行 `setup_challenge_scripts.sh` 进行初始化**：

    ```
    <模型结果基础目录>/                # 例如: ../Exp-Results/MyCoolModel (对应 $MODEL_SRC_DIR)
    ├── <挑战名称_1>/                 # 例如: 1_not_gate
    │   ├── <尝试编号_1>/             # 例如: 1
    │   │   └── <模块名称>.v          # 模型生成的 Verilog 文件, 如 not_gate.v
    │   ├── <尝试编号_2>/             # 例如: 2
    │   │   └── <模块名称>.v
    │   └── ...                     # 例如: ... 直到 N (如 20)
    ├── <挑战名称_2>/                 # 例如: 3_xor_gate
    │   ├── <尝试编号_1>/             # 例如: 1
    │   │   └── <模块名称>.v          # 例如: xor_gate.v
    │   └── ...
    └── ...                         # 其他所有 TC-Bench 挑战
    ```

      * `<模型结果基础目录>`: 存放特定模型所有输出的根目录。
      * `<挑战名称>`: 必须与 TC-Bench 的挑战目录名称基本一致（如 `1_not_gate`, `23_logic_engine`）。脚本会从中提取模块名称。
      * `<尝试编号>`: **必须是纯数字**（如 `1`, `2`, ..., `20`），代表对该挑战的第 N 次生成/解决尝试。
      * `<模块名称>.v`: **关键变化点\!** 每个尝试文件夹内，模型生成的 Verilog 文件名**必须是该挑战对应的模块名** (例如，对于挑战 `3_xor_gate`，其尝试 `1` 下的 Verilog 文件应为 `xor_gate.v`)。这是因为 `run_inner_template.sh` 脚本会基于父目录名动态确定模块名和 Verilog 文件名。

    **初始化后，`setup_challenge_scripts.sh` 会在相应目录中添加必要的脚本，例如：**

    ```
    <模型结果基础目录>/
    ├── <挑战名称_1>/
    │   ├── evaluate.sh             # (从 evaluate_inner_template.sh 复制)
    │   ├── validate.sh             # (从 validate_template.sh 复制并配置)
    │   ├── compile.ys              # (从 compile_template.ys 复制)
    │   ├── testbench.v             # (从 TC_BENCH_SRC_DIR 复制, 可选)
    │   ├── <模块名称>_ref.v        # (从 TC_BENCH_SRC_DIR 复制, 可选)
    │   ├── <尝试编号_1>/
    │   │   ├── <模块名称>.v
    │   │   └── run.sh              # (从 run_inner_template.sh 复制)
    │   └── ...
    └── ...
    ```

## TC-Bench 评估工作流程详解

本文档解释了用于对照 TC-Bench 基准评估电路生成模型的脚本序列。工作流程涉及环境设置、仿真生成的电路、提取性能指标、分析结果和比较模型。

您可以单独运行每个脚本进行调试或理解，或使用主编排脚本 (`evaluate.sh` - 主评估脚本) 自动运行单个模型的整个评估过程（初始化步骤除外）。

-----

### 脚本描述

1.  **环境初始化脚本 (`setup_challenge_scripts.sh`)**

      * **位置:** 评估脚本的根目录。
      * **目的:** 此脚本是运行任何评估之前的**第一步**。它会遍历指定模型结果目录下的所有挑战，并为每个挑战及其所有尝试配置必要的运行环境。
      * **核心功能:**
          * 从 `./script_templates` 目录复制模板脚本到每个挑战和尝试目录中。
          * **挑战目录级别:**
              * 复制 `evaluate_inner_template.sh` 为 `evaluate.sh` (内部评估脚本)。
              * 复制 `validate_template.sh` 为 `validate.sh`，并用实际模块名替换占位符 `##MODULE##`。
              * 复制 `compile_template.ys` 为 `compile.ys`。
              * (可选) 如果配置了 `TC_BENCH_SRC_DIR`，则从 TC-Bench 源复制相应的 `testbench.v` 和 `<模块名称>_ref.v`。
          * **尝试目录级别:**
              * 复制 `run_inner_template.sh` 为 `run.sh`。
          * 为复制的脚本添加执行权限。
      * **输入:**
          * `<path_to_model_results_base_dir>`: 模型结果的基础目录路径 (命令行参数)。
          * `TEMPLATE_DIR` (脚本内变量): 指向 `./script_templates` 目录。
          * `TC_BENCH_SRC_DIR` (脚本内变量, 可选): TC-Bench 数据集源目录路径。
      * **输出:**
          * 在模型结果目录的每个挑战和尝试文件夹中创建和配置上述脚本和文件。
          * 在标准输出打印设置过程。

2.  **单次尝试运行脚本 (`run.sh` - 位于*每个尝试文件夹内部*)**

      * **来源:** 由 `setup_challenge_scripts.sh` 从 `run_inner_template.sh` 复制而来。
      * **目的:** 负责对*单个*生成的电路尝试执行功能验证和性能评估。
      * **核心功能:**
          * 按顺序调用位于其父目录 (即挑战目录) 中的 `validate.sh` 和 `evaluate.sh` (内部评估脚本)。
      * **输入:**
          * 无直接命令行参数，但依赖于其所在路径来定位 Verilog 文件 (假定为 `<模块名称>.v`) 和父目录中的脚本。
      * **输出:**
          * 打印执行进度到标准输出。
          * 依赖 `validate.sh` 和 `evaluate.sh` (内部) 的输出和退出码来决定流程是否继续。
          * 成功时退出码为 0，失败时为非零。

3.  **功能验证脚本 (`validate.sh` - 位于*每个挑战文件夹内部*)**

      * **来源:** 由 `setup_challenge_scripts.sh` 从 `validate_template.sh` 复制和配置而来。
      * **目的:** 编译并仿真模型生成的 Verilog 代码与参考设计 (如果存在) 及测试平台，以验证功能正确性。
      * **核心功能:**
          * 使用 `iverilog` 编译提供的尝试 Verilog 文件、参考 Verilog 文件 (`<模块名称>_ref.v`) 和测试平台 (`testbench.v`)。
          * 运行编译后的 `vvp` 文件，并将仿真输出保存到临时文本文件。
          * 检查仿真输出中是否包含成功消息 (例如 "All tests passed: Passed")。
      * **输入:**
          * `<path_to_attempt_verilog_file>`: 当前尝试的 Verilog 文件路径 (由其调用者 `run.sh` 提供)。
      * **输出:**
          * 打印 "All tests passed: Passed" 到标准输出（如果成功）。
          * 成功时退出码为 0，编译或仿真失败/不匹配时退出码为非零。

4.  **内部性能评估脚本 (`evaluate.sh` - 位于*每个挑战文件夹内部*)**

      * **来源:** 由 `setup_challenge_scripts.sh` 从 `evaluate_inner_template.sh` 复制而来。
      * **目的:** 对单个成功的 Verilog 设计进行综合，并运行 Python 脚本提取性能指标。
      * **核心功能:**
          * 使用 Yosys 和当前挑战目录下的 `compile.ys` 脚本来综合 Verilog 文件，生成 SPICE 网表。
          * 调用 Python 脚本 (如 `Gates-delay-calulate.py`) 处理 SPICE 网表以提取门数、延迟等指标。
      * **输入:**
          * `<path_to_attempt_verilog_file>`: 当前尝试的 Verilog 文件路径 (由其调用者 `run.sh` 提供)。
          * 环境变量 `METRIC_SCRIPT_DIR_ABS`: 指向 Python 度量脚本的目录。
          * 环境变量 `OUTPUT_BASE_DIR`: 用于定位设备类型 JSON 文件。
      * **输出:**
          * 将性能指标（例如 `Longest delay: ...`, `Total logic gates: ...`）打印到**标准输出**，格式需符合后续 `extract.py` 脚本的要求。
          * 成功时退出码为 0，Yosys 或 Python 脚本失败时退出码为非零。

5.  **Yosys 综合脚本 (`compile.ys` - 位于*每个挑战文件夹内部*)**

      * **来源:** 由 `setup_challenge_scripts.sh` 从 `compile_template.ys` 复制而来。
      * **目的:** Yosys 使用此脚本来综合 Verilog 设计。
      * **核心功能:** 读取 Verilog，执行标准综合流程，并写出 SPICE 网表。占位符 (`##VERILOG_FILE##`, `##MODULE##`, `##SPICE_FILE##`) 由调用它的 `evaluate.sh` (内部) 脚本通过 `sed` 动态替换。
      * **输入:** 通过 `sed` 注入的 Verilog 文件路径、模块名和输出 SPICE 文件路径。
      * **输出:** 生成的 SPICE 网表文件。

6.  **特定挑战优化脚本 (`run_single.sh` - 位于评估脚本根目录)**

      * **目的:** 针对*特定挑战*（例如 `3_xor_gate`）的所有尝试运行评估，并记录最佳结果（例如最小门数）。主要用于获取特定基础组件的优化参数。
      * **输入:**
          * `<challenge_folder_path>`: 特定挑战目录的路径。
          * `<script_name>`: 在每个尝试文件夹内运行的脚本名 (通常是 `"run.sh"`)。
          * `<input_json_file>`: 模板 JSON 文件路径。
          * `<output_json_file>`: 更新后的 JSON 文件保存路径。
          * `<temp_results_file>`: 临时存储门数的文件路径。
      * **输出:**
          * 创建/更新 `<output_json_file>`，包含找到的最小门数。
          * 打印进度到标准输出。

7.  **批量仿真/评估脚本 (`run.sh` - 位于评估脚本根目录，区别于尝试内部的 `run.sh`)**

      * **目的:** 自动为给定模型的**所有**挑战文件夹下的**所有**尝试执行位于尝试文件夹内的 `run.sh` 脚本。它编排了批量的验证和评估过程。
      * **输入:**
          * `<model_results_base_dir>`: 模型结果的基础目录路径。
          * `[optional_challenge_names...]`: (可选) 要处理的特定挑战文件夹名称列表。
      * **输出:**
          * 将每个挑战和尝试的详细执行进度打印到**标准输出**。这包括关键的 `--> Executing 'run.sh' in '...'` 行。
          * 此脚本的标准输出**旨在被捕获**到一个主日志文件中 (例如，使用 `tee`)。该日志文件成为提取脚本的主要输入。
          * 打印警告和错误到标准输出/错误。

8.  **Verilog 多样性测试脚本 (`Verilog_Diversity_Test.py`)**

      * **目的:** 通过计算每个挑战下内容唯一的 Verilog 文件数量来衡量模型生成解决方案的多样性。
      * **输入:**
          * `--input-dir`: 模型结果的基础目录路径。
      * **输出:**
          * 将一个格式化的表格 (`PrettyTable`) 打印到**标准输出**，显示每个挑战的多样性计数。此输出通常由 `tee` 捕获到多样性日志文件中。

9.  **结果提取脚本 (`extract.py` 或 `extract-v2.py`)**

      * **目的:** 解析由*批量仿真/评估脚本*（步骤 7）生成的主日志文件，提取每个成功尝试的性能指标，识别失败的尝试，并保存结构化数据。
      * **输入:**
          * `--log-file`: 从批量仿真/评估脚本的标准输出捕获的主日志文件路径。
          * `--output-csv`: 提取的原始结果将以 CSV 格式保存的路径 (`*-raw.csv`)。
      * **输出:**
          * 创建 `*-raw.csv` 文件，包含每次尝试提取的指标，带有挑战分隔符，失败的运行则指标为空。
          * 打印进度、状态和检测到的失败仿真列表到标准输出。

10. **结果分析脚本 (`analysis_gate.py` 或 `analysis_gate-v2.py`)**

      * **目的:** 分析原始结果 CSV，计算组合指标（例如门数 + 延迟的某种组合，当前脚本似乎主要关注门数），过滤无效/零结果，根据最小组合指标（或门数）找到每个挑战的最佳尝试，并保存这些最佳结果。
      * **输入:**
          * `--input-csv`: 由 `extract.py` 生成的原始结果 CSV 文件路径 (`*-raw.csv`)。
          * `--output-csv`: 过滤后的“最佳结果”将以 CSV 格式保存的路径 (`*-less.csv`)。
      * **输出:**
          * 创建 `*-less.csv` 文件，仅包含每个挑战的最佳结果行。
          * 打印状态消息到标准输出。

11. **通过率计算脚本 (`pass_ratio.py` 或 `pass_ratio-v2.py`)**

      * **目的:** 基于原始结果 CSV 中记录的成功尝试次数，计算每个挑战的 pass@k 成功率（例如 pass@1, pass@5），假设每个挑战的总尝试次数固定。
      * **输入:**
          * `--input-csv`: 原始结果 CSV 文件路径 (`*-raw.csv`)。
          * `--output-results-csv`: 保存计算的通过率结果的 CSV 文件路径。
          * `--output-plot-pass1`: 保存 pass@1 条形图 PNG 的路径。
          * `--output-plot-pass5`: 保存 pass@5 条形图 PNG 的路径。
          * `--total-trials`: 每个挑战假定的总尝试次数（整数，默认：20）。
      * **输出:**
          * 创建通过率结果 CSV 文件。
          * 创建 pass@1 和 pass@5 PNG 绘图文件。
          * 将通过率的摘要表 (`PrettyTable`) 打印到标准输出（通常由 `tee` 捕获）。

12. **多模型结果合并脚本 (`merge_gates.py` 或 `merge_gates-v2.py`)**

      * **目的:** 将来自**多个模型**的最佳门数结果（来自 `*-less.csv` 文件的 `Total logic gates`）合并到一个摘要表中，以便于比较。
      * **输入:**
          * `--input-dir`: 包含**所有**待比较模型的结果文件夹的目录路径（例如 `./Results/Pass-Results/ModelTest/`）。脚本会在此目录中递归搜索 `*-less.csv` 文件。
          * `--output-csv`: 合并的比较表将以 CSV 格式保存的路径。
      * **输出:**
          * 创建合并的 CSV 文件（例如 `GATES-merged-*.csv`）。
          * 打印状态消息到标准输出。

13. **多模型结果比较绘图脚本 (`model_res_compare_gates.py` 或 `model_res_compare_gates-v2.py`)**

      * **目的:** 生成一个散点图，比较**多个模型**在所有挑战中实现的最佳门数（来自 `*-less.csv` 文件）。
      * **输入:**
          * `--input-dir`: 包含**所有**待比较模型的结果文件夹的目录路径。
          * `--output-png`: 比较图 PNG 文件将保存的路径。
      * **输出:**
          * 创建比较图 PNG 文件（例如 `GATES-compared-*.png`）。
          * 打印状态消息到标准输出。

-----

### 主评估编排脚本 (`evaluate.sh` - 位于评估脚本根目录)

  * **目的:** 此主脚本自动化**单个模型**的整个评估工作流程（**不包括初始的环境设置步骤**）。它设置必要的目录并按正确顺序调用上述各个分析脚本（从 `run_single.sh` 开始，然后是批处理 `run.sh`，接着是 Python 分析脚本），在它们之间传递适当的输入和输出。它处理特定模型运行的配置。
  * **输入:**
      * `<ModelName>`: 模型名称，作为第一个命令行参数提供。
      * 脚本内部设置的配置变量（例如 `MODEL_SRC_BASE_DIR`, `OUTPUT_BASE_DIR`, `METRIC_SCRIPT_DIR_ABS`, `TOTAL_TRIALS` 等）。
  * **输出:**
      * 在指定的 `OUTPUT_BASE_DIR` 内编排创建脚本 6-13 所述的所有输出文件和目录。
      * 将总体进度消息打印到标准输出。

-----

## 运行流程

执行此评估主要有以下步骤：

1.  **环境初始化 (必需的第一步):**

      * 确保您的模型输出的 Verilog 文件已按照“模型输出数据结构”部分所述的结构和命名约定准备好。
      * 打开 `setup_challenge_scripts.sh` 脚本，根据需要配置 `TEMPLATE_DIR` (通常默认为 `./script_templates`) 和 `TC_BENCH_SRC_DIR` (如果需要复制测试平台和参考文件)。
      * 从评估脚本的根目录运行初始化脚本，并提供模型结果的基础目录作为参数：
        ```bash
        bash setup_challenge_scripts.sh <path_to_model_results_base_dir>
        # 例如: bash setup_challenge_scripts.sh ../Exp-Results/MyCoolModel
        ```
      * 此步骤将为每个挑战和尝试填充所需的 `run.sh`, `validate.sh`, `evaluate.sh` (内部), `compile.ys` 等脚本。

2.  **自动化评估 (使用主 `evaluate.sh`):** 这是标准评估运行的推荐方法。

      * 在运行此脚本前，**必须先完成上述的环境初始化步骤**。
      * 根据您的环境，配置主 `evaluate.sh` 脚本顶部的变量（特别是 `MODEL_SRC_BASE_DIR`, `OUTPUT_BASE_DIR`, `METRIC_SCRIPT_DIR_ABS`）。
      * 确保所有单个脚本（如 Python 脚本 `extract.py` 等，以及批处理 `run.sh`）都存在于主 `evaluate.sh` 预期的位置（通常是同一目录或 `utils` 子目录）并且是可执行的。
      * 运行主评估脚本，并提供模型名称作为参数：
        ```bash
        bash evaluate.sh YourModelName
        ```
      * 这将自动为配置的模型执行从 `run_single.sh` (针对XOR门) 开始，到后续的批量处理、数据提取、分析和通过率计算等步骤。

3.  **手动执行 (用于调试):**

      * 在完成步骤1的环境初始化后，您可以从命令行单独运行各个脚本（例如，首先运行批处理 `run.sh`，然后是 `extract.py`，依此类推），并提供所需的参数。
      * 这对于调试流程的特定部分或只需要部分分析时非常有用。
      * 请确保一个步骤的输出可作为下一个步骤的输入。特别注意，需要将批量仿真/评估脚本 (`run.sh`) 的标准输出捕获到日志文件中，以供 `extract.py` 使用。
        ```bash
        # 示例：手动运行批量评估并捕获日志
        bash run.sh ../Exp-Results/MyCoolModel > MyCoolModel-run.log
        # 然后运行提取
        python3 extract.py --log-file MyCoolModel-run.log --output-csv MyCoolModel-raw.csv
        # ...等等
        ```

**跨模型比较:**

用于合并结果的脚本 (`merge_gates.py`) 和生成比较图的脚本 (`model_res_compare_gates.py`) 设计用于处理*多个*模型。它们通常在您为要比较的**每个模型**都运行了完整的评估流程（即上述步骤1和步骤2）**之后单独运行**。确保这些脚本的 `--input-dir` 参数指向包含所有单个模型结果文件夹的父目录（例如 `./Results/Pass-Results/ModelTest/`）。

-----