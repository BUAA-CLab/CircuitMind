# CircuitMind 多智能体框架

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**CircuitMind 多智能体框架** 是一个基于大语言模型(LLM)的自动化 Verilog 代码生成和验证系统。通过多智能体协作架构，系统能够自动完成从设计需求理解、代码生成、代码审查到编译仿真验证的完整硬件设计流程。

## 🎯 核心功能

### 自动化硬件设计流程
- **智能需求分析**: 理解自然语言描述的硬件设计需求
- **结构化代码生成**: 生成符合工业标准的结构化 Verilog 代码
- **智能代码审查**: 自动检测语法错误、逻辑问题和设计规范违反
- **自动编译验证**: 使用 Icarus Verilog 进行编译和仿真测试
- **错误反馈与修复**: 基于编译/仿真错误自动修复代码

### 多智能体协作架构
- **CoderAgent**: 负责 Verilog 代码生成和需求分析
- **Reviewer**: 执行代码审查和自动错误修复
- **Executor**: 处理代码编译和仿真执行
- **Summarizer**: 生成实验报告和知识库更新
- **UserProxy**: 管理用户交互和任务分发

### 高级特性
- **RAG 增强**: 基于历史经验和最佳实践的检索增强生成
- **多模型支持**: 兼容 OpenAI、DeepSeek、Qwen、Ollama 等多种 LLM
- **智能重试策略**: 基于错误类型的差异化重试机制
- **并发执行**: 支持多实验并行处理，提升效率
- **实时监控**: 完整的指标收集和性能监控系统

## 🚀 快速开始

### 系统要求
- **Python**: 3.8 或更高版本
- **操作系统**: Linux/macOS/Windows
- **Verilog 工具**: Icarus Verilog (`iverilog`)

### 安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd CircuitMind/Multi-Agents

# 2. 创建虚拟环境 (推荐)
conda create -n circuitmind python=3.11
conda activate circuitmind
# 或 python -m venv venv && source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Verilog 工具
# Ubuntu/Debian:
sudo apt-get install iverilog

# macOS:
brew install icarus-verilog
```

### 基本配置

1. **配置 LLM 模型** (选择其中一种):
```bash
# 使用 OpenAI API
cp configs/models/gpt-4o.yaml configs/models/my_model.yaml
# 编辑 configs/models/my_model.yaml，填入你的 API 密钥

# 或使用本地 Ollama
# 确保 Ollama 服务运行在 http://localhost:11434
```

2. **更新基础配置**:
```yaml
# configs/base.yaml
current_model: my_model  # 使用你配置的模型名称
```

### 第一次运行

```bash
# 运行单个简单实验
python main.py -t "./TC/Datasets-TC/1_not_gate"

# 或运行所有配置的实验
python main.py
```

## 📁 项目结构

```
Multi-Agents/
├── 📂 agents/                    # 智能体实现
│   ├── 🤖 coder_agent.py        # 代码生成智能体
│   ├── 🔍 reviewer.py           # 代码审查智能体
│   ├── ⚙️ executor.py           # 代码执行智能体
│   ├── 📊 summarizer.py         # 结果汇总智能体
│   ├── 👤 user_proxy.py         # 用户代理
│   ├── 📄 dff.v                 # D触发器模块模板
│   └── 📂 prompts/              # LLM 提示模板
├── 📂 configs/                   # 配置管理
│   ├── 📄 base.yaml             # 基础配置
│   ├── 📂 models/               # 模型配置
│   ├── 📂 environments/         # 环境配置
│   └── 📂 experiments/          # 实验配置
├── 📂 src/                      # 核心框架
│   ├── 📂 config/               # 配置系统
│   └── 📂 core/                 # 核心组件
├── 📂 utils/                    # 工具模块
│   ├── 🔄 llm_client_pool.py   # LLM 客户端池
│   ├── 💬 chat_session.py       # 聊天会话管理
│   ├── 🔁 retry_strategy.py     # 重试策略
│   ├── 📈 metrics.py            # 指标收集
│   ├── 🔍 RAG.py               # 检索增强生成
│   └── 📝 logger.py             # 日志系统
├── 📂 knowledge_base/           # 知识库
├── 🚀 main.py                   # 主执行脚本
├── ⚙️ agent_base.py             # 智能体基类
├── 🔗 mediator.py              # 消息中介
└── 📚 README.md                # 主文档
```

## 🖥️ 使用指南

### 基本用法

```bash
# 基本运行
python main.py

