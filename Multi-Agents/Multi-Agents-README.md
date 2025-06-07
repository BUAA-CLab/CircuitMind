# CircuitMind Multi-Agent Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**CircuitMind Multi-Agent Framework** is an advanced LLM-based automated Verilog code generation and verification system. Through a multi-agent collaboration architecture, the system can automatically complete the entire hardware design process from design requirement understanding, code generation, code review to compilation simulation verification.

## 🎯 Core Features

### Automated Hardware Design Workflow
- **Intelligent Requirement Analysis**: Understanding hardware design requirements described in natural language
- **Structured Code Generation**: Generate industry-standard structural Verilog code
- **Intelligent Code Review**: Automatically detect syntax errors, logic issues and design specification violations
- **Automated Compilation Verification**: Use Icarus Verilog for compilation and simulation testing
- **Error Feedback & Repair**: Automatically fix code based on compilation/simulation errors

### Multi-Agent Collaboration Architecture
- **CoderAgent**: Responsible for Verilog code generation and requirement analysis
- **Reviewer**: Execute code review and automated error correction
- **Executor**: Handle code compilation and simulation execution
- **Summarizer**: Generate experiment reports and knowledge base updates
- **UserProxy**: Manage user interaction and task distribution

### Advanced Features
- **RAG Enhancement**: Retrieval-augmented generation based on historical experience and best practices
- **Multi-Model Support**: Compatible with OpenAI, DeepSeek, Qwen, Ollama and other LLMs
- **Intelligent Retry Strategy**: Differentiated retry mechanism based on error types
- **Concurrent Execution**: Support multi-experiment parallel processing for improved efficiency
- **Real-time Monitoring**: Complete metrics collection and performance monitoring system

## 🚀 Quick Start

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux/macOS/Windows
- **Verilog Tools**: Icarus Verilog (`iverilog`)

### Installation

```bash
# 1. Clone the project
git clone <repository-url>
cd CircuitMind/Multi-Agents

# 2. Create virtual environment (recommended)
conda create -n circuitmind python=3.11
conda activate circuitmind
# or python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Verilog tools
# Ubuntu/Debian:
sudo apt-get install iverilog

# macOS:
brew install icarus-verilog
```

### Basic Configuration

1. **Configure LLM Model** (choose one):
```bash
# Using OpenAI API
cp configs/models/gpt-4o.yaml configs/models/my_model.yaml
# Edit configs/models/my_model.yaml and fill in your API key

# Or use local Ollama
# Ensure Ollama service is running at http://localhost:11434
```

2. **Update Base Configuration**:
```yaml
# configs/base.yaml
current_model: my_model  # Use your configured model name
```

### First Run

```bash
# Run single simple experiment
python main.py -t "./TC/Datasets-TC/1_not_gate"

# Or run all configured experiments
python main.py
```

## 📁 Project Structure

```
Multi-Agents/
├── 📂 agents/                    # Agent implementations
│   ├── 🤖 coder_agent.py        # Code generation agent
│   ├── 🔍 reviewer.py           # Code review agent
│   ├── ⚙️ executor.py           # Code execution agent
│   ├── 📊 summarizer.py         # Result summarization agent
│   ├── 👤 user_proxy.py         # User proxy
│   ├── 📄 dff.v                 # D flip-flop module template
│   └── 📂 prompts/              # LLM prompt templates
├── 📂 configs/                   # Configuration management
│   ├── 📄 base.yaml             # Base configuration
│   ├── 📂 models/               # Model configurations
│   ├── 📂 environments/         # Environment configurations
│   └── 📂 experiments/          # Experiment configurations
├── 📂 src/                      # Core framework
│   ├── 📂 config/               # Configuration system
│   └── 📂 core/                 # Core components
├── 📂 utils/                    # Utility modules
│   ├── 🔄 llm_client_pool.py   # LLM client pool
│   ├── 💬 chat_session.py       # Chat session management
│   ├── 🔁 retry_strategy.py     # Retry strategies
│   ├── 📈 metrics.py            # Metrics collection
│   ├── 🔍 RAG.py               # Retrieval-augmented generation
│   └── 📝 logger.py             # Logging system
├── 📂 knowledge_base/           # Knowledge base
├── 🚀 main.py                   # Main execution script
├── ⚙️ agent_base.py             # Agent base class
├── 🔗 mediator.py              # Message mediator
└── 📚 README.md                # Main documentation
```

## 🖥️ Usage Guide

### Basic Usage

```bash
# Basic run
python main.py

# Specify model
python main.py -m gpt-4o

# Run specific experiment
python main.py -t "./path/to/experiment"

# Run multiple experiments
python main.py -t "./exp1" -t "./exp2"

# Parallel execution (4 workers)
python main.py -w 4

# Production environment
python main.py -e production
```

