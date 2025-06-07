# CircuitMind-Lite 快速参考指南

## ⚡ 一分钟快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
sudo apt-get install iverilog  # Linux
# brew install icarus-verilog   # macOS

# 2. 配置模型 (选择一种)
# 方案A: 使用 OpenAI
cp configs/models/gpt-4o.yaml configs/models/my_model.yaml
# 编辑 my_model.yaml，填入 API 密钥

# 方案B: 使用本地 Ollama
# 确保 Ollama 运行在 localhost:11434

# 4. 更新配置
# 编辑 configs/base.yaml，设置 current_model: my_model

# 5. 运行测试
python main.py -t "./TC/Datasets-TC/1_not_gate"
```

## 🎛️ 常用命令

| 场景 | 命令 |
|------|------|
| 基本运行 | `python main.py` |
| 指定模型 | `python main.py -m gpt-4o` |
| 单个实验 | `python main.py -t "./path/to/experiment"` |
| 并行执行 | `python main.py -w 4` |
| 生产环境 | `python main.py -e production` |
| 调试模式 | `python main.py -e development` |

## 📁 关键文件位置

| 文件/目录 | 用途 |
|-----------|------|
| `configs/base.yaml` | 主配置文件 |
| `configs/models/` | LLM 模型配置 |
| `experiments_output/` | 实验结果输出 |
| `knowledge_base/` | RAG 知识库 |
| `main.py` | 主执行脚本 |

## ⚙️ 快速配置检查表

- [ ] **LLM 配置**: API 密钥已设置
- [ ] **Verilog 工具**: `iverilog -V` 可正常执行
- [ ] **实验路径**: 目标实验目录存在且包含必需文件
- [ ] **输出目录**: 有写入权限
- [ ] **网络连接**: 可访问 LLM API (如使用云端服务)

## 🚨 快速故障排查

| 错误信息 | 解决方案 |
|----------|----------|
| `Model 'xxx' not found` | 检查 `configs/models/` 目录和 `current_model` 设置 |
| `API Error: 401` | 验证 API 密钥有效性 |
| `iverilog not found` | 安装 Icarus Verilog |
| `Simulation timeout` | 增加 `agents.Executor.timeout` 配置值 |
| `Import Error` | 运行 `python compatibility_fixes.py` |
| `Permission denied` | 检查输出目录写入权限 |

## 📊 配置参数速查

### 基础配置 (`configs/base.yaml`)
```yaml
# 核心设置
current_model: "your_model"           # 使用的模型
debug: false                          # 调试模式

# 智能体配置
agents:
  CoderAgent:
    max_retry_attempts: 2             # 最大重试次数
    max_auto_fix_attempts: 2          # 自动修复次数
  Executor:
    timeout: 2                        # 仿真超时 (秒)

# RAG 系统
rag:
  enabled: false                      # 是否启用 RAG

# 实验配置
experiments:
  root_dir: "./TC/Datasets-TC"        # 实验根目录
  target_experiments: []              # 目标实验列表
```

### 模型配置 (`configs/models/*.yaml`)
```yaml
api_keys:
  - "your-api-key-here"               # API 密钥 (支持多个)
base_url: "https://api.example.com/v1" # API 端点
max_retries: 3                        # 重试次数
temperature: 0.7                      # 生成温度
timeout: 30                           # 请求超时
```

## 🔍 日志查看

```bash
# 查看最新实验日志
tail -f experiments_output/v0-merged/*/*/experiment.log

# 查看 LLM 对话
grep "DIALOGUE" experiments_output/*/*/experiment.log

# 查看错误信息
grep "ERROR" experiments_output/*/*/experiment.log

# 查看状态转换
grep "State transition" experiments_output/*/*/experiment.log
```

## 🧪 测试验证

```bash
# 测试配置系统
python -c "
from src.config import get_config_manager
cm = get_config_manager()
print('✓ 配置系统正常')
print(f'当前模型: {cm.config.current_model}')
print(f'可用模型: {list(cm.config.models.keys())}')
"

# 测试 LLM 连接
python -c "
from utils.llm_client_pool import get_llm_client_pool
from src.config import get_config_manager
pool = get_llm_client_pool()
config = get_config_manager().get_model_config()
client = pool.get_client(config)
print('✓ LLM 客户端连接正常')
"

# 测试 Verilog 工具
iverilog -V && echo "✓ Icarus Verilog 可用"
```

## 📈 性能优化建议

| 场景 | 建议 |
|------|------|
| **大量实验** | 使用并行执行 `-w 4` |
| **网络较慢** | 增加 `timeout` 配置 |
| **频繁重试** | 配置多个 API 密钥实现轮换 |
| **内存不足** | 减少并行工作线程数 |
| **调试问题** | 启用 `debug: true` 和 `level: DEBUG` |

## 🔧 环境变量

```bash
# 设置环境
export ENVIRONMENT=production

# 设置日志级别
export LOG_LEVEL=DEBUG

# 设置 API 密钥 (可选)
export OPENAI_API_KEY="your-key"
```

## 📞 获取帮助

```bash
# 查看命令行帮助
python main.py --help

# 查看配置帮助
python -c "
from src.config import get_config_manager
help(get_config_manager)
"

# 检查系统状态
python -c "
from utils.metrics import get_metrics_collector
metrics = get_metrics_collector()
print(metrics.get_system_summary())
"
```