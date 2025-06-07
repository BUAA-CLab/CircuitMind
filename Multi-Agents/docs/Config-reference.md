# CircuitMind-Lite 配置参考文档

## 📋 配置系统概述

CircuitMind-Lite 采用分层配置系统，支持：
- 🌍 **多环境配置** (development/production)
- 🤖 **多模型支持** (OpenAI/Ollama/DeepSeek等)
- ⚙️ **智能体自定义** (重试策略、超时设置等)
- 🧪 **实验批次管理** (目标实验、输出路径等)

## 🗂️ 配置文件结构

```
configs/
├── 📄 base.yaml                    # 基础配置 (必需)
├── 📁 environments/               # 环境配置
│   ├── 📄 development.yaml        # 开发环境
│   ├── 📄 production.yaml         # 生产环境
│   └── 📄 testing.yaml            # 测试环境
├── 📁 models/                     # 模型配置
│   ├── 📄 gpt-4o.yaml             # OpenAI GPT-4o
│   ├── 📄 deepseek-chat.yaml      # DeepSeek Chat
│   ├── 📄 qwen2.5-coder-14b.yaml  # Qwen 2.5 Coder
│   └── 📄 ...                     # 其他模型
└── 📁 experiments/               # 实验批次配置
    ├── 📄 simple_test.yaml        # 简单测试批次
    ├── 📄 tc_datasets.yaml        # 完整数据集
    └── 📄 custom_batch.yaml       # 自定义批次
```

## ⚙️ 基础配置详解 (`configs/base.yaml`)

### 核心设置

```yaml
# === 系统核心设置 ===
debug: false                        # 调试模式开关
environment: development            # 当前环境 (development/production/testing)
current_model: gpt-4o              # 默认使用的模型名称
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `debug` | boolean | `false` | 启用详细调试信息和额外日志 |
| `environment` | string | `development` | 当前运行环境，影响日志级别和行为 |
| `current_model` | string | - | 默认使用的 LLM 模型名称 |

### 智能体配置

```yaml
# === 智能体行为配置 ===
agents:
  CoderAgent:                       # 代码生成智能体
    max_auto_fix_attempts: 2        # 自动修复最大尝试次数
    max_retry_attempts: 2           # 代码生成最大重试次数
    template_dir: "agents/prompts"  # 提示模板目录
  
  Reviewer:                         # 代码审查智能体
    max_auto_fix_attempts: 2        # 审查失败后自动修复次数
    max_retry_attempts: 2           # 审查重试次数
    template_dir: "agents/prompts"  # 提示模板目录
  
  Executor:                         # 代码执行智能体
    timeout: 2                      # 仿真超时时间 (秒)
    max_retry_attempts: 3           # 执行重试次数
  
  Summarizer:                       # 结果汇总智能体
    output_format: "json"           # 输出格式 (json/markdown)
```

#### CoderAgent 配置详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_auto_fix_attempts` | int | `2` | 基于错误信息自动修复代码的最大尝试次数 |
| `max_retry_attempts` | int | `2` | 代码生成失败时的最大重试次数 |
| `template_dir` | string | `"agents/prompts"` | Jinja2 提示模板存储目录 |

#### Reviewer 配置详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_auto_fix_attempts` | int | `2` | 代码审查发现问题后自动修复的尝试次数 |
| `max_retry_attempts` | int | `2` | 审查过程失败时的重试次数 |

#### Executor 配置详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | int | `2` | Verilog 仿真的超时时间 (秒) |
| `max_retry_attempts` | int | `3` | 编译/仿真失败时的重试次数 |

### RAG 系统配置