# 指定模型
python main.py -m gpt-4o

# 运行特定实验
python main.py -t "./path/to/experiment"

# 运行多个实验
python main.py -t "./exp1" -t "./exp2"

# 并行运行 (4个worker)
python main.py -w 4

# 生产环境运行
python main.py -e production
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--model` | `-m` | 指定使用的 LLM 模型 | `configs/base.yaml` 中的 `current_model` |
| `--key_index` | `-k` | 指定 API 密钥索引 | `0` |
| `--root` | `-r` | 实验根目录路径 | `./TC/Datasets-TC` |
| `--target` | `-t` | 目标实验路径 (可多次指定) | 配置文件中的列表 |
| `--environment` | `-e` | 环境配置 | `development` |
| `--workers` | `-w` | 并行工作线程数 | `4` |
| `--no-parallel` | | 禁用并行执行 | `False` |

### 实验目录结构

每个实验目录必须包含：

```
experiment_name/
├── experiment_name_Prompt.txt    # 设计需求描述 (必需)
├── testbench.v                   # 测试平台 (必需)
├── experiment_name_ref.v         # 参考实现 (必需)
└── README.md                     # 实验说明 (可选)
```

**示例实验文件**:
```verilog
// 1_not_gate_Prompt.txt
设计一个简单的非门：
- 输入: a (1位)
- 输出: out (1位)
- 功能: out = ~a
- 只使用基本逻辑门

// testbench.v
module testbench;
    reg a;
    wire out, expected_out;
    
    not_gate uut (.a(a), .out(out));
    not_gate_ref ref (.a(a), .out(expected_out));
    
    initial begin
        a = 0; #10;
        if (out !== expected_out) $display("Test failed");
        a = 1; #10;
        if (out !== expected_out) $display("Test failed");
        else $display("All tests passed");
        $finish;
    end
endmodule

// not_gate_ref.v
module not_gate_ref (
    input a,
    output out
);
    not g1 (out, a);
endmodule
```

## ⚙️ 配置系统

CircuitMind 多智能体框架采用分层配置系统，支持灵活的环境和模型管理。

### 配置文件层次结构

```
configs/
├── base.yaml                    # 基础配置
├── environments/               # 环境特定配置
│   ├── development.yaml
│   └── production.yaml
├── models/                     # 模型配置
│   ├── gpt-4o.yaml
│   ├── deepseek-chat.yaml
│   ├── qwen2.5-coder-14b.yaml
│   └── ...
└── experiments/               # 实验批次配置
    ├── simple_test.yaml
    └── tc_datasets.yaml
```

### 主要配置参数

#### 🎛️ 基础配置 (`configs/base.yaml`)

```yaml
# === 核心设置 ===
debug: false                    # 调试模式
environment: development        # 当前环境
current_model: gpt-4o          # 默认使用的模型

# === 智能体配置 ===
agents:
  CoderAgent:
    max_auto_fix_attempts: 2    # 自动修复最大尝试次数
    max_retry_attempts: 2       # 最大重试次数
  
  Reviewer:
    max_auto_fix_attempts: 2    # 审查失败后自动修复次数
    max_retry_attempts: 2       # 审查重试次数
  
  Executor:
    timeout: 10                 # 仿真超时时间 (秒)
    max_retry_attempts: 3       # 执行重试次数

