# 贡献指南

感谢您对 CircuitMind-Lite 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
- 使用 GitHub Issues 报告 bug
- 提供详细的错误信息和复现步骤
- 包含系统环境信息（Python版本、操作系统等）

### 提交代码
1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/CircuitMind-Lite.git
   cd CircuitMind-Lite
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行开发**
   - 遵循代码规范
   - 添加必要的测试
   - 更新相关文档

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 提供清晰的PR描述
   - 关联相关的Issue
   - 确保CI检查通过

## 📝 代码规范

### Python 代码风格
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 行长度限制为 88 字符

### 文档字符串
```python
def example_function(param1: str, param2: int) -> bool:
    """
    简短的函数描述。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 错误条件的描述
    """
    pass
```

### 提交信息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

## 🧪 测试

### 运行测试
```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_specific.py
```

### 添加测试
- 为新功能添加单元测试
- 确保测试覆盖率不降低
- 测试文件命名：`test_*.py`

## 🏗️ 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/your-username/CircuitMind-Lite.git
cd CircuitMind-Lite
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 4. 安装预提交钩子
```bash
pre-commit install
```

## 🎯 贡献领域

我们特别欢迎以下方面的贡献：

### 核心功能
- 新的智能体实现
- LLM模型适配
- 错误处理优化
- 性能改进

### 文档
- API文档完善
- 使用示例
- 最佳实践指南
- 多语言文档

### 测试
- 单元测试
- 集成测试
- 性能测试
- 边界条件测试

### 工具和基础设施
- CI/CD 改进
- 开发工具
- 部署脚本
- 监控和日志

## 🐛 问题报告模板

```markdown
**问题描述**
简要描述遇到的问题

**复现步骤**
1. 执行命令 '...'
2. 查看输出 '...'
3. 发现错误 '...'

**期望行为**
描述期望的正确行为

**实际行为**
描述实际发生的行为

**环境信息**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.8.10]
- CircuitMind-Lite: [e.g. v1.0.0]

**附加信息**
添加任何其他相关信息、日志或截图
```

## 📋 Pull Request 模板

```markdown
**变更类型**
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能改进
- [ ] 代码重构

**变更描述**
简要描述此PR的变更内容

**相关Issue**
关联的Issue编号（如果有）

**测试**
- [ ] 添加了新的测试
- [ ] 所有测试通过
- [ ] 手动测试通过

**检查清单**
- [ ] 代码遵循项目规范
- [ ] 自我审查了代码
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
```

## 🎉 致谢

感谢所有为 CircuitMind-Lite 项目做出贡献的开发者！

## 📞 联系方式

如有任何问题，请通过以下方式联系：
- GitHub Issues
- 项目维护者邮箱

---

再次感谢您的贡献！🚀 