```yaml
# === RAG (检索增强生成) 配置 ===
rag:
  enabled: false                                        # 是否启用 RAG 系统
  knowledge_base_path: "./knowledge_base/RAG-data"      # 基础知识库路径
  detail_knowledge_base_path: "./knowledge_base/RAG-data-detail" # 详细知识库路径
  index_path: "./knowledge_base/RAG-data/vector_index.faiss" # FAISS 向量索引路径
  data_path: "./knowledge_base/RAG-data/vector_data.json"    # 向量数据路径
  embedding_model: "nomic-embed-text:latest"           # 嵌入模型名称
  llm_model: "qwen2.5-coder:14b"                       # RAG 使用的 LLM 模型
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `false` | 是否启用 RAG 功能 |
| `knowledge_base_path` | string | - | 基础知识库文件目录 |
| `embedding_model` | string | - | 用于向量化的嵌入模型 |
| `llm_model` | string | - | RAG 检索时使用的 LLM 模型 |

### 实验配置

```yaml
# === 实验管理配置 ===
experiments:
  root_dir: "./TC/Datasets-TC"                         # 实验根目录
  output_base_dir: "./experiments_output-v0-merged"    # 输出基础目录
  target_experiments:                                  # 目标实验列表
    - "./TC/Datasets/Easy/1_not_gate"
    - "./TC/Datasets/Easy/2_second_tick"
    - "./TC/Datasets/Easy/3_xor_gate"
    # ... 更多实验路径
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `root_dir` | string | - | 实验数据集根目录 |
| `output_base_dir` | string | - | 实验结果输出基础目录 |
| `target_experiments` | list | `[]` | 要执行的实验路径列表 |

### 智能体系统消息

```yaml
# === LLM 系统消息配置 ===
agent_system_messages:
  CoderAgent: |
    你是一个高度专业的 Verilog 代码生成助手，专注于实现电路功能...
    
  Reviewer: |
    你是一个专业的 Verilog 代码审查助手，专门确保代码正确性...
    
  Summarizer: |
    你是一个实验总结助手，负责分析实验过程并总结发现...
```

## 🤖 模型配置详解 (`configs/models/*.yaml`)

### OpenAI 模型配置

```yaml
# configs/models/gpt-4o.yaml
api_keys:                           # API 密钥列表 (支持多个，自动轮换)
  - "sk-proj-xxxxxxxxxxxx"          # 主密钥
  - "sk-proj-yyyyyyyyyyyy"          # 备用密钥
base_url: "https://api.openai.com/v1"  # API 端点 URL
max_retries: 3                      # API 调用最大重试次数
temperature: 0.7                    # 生成温度 (0.0-2.0)
timeout: 30                         # 请求超时时间 (秒)
max_tokens: 4096                    # 最大生成 token 数 (可选)
```

### 本地 Ollama 模型配置

```yaml
# configs/models/qwen2.5-coder-14b.yaml
api_keys:
  - "ollama"                        # Ollama 使用固定标识符
base_url: "http://localhost:11434/v1"  # 本地 Ollama 服务地址
max_retries: 3
temperature: 0.7
timeout: 60                         # 本地模型通常需要更长时间
```

### 商业 API 模型配置

```yaml
# configs/models/deepseek-chat.yaml
api_keys:
  - "sk-xxxxxxxxxxxxxxxxxxxx"
base_url: "https://api.deepseek.com"
max_retries: 3
temperature: 0.7
timeout: 30
```

### 模型配置参数详解

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `api_keys` | list | ✅ | API 密钥列表，系统会自动轮换使用 |
| `base_url` | string | ✅ | API 服务端点 URL |
| `max_retries` | int | ❌ | API 调用失败时的最大重试次数 |
| `temperature` | float | ❌ | 生成随机性控制 (0.0=确定性, 2.0=最随机) |
| `timeout` | int | ❌ | 单次 API 请求超时时间 (秒) |
| `max_tokens` | int | ❌ | 单次生成的最大 token 数量 |

## 🌍 环境配置详解

### 开发环境 (`configs/environments/development.yaml`)

```yaml
debug: true                         # 启用调试模式
logging:
  console_enabled: true             # 控制台日志输出
  level: DEBUG                      # 日志级别 (DEBUG/INFO/WARNING/ERROR)
  file_enabled: true                # 文件日志输出
```

### 生产环境 (`configs/environments/production.yaml`)

```yaml
debug: false                        # 关闭调试模式
logging:
  console_enabled: false            # 仅文件日志
  level: INFO                       # 较高日志级别
  file_enabled: true
```

### 测试环境 (`configs/environments/testing.yaml`)

```yaml
debug: true
logging:
  console_enabled: true
  level: DEBUG
  file_enabled: true
experiments:
  output_base_dir: "./test_output"  # 测试专用输出目录
```

## 🧪 实验批次配置

### 简单测试批次 (`configs/experiments/simple_test.yaml`)

