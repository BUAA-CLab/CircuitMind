# TC-Bench: 门级电路生成基准测试集

欢迎使用 TC-Bench！这是一个基于 [TuringComplete 游戏](https://turingcomplete.game/) 设计的门级电路生成基准测试集，旨在评估和比较 AI 或人类设计的数字电路的性能。TC-Bench 的核心目标是衡量设计在功能正确性和物理效率（门数、延迟）方面的表现，并将其与人类专家的水平进行比较。

## 数据集结构

本测试集 (`TC-Bench`) 包含一系列电路设计挑战，按难度分为三个级别：

* **`Easy/`**: 包含基础的组合逻辑问题。
* **`Medium/`**: 包含更复杂的组件，如加法器、多路选择器等。
* **`Hard/`**: 包含高级设计，如算术逻辑单元 (ALU)、逻辑引擎等。

在每个难度级别的目录下，包含了对应挑战的子文件夹，例如 `Easy/NAND/`。每个挑战子文件夹内通常包含：

* **`description.md` / `README.md`**: 对挑战任务的文字描述和要求。
* **`solution.circ` / `reference.circ` (或其他格式)**: 一个或多个人类专家编写的高效参考解决方案（门级网表）。
* **`test.circ` / `testbench.v`**: 用于验证电路功能正确性的测试代码或测试平台 (testbench)。

*请注意：具体文件名可能因挑战而异。*

## 评估方法

对提交的电路设计（通常是一个门级网表文件，例如 `.circ` 或 Verilog 文件）的评估主要包括两个方面：功能正确性和性能效率。

### 1. 功能正确性检查

我们使用 [Icarus Verilog (`iverilog`)](http://iverilog.icarus.com/) 来编译和仿真提交的设计，并运行每个挑战提供的测试平台 (`testbench.v` 或类似文件) 来验证其逻辑功能是否符合要求。

* **通过标准**: 只有完全通过所有测试用例的设计才被认为是功能正确的，才能进行后续的性能评估。

### 2. 性能效率评估

对于功能正确的设计，我们会计算以下指标：

* **逻辑门数量 (Gate Count)**:
    * 我们计算设计中使用的基本逻辑门（AND, OR, NOT, XOR, NAND）的总数。
    * 这里的计数规则遵循 TuringComplete 游戏中的设定，即每个基本逻辑门计为 1 个门。
    * 计算逻辑由 `evaluate/` 目录下的脚本实现。
* **关键路径延迟 (Delay)**:
    * 我们计算信号通过电路所需的最长路径延迟。这通常取决于电路的深度。
    * 计算逻辑由 `evaluate/` 目录下的自定义脚本实现。
* **解决方案效率指数 (Solution Efficiency Index - SEI)**:
    * 这是一个综合指标，结合了门数量和延迟来评估整体效率。计算公式请参考我们的主要论文 (链接在主 README)。SEI 越高表示效率越好。
* **与人类专家比较**:
    * 计算出的 SEI 分数可以与从 TuringComplete 社区收集到的人类专家性能等级（Top/Mid/Low Tiers）进行比较，以衡量设计的相对水平。

## 评估工具 (`evaluate/` 目录)

用于执行上述评估（门数计算、延迟计算、SEI 计算等）的脚本位于本目录下的 `evaluate/` 子文件夹中。

### 如何运行评估

*(请在此处添加具体的命令和步骤来运行你的评估脚本)*

```bash
# 示例:
# 1. 确保你的环境中已安装 iverilog 和 Python 3

# 2. 进入 evaluate 目录
# cd evaluate

# 3. 运行功能性检查 (假设有一个 check_functionality.sh 脚本)
# ./check_functionality.sh <path_to_submitted_design.v> <path_to_testbench.v>

# 4. 如果功能正确，运行性能评估 (假设有一个 evaluate_performance.py 脚本)
# python evaluate_performance.py <path_to_submitted_design.v>

# 5. 查看输出结果 (例如: Gate Count, Delay, SEI)
# ...

# --- 请将以上示例替换为你的实际执行命令 ---
```

请参考 `evaluate/` 目录下的具体脚本和可能的内部 README 文件获取更详细的使用说明和依赖项信息。