### Command Line Arguments

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--model` | `-m` | Specify LLM model to use | `current_model` in `configs/base.yaml` |
| `--key_index` | `-k` | Specify API key index | `0` |
| `--root` | `-r` | Experiment root directory path | `./TC/Datasets-TC` |
| `--target` | `-t` | Target experiment path (can be specified multiple times) | List in config file |
| `--environment` | `-e` | Environment configuration | `development` |
| `--workers` | `-w` | Number of parallel worker threads | `4` |
| `--no-parallel` | | Disable parallel execution | `False` |

### Experiment Directory Structure

Each experiment directory must contain:

```
experiment_name/
├── experiment_name_Prompt.txt    # Design requirement description (required)
├── testbench.v                   # Test bench (required)
├── experiment_name_ref.v         # Reference implementation (required)
└── README.md                     # Experiment description (optional)
```

**Example Experiment Files**:
```verilog
// 1_not_gate_Prompt.txt
Design a simple NOT gate with:
- Input: a (1-bit)
- Output: out (1-bit)
- Function: out = ~a
- Use only basic logic gates

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

## ⚙️ Configuration System

CircuitMind Multi-Agent Framework uses a hierarchical configuration system supporting flexible environment and model management.

### Configuration File Hierarchy

```
configs/
├── base.yaml                    # Base configuration
├── environments/               # Environment-specific configs
│   ├── development.yaml
│   └── production.yaml
├── models/                     # Model configurations
│   ├── gpt-4o.yaml
│   ├── deepseek-chat.yaml
│   ├── qwen2.5-coder-14b.yaml
│   └── ...
└── experiments/               # Experiment batch configs
    ├── simple_test.yaml
    └── tc_datasets.yaml
```

### Main Configuration Parameters

#### 🎛️ Base Configuration (`configs/base.yaml`)

```yaml
# === Core Settings ===
debug: false                    # Debug mode
environment: development        # Current environment
current_model: gpt-4o          # Default model to use

# === Agent Configuration ===
agents:
  CoderAgent:
    max_auto_fix_attempts: 2    # Max auto-fix attempts
    max_retry_attempts: 2       # Max retry attempts
  
  Reviewer:
    max_auto_fix_attempts: 2    # Auto-fix attempts after review failure
    max_retry_attempts: 2       # Review retry attempts
  
  Executor:
    timeout: 10                 # Simulation timeout (seconds)
    max_retry_attempts: 3       # Execution retry attempts

# === RAG System Configuration ===
rag:
  enabled: true                 # Enable RAG system
  knowledge_base_path: ./knowledge_base/RAG-data
  embedding_model: nomic-embed-text:latest
  llm_model: qwen2.5:7b
  ollama_host: http://localhost:11434

# === Experiment Configuration ===
experiments:
  root_dir: ./TC/Datasets-TC
  target_experiments:           # Target experiment list
    - ./TC/Datasets-TC/1_not_gate
    - ./TC/Datasets-TC/2_second_tick
    # ... more experiments
```

#### 🤖 Model Configuration (`configs/models/*.yaml`)

**OpenAI Configuration Example**:
```yaml
# configs/models/gpt-4o.yaml
api_keys:
  - "sk-proj-xxxxxxxxxxxx"     # Primary API key
  - "sk-proj-yyyyyyyyyyyy"     # Backup key (automatic rotation)
base_url: "https://api.openai.com/v1"
max_retries: 3                 # API call retry count
temperature: 0.7               # Generation temperature
timeout: 30                    # Request timeout (seconds)
max_tokens: 4096              # Maximum token count
```

**Local Ollama Configuration Example**:
```yaml
# configs/models/qwen2.5-coder-14b.yaml
api_keys:
  - "ollama"                   # Ollama uses fixed identifier
base_url: "http://localhost:11434/v1"
max_retries: 3
temperature: 0.7
timeout: 60                    # Local models need more time
```

## 🔧 Advanced Features

### 🔍 RAG (Retrieval-Augmented Generation) System

The RAG system enhances code generation quality through historical experience and best practices.

**Enable RAG**:
```yaml
# configs/base.yaml
rag:
  enabled: true
  knowledge_base_path: ./knowledge_base/RAG-data
  embedding_model: nomic-embed-text:latest
  llm_model: qwen2.5:7b
  ollama_host: http://localhost:11434
```

**Knowledge Base Structure**:
```
knowledge_base/
├── RAG-data/                   # Basic retrieval data
│   ├── best_practices.json    # Best practices
│   ├── circuit_designs.json   # Circuit design patterns
│   └── error_patterns.json    # Error patterns
├── RAG-data-detail/           # Detailed data
│   └── error_patterns.json   # Detailed error-solution mapping
└── Model-incrementment/       # Model experiment results
    ├── gpt-4o.json
    └── deepseek-chat.json
```

### 🔄 Intelligent Retry Strategy

The system uses different retry strategies based on error types:

- **Compilation Error**: Linear backoff, maximum 3 retries
- **Simulation Error**: Exponential backoff, maximum 2 retries
- **LLM API Error**: Exponential backoff, maximum 5 retries, supports key rotation
- **Timeout Error**: Linear backoff, increased wait time
- **Validation Error**: Maximum 1 retry