```yaml
root_dir: "./TC/Datasets-TC"
target_experiments:
  - "./TC/Easy/1_not_gate"
  - "./TC/Easy/2_second_tick"
  - "./TC/Easy/3_xor_gate"
```

### 完整数据集 (`configs/experiments/tc_datasets.yaml`)

```yaml
root_dir: "./TC/Datasets-TC"
target_experiments:
  # Easy 级别实验
  - "./TC/Datasets/Easy/1_not_gate"
  - "./TC/Datasets/Easy/2_second_tick"
  # ... 更多实验
  
  # Medium 级别实验
  - "./TC/Datasets/Medium/7_double_trouble"
  # ... 更多实验
  
  # Hard 级别实验
  - "./TC/Datasets/Hard/12_odd_change"
  # ... 更多实验
```

## 🔧 高级配置选项

### 性能调优配置

```yaml
# 高性能配置示例
agents:
  CoderAgent:
    max_retry_attempts: 5           # 增加重试次数
    max_auto_fix_attempts: 3        # 增加自动修复次数
  
  Executor:
    timeout: 10                     # 增加超时时间
    max_retry_attempts: 5

# 模型配置优化
models:
  high_performance_model:
    api_keys:
      - "key1"
      - "key2"
      - "key3"                      # 多密钥负载均衡
    max_retries: 5
    timeout: 60
    temperature: 0.3                # 降低随机性提高一致性
```

### 调试配置

```yaml
# 详细调试配置
debug: true
environment: development

logging:
  level: DEBUG
  console_enabled: true
  file_enabled: true

agents:
  CoderAgent:
    max_retry_attempts: 1           # 减少重试快速失败
    max_auto_fix_attempts: 1
  
  Executor:
    timeout: 30                     # 增加超时避免误判
```

## 📝 配置验证

### 自动验证

系统启动时会自动验证：
- ✅ 必需配置文件存在
- ✅ API 密钥格式正确
- ✅ 文件路径有效
- ✅ 数值范围合理
- ✅ 模型配置完整

### 手动验证命令

```bash
# 验证配置完整性
python -c "
from src.config import get_config_manager
try:
    cm = get_config_manager()
    print('✅ 配置验证通过')
    print(f'当前模型: {cm.config.current_model}')
    print(f'环境: {cm.config.environment}')
except Exception as e:
    print(f'❌ 配置验证失败: {e}')
"

# 验证模型连接
python -c "
from utils.llm_client_pool import get_llm_client_pool
from src.config import get_config_manager
pool = get_llm_client_pool()
config = get_config_manager().get_model_config()
try:
    client = pool.get_client(config)
    print('✅ 模型连接正常')
except Exception as e:
    print(f'❌ 模型连接失败: {e}')
"
```

## 🔄 配置热更新

系统支持运行时配置更新：

```python
from src.config import get_config_manager

config_manager = get_config_manager()

# 切换模型
config_manager.switch_model("gpt-4o")

# 更新智能体配置
config_manager.update_config(
    agents={
        "CoderAgent": {
            "max_retry_attempts": 5
        }
    }
)
```

## 📋 配置最佳实践

### ✅ 推荐做法

1. **分离敏感信息**: API 密钥单独存储，不提交到版本控制
2. **环境隔离**: 开发、测试、生产使用不同配置
3. **配置备份**: 重要配置文件定期备份
4. **渐进更新**: 配置变更后先在测试环境验证
5. **文档同步**: 配置变更及时更新文档

### ❌ 避免做法

1. **硬编码**: 避免在代码中硬编码配置值
2. **密钥泄露**: 不要将 API 密钥提交到公开仓库
3. **单点故障**: 避免只配置单个 API 密钥
4. **忽略验证**: 配置更改后要验证系统功能
5. **配置混乱**: 避免在多个地方重复定义相同配置

## 🚨 常见配置问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 模型不存在 | `current_model` 配置错误 | 检查模型名称和配置文件 |
| API 调用失败 | 密钥无效或过期 | 更新 API 密钥 |
| 路径错误 | 实验路径不存在 | 检查 `experiments.root_dir` 配置 |
| 超时频繁 | 超时设置过低 | 增加 `timeout` 配置值 |
| 内存不足 | 并发数过高 | 减少并行工作线程数 |