# === RAG 系统配置 ===
rag:
  enabled: true                 # 是否启用 RAG 系统
  knowledge_base_path: ./knowledge_base/RAG-data
  embedding_model: nomic-embed-text:latest
  llm_model: qwen2.5:7b
  ollama_host: http://localhost:11434

# === 实验配置 ===
experiments:
  root_dir: ./TC/Datasets-TC
  target_experiments:           # 目标实验列表
    - ./TC/Datasets-TC/1_not_gate
    - ./TC/Datasets-TC/2_second_tick
    # ... 更多实验
```

#### 🤖 模型配置 (`configs/models/*.yaml`)

**OpenAI 配置示例**:
```yaml
# configs/models/gpt-4o.yaml
api_keys:
  - "sk-proj-xxxxxxxxxxxx"     # 主 API 密钥
  - "sk-proj-yyyyyyyyyyyy"     # 备用密钥 (自动轮换)
base_url: "https://api.openai.com/v1"
max_retries: 3                 # API 调用重试次数
temperature: 0.7               # 生成温度
timeout: 30                    # 请求超时 (秒)
max_tokens: 4096              # 最大 token 数
```

**本地 Ollama 配置示例**:
```yaml
# configs/models/qwen2.5-coder-14b.yaml
api_keys:
  - "ollama"                   # Ollama 使用固定标识
base_url: "http://localhost:11434/v1"
max_retries: 3
temperature: 0.7
timeout: 60                    # 本地模型需要更长时间
```

## 🔧 高级功能

### 🔍 RAG (检索增强生成) 系统

RAG 系统通过历史经验和最佳实践增强代码生成质量。

**启用 RAG**:
```yaml
# configs/base.yaml
rag:
  enabled: true
  knowledge_base_path: ./knowledge_base/RAG-data
  embedding_model: nomic-embed-text:latest
  llm_model: qwen2.5:7b
  ollama_host: http://localhost:11434
```

**知识库结构**:
```
knowledge_base/
├── RAG-data/                   # 基础检索数据
│   ├── best_practices.json    # 最佳实践
│   ├── circuit_designs.json   # 电路设计模式
│   └── error_patterns.json    # 错误模式
├── RAG-data-detail/           # 详细数据
│   └── error_patterns.json   # 详细错误-解决方案映射
└── Model-incrementment/       # 模型实验结果
    ├── gpt-4o.json
    └── deepseek-chat.json
```

### 🔄 智能重试策略

系统根据错误类型采用不同的重试策略：

- **编译错误**: 线性退避，最多3次重试
- **仿真错误**: 指数退避，最多2次重试  
- **LLM API错误**: 指数退避，最多5次重试，支持密钥轮换
- **超时错误**: 线性退避，增加等待时间
- **验证错误**: 最多1次重试

### 🔄 LLM 客户端池化

自动管理 LLM 客户端连接，提升性能：

- **连接复用**: 避免重复创建客户端
- **自动清理**: 定期清理过期连接
- **线程安全**: 支持并发访问
- **统计监控**: 提供使用统计信息

### 📊 实时监控系统

完整的指标收集和监控功能：

```python
from utils.metrics import get_metrics_collector

metrics = get_metrics_collector()

# 获取系统指标
system_stats = metrics.get_system_summary()
print(f"成功率: {system_stats['success_rate']:.1%}")
print(f"总 LLM 调用: {system_stats['total_llm_calls']}")

# 获取实时统计
real_time = metrics.get_real_time_stats()
print(f"活跃智能体: {real_time['active_agents']}")
print(f"运行中实验: {real_time['running_experiments']}")
```

## 📊 输出和结果

### 📁 输出目录结构

```
experiments_output/
└── v0-merged/
    └── {model_name}/
        └── {experiment_name}_{run_number}/
            ├── experiment.log      # 详细执行日志
            ├── summary.txt         # 简要总结
            ├── llm_summary.txt     # LLM 生成的总结
            └── verilog_projects/   # 生成的 Verilog 文件
                └── {module_name}.v
```

### 📈 执行报告

系统自动生成详细的执行报告：

```
=============================================================
实验总结
=============================================================
总实验数: 10
成功: 8
失败: 2
成功率: 80.0%

系统指标:
总 LLM 调用数: 45
总 token 数: 123,456
总错误数: 12
平均实验时长: 34.56秒

LLM 客户端池:
活跃客户端: 2
总使用量: 45

重试统计:
总重试尝试: 18
成功重试: 15
失败重试: 3
=============================================================
```

## 🔧 故障排除

### 常见问题

**配置错误**:
```bash
# 问题: Model 'xxx' not found
# 解决方案:
# 1. 检查模型名称拼写
# 2. 确认模型配置文件存在
ls configs/models/

# 3. 查看可用模型
python -c "
from src.config import get_config_manager
cm = get_config_manager()
print('Available models:', list(cm.config.models.keys()))
"
```

**API 连接错误**:
```bash
# 问题: LLM API Error: 401 - Unauthorized
# 解决方案:
# 1. 验证 API 密钥
# 2. 检查网络连接
# 3. 确认 base_url 正确
# 4. 查看详细错误日志
tail -f experiments_output/*/experiment.log
```

**编译错误**:
```bash
# 问题: iverilog compilation failed
# 解决方案:
# 1. 确保 iverilog 已安装
iverilog -V