### 🔄 LLM Client Pooling

Automatically manage LLM client connections for improved performance:

- **Connection Reuse**: Avoid creating duplicate clients
- **Automatic Cleanup**: Periodically clean expired connections
- **Thread Safety**: Support concurrent access
- **Statistics Monitoring**: Provide usage statistics

### 📊 Real-time Monitoring System

Complete metrics collection and monitoring functionality:

```python
from utils.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Get system metrics
system_stats = metrics.get_system_summary()
print(f"Success rate: {system_stats['success_rate']:.1%}")
print(f"Total LLM calls: {system_stats['total_llm_calls']}")

# Get real-time statistics
real_time = metrics.get_real_time_stats()
print(f"Active agents: {real_time['active_agents']}")
print(f"Running experiments: {real_time['running_experiments']}")
```

## 📊 Output and Results

### 📁 Output Directory Structure

```
experiments_output/
└── v0-merged/
    └── {model_name}/
        └── {experiment_name}_{run_number}/
            ├── experiment.log      # Detailed execution log
            ├── summary.txt         # Brief summary
            ├── llm_summary.txt     # LLM-generated summary
            └── verilog_projects/   # Generated Verilog files
                └── {module_name}.v
```

### 📈 Execution Report

The system automatically generates detailed execution reports:

```
=============================================================
EXPERIMENT SUMMARY
=============================================================
Total experiments: 10
Successful: 8
Failed: 2
Success rate: 80.0%

SYSTEM METRICS:
Total LLM calls: 45
Total tokens: 123,456
Total errors: 12
Average experiment duration: 34.56s

LLM CLIENT POOL:
Active clients: 2
Total usage: 45

RETRY STATISTICS:
Total retry attempts: 18
Successful retries: 15
Failed retries: 3
=============================================================
```

## 🔧 Troubleshooting

### Common Issues

**Configuration Errors**:
```bash
# Problem: Model 'xxx' not found
# Solution:
# 1. Check model name spelling
# 2. Confirm model config file exists
ls configs/models/

# 3. View available models
python -c "
from src.config import get_config_manager
cm = get_config_manager()
print('Available models:', list(cm.config.models.keys()))
"
```

**API Connection Errors**:
```bash
# Problem: LLM API Error: 401 - Unauthorized
# Solution:
# 1. Verify API key
# 2. Check network connection
# 3. Confirm base_url is correct
# 4. View detailed error logs
tail -f experiments_output/*/experiment.log
```

**Compilation Errors**:
```bash
# Problem: iverilog compilation failed
# Solution:
# 1. Ensure iverilog is installed
iverilog -V

# 2. Check generated Verilog syntax
# 3. View compilation error details
# 4. Verify test file paths
```

**Simulation Timeout**:
```yaml
# Problem: Simulation timed out
# Solution:
# Increase timeout in configs/base.yaml
agents:
  Executor:
    timeout: 10  # Increase to 10 seconds
```

### Debugging Tips

**Enable Verbose Logging**:
```yaml
# configs/environments/development.yaml
debug: true
logging:
  level: DEBUG
```

**Monitor LLM Conversations**:
```bash
# View DIALOGUE level logs
grep "DIALOGUE" experiments_output/*/experiment.log
```

## 🤝 Extension Development

### Adding New Agents

```python
from agent_base import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, name, mediator, config):
        super().__init__(name, mediator, config, role="custom")
        self.register_message_handlers()
    
    def register_message_handlers(self):
        self.register_message_handler("custom_type", self._handle_custom)
    
    def _handle_custom(self, message, sender=None):
        # Implement custom logic
        pass
```

### Adding New Model Support

1. **Create Model Configuration File**:
```yaml
# configs/models/my_new_model.yaml
api_keys:
  - "your-api-key"
base_url: "https://api.example.com/v1"
max_retries: 3
temperature: 0.7
```

2. **Update Base Configuration**:
```yaml
# configs/base.yaml
current_model: my_new_model
```

### Custom Experiments

Refer to [Experiment Directory Structure](#experiment-directory-structure) to create new experiment directories, then:

```bash
python main.py -t "./path/to/my_experiment"
```

## 🤝 Contributing

We welcome community contributions! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information.

### Contribution Methods
- 🐛 **Report Issues**: Report bugs or suggest new features in Issues
- 📝 **Improve Documentation**: Help improve documentation and examples
- 💻 **Submit Code**: Fix bugs or implement new features
- 🧪 **Test Validation**: Test new versions and provide feedback

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to the following open source projects and communities for their support:
- [OpenAI](https://openai.com/) - GPT model support
- [Icarus Verilog](http://iverilog.icarus.com/) - Verilog compiler
- [Python Transitions](https://github.com/pytransitions/transitions) - State machine framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector retrieval library

---

**⭐ If this project helps you, please give us a star!**

**🚀 Start your automated hardware design journey!** 