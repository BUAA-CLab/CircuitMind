<div align="center">
  <img src="Pics/CircuitMind-Logo.jpeg" width="200" alt="CircuitMind Logo">
  <div>&nbsp;</div>
  <h1>CircuitMind: 通过多智能体协作实现最优电路生成</h1>
  <div>&nbsp;</div>

  [English](README.md) | 简体中文

  <div>&nbsp;</div>
  <a href="https://huggingface.co/datasets/hyq001/TC-Bench">
    <img src="https://img.shields.io/badge/数据集(HuggingFace)-TC--Bench-blue" alt="Hugging Face Dataset">
  </a>
  <a href="https://github.com/BUAA-CLab/CircuitMind/tree/main/TC-Bench">
    <img src="https://img.shields.io/badge/数据集(GitHub)-TC--Bench-blue" alt="TC-Bench Dataset GitHub">
  </a>
  <a href="https://github.com/BUAA-CLab/CircuitMind">
     <img src="https://img.shields.io/github/stars/BUAA-CLab/CircuitMind?style=social" alt="GitHub Stars">
  </a>
  <div>&nbsp;</div>

  [![License](https://img.shields.io/github/license/BUAA-CLab/CircuitMind.svg)](https://github.com/BUAA-CLab/CircuitMind/blob/main/LICENSE)
  [![Python Version](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/) <div>&nbsp;</div>

  [📚 项目框架 README](https://github.com/BUAA-CLab/CircuitMind/blob/main/CircuitMind/README.md) |
  [💾 TC-Bench 数据集 README](https://github.com/BUAA-CLab/CircuitMind/blob/main/TC-Bench/README.md) |
  [📝 论文](https://arxiv.org/pdf/2504.14625v3) |
  [🐛 报告问题](https://github.com/BUAA-CLab/CircuitMind/issues/new/choose)

</div>

-----

## 目录

* [引言](#introduction)
* [主要成果](#key-achievements)
* [代码库内容](#repository-contents)
    * [TC-Bench 测试集与评估工具](#tc-bench-test-suite--evaluation-tools)
    * [CircuitMind 框架](#circuitmind-framework)
* [开源计划 (To-Do List)](#open-source-plan-to-do-list)
* [阅读我们的论文了解更多详情](#read-our-paper)
* [引用](#citation)
* [许可证](#license)

-----
<div id="introduction"></div>

## 引言

**CircuitMind** 是一个多智能体框架，旨在克服大型语言模型 (LLM) 在门级硬件设计中的效率限制。尽管 LLM 在代码生成方面表现出色，但它们在电路设计中的应用通常导致门数量远超人类专家的设计。这种“布尔优化障碍”源于 LLM 在高效门级设计所需的结构化推理和全局优化方面的局限性。

我们的工作提出了 **CircuitMind**，这是一个新颖的分层多智能体系统，通过三项关键创新实现了与人类专家相媲美的效率：

1.  **语法锁定 (Syntax Locking, SL):** 将生成限制在基本逻辑门（AND, OR, NOT, XOR, NAND），强制在网表级别进行真正的布尔优化。
2.  **检索增强生成 (Retrieval-Augmented Generation, RAG):** 通过从动态知识库中检索和重用优化的子电路模式，实现知识驱动的设计。
3.  **双重奖励优化 (Dual-Reward Optimization, DR)::** 通过有针对性的反馈循环，平衡功能正确性与物理效率（门数、延迟）。

为了评估我们的方法，我们引入了 **TC-Bench**，这是第一个利用来自 [TuringComplete 游戏](https://turingcomplete.game/) 的集体智能的门级基准测试。TC-Bench 基于数千个经过竞争优化的人类设计，提供与人类水平对齐的指标和性能等级。

<div id="key-achievements"></div>

## 主要成果

* CircuitMind 使大部分 (**55.6%**) 的模型实现能够达到或超过顶级人类专家在 TC-Bench 上的效率水平。
* 我们的框架证明了其能够提升中等规模模型，使其在无需专门训练的情况下性能超越更大的模型，并达到顶级人类专家的表现。
* 在各种 LLM 上观察到解决方案效率指数 (SEI) 的显著提高，证明了我们的协作方法在克服布尔优化障碍方面的有效性。

-----
<div id="repository-contents"></div>

## 代码库内容

该存储库包含 CircuitMind 和 TC-Bench 的开源代码、模型和数据。主要包含两个部分：

<div id="tc-bench-test-suite--evaluation-tools"></div>

### TC-Bench 测试集与评估工具

此目录包含用于评估的完整 TC-Bench 基准测试数据集。

* 数据集按 `Easy` (简单)、`Medium` (中等) 和 `Hard` (困难) 三个难度级别组织，每个级别下包含对应问题的子文件夹（问题描述、测试代码、参考解决方案）。
* **特别地，此目录还包含了性能评估工具**，允许你将生成电路的性能（使用 SEI 等指标）与已建立的人类专家等级进行比较。
* 关于数据集结构和评估工具使用的详细信息，可以在 **[TC-Bench 目录内的 README 文件](https://github.com/BUAA-CLab/CircuitMind/blob/main/TC-Bench/README.md)** 中找到。
* **[点击此处浏览 TC-Bench 数据集与工具](https://github.com/BUAA-CLab/CircuitMind/tree/main/TC-Bench)**

<div id="circuitmind-framework"></div>

### CircuitMind 框架

此目录包含 CircuitMind 多智能体框架的源代码。

* 关于如何设置、配置和运行 CircuitMind 框架的说明，请参见此目录下的 README 文件。
* **[点击此处查看 CircuitMind 代码及使用说明](https://github.com/BUAA-CLab/CircuitMind/blob/main/CircuitMind/README.md)**

-----
<div id="open-source-plan-to-do-list"></div>

## 开源计划 (To-Do List)

- [x] **TC-Bench 测试集与评估工具** - 已开源！
- [ ] **CircuitMind 多智能体框架** - 论文接收后将开源，敬请期待！

-----
<div id="read-our-paper"></div>

## 阅读我们的论文了解更多详情

阅读我们的论文了解更多详情: [论文](https://arxiv.org/pdf/2504.14625v3)

<div id="citation"></div>

## 引用

如果这项工作对你的研究有用，请引用我们的论文：

```bibtex
@article{qin2025towards,
  title={Towards Optimal Circuit Generation: Multi-Agent Collaboration Meets Collective Intelligence},
  author={Qin, Haiyan and Feng, Jiahao and Feng, Xiaotong and Xing, Wei W and Kang, Wang},
  journal={arXiv preprint arXiv:2504.14625},
  year={2025}
}
```

## 许可证

本项目采用 Apache License 2.0 许可证 - 详情请见 [LICENSE](./LICENSE) 文件。