# 2. 检查生成的 Verilog 语法
# 3. 查看编译错误详情
# 4. 验证测试文件路径
```

**仿真超时**:
```yaml
# 问题: Simulation timed out
# 解决方案:
# 在 configs/base.yaml 中增加超时时间
agents:
  Executor:
    timeout: 10  # 增加到 10 秒
```

### 调试技巧

**启用详细日志**:
```yaml
# configs/environments/development.yaml
debug: true
logging:
  level: DEBUG
```

**监控 LLM 对话**:
```bash
# 查看 DIALOGUE 级别日志
grep "DIALOGUE" experiments_output/*/experiment.log
```

## 🤝 扩展开发

### 添加新智能体

```python
from agent_base import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, name, mediator, config):
        super().__init__(name, mediator, config, role="custom")
        self.register_message_handlers()
    
    def register_message_handlers(self):
        self.register_message_handler("custom_type", self._handle_custom)
    
    def _handle_custom(self, message, sender=None):
        # 实现自定义逻辑
        pass
```

### 添加新模型支持

1. **创建模型配置文件**:
```yaml
# configs/models/my_new_model.yaml
api_keys:
  - "your-api-key"
base_url: "https://api.example.com/v1"
max_retries: 3
temperature: 0.7
```

2. **更新基础配置**:
```yaml
# configs/base.yaml
current_model: my_new_model
```

### 自定义实验

参考 [实验目录结构](#实验目录结构) 创建新的实验目录，然后：

```bash
python main.py -t "./path/to/my_experiment"
```

## 🤝 贡献

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献方式
- 🐛 **报告问题**: 在 Issues 中报告 bug 或建议新功能
- 📝 **改进文档**: 帮助完善文档和示例
- 💻 **提交代码**: 修复 bug 或实现新功能
- 🧪 **测试验证**: 测试新版本并提供反馈

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详细信息。

## 🙏 致谢

感谢以下开源项目和社区的支持：
- [OpenAI](https://openai.com/) - GPT 模型支持
- [Icarus Verilog](http://iverilog.icarus.com/) - Verilog 编译器
- [Python Transitions](https://github.com/pytransitions/transitions) - 状态机框架
- [FAISS](https://github.com/facebookresearch/faiss) - 向量检索库

---

**⭐ 如果这个项目对你有帮助，请给我们一个 star！**

**🚀 开始你的硬件设计自动化之旅吧！** 