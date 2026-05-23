# 项目概览

- 来源：https://github.com/karpathy/nanochat
- 仓库：karpathy/nanochat
- 默认分支：master
- 发布者类型：User
- 仓库描述：The best ChatGPT that $100 can buy.
- 分析文件：README.md, pyproject.toml

---

## 项目目标
nanochat 是一个实验性全栈框架，旨在以极低的成本（约 $48）快速训练出具备 GPT-2 能力的语言模型，并提供完整的训练、测试、推理和聊天 UI 工具链。其核心理念是通过单一复杂度旋钮（`--depth` 参数）自动计算所有超参数，实现计算最优的训练配置，让研究人员和开发者在单台 GPU 节点上就能复现当年耗费 $43,000 的模型。

## 解决的问题
该项目解决了大型语言模型（LLM）训练的高成本和高门槛问题。传统 GPT-2 训练需要昂贵的计算资源和复杂的调参经验，而 nanochat 通过优化的工程实现和自动超参数推导，将完整训练流程压缩到 2 小时、成本降至 $100 以下，并且提供可 hack 的代码，便于社区进行实验和迭代。这是一个**个人开源项目**（发布者为 @karpathy），致力于推动 LLM 训练民主化。

## 核心技术/功能
- **单参数计算最优配置**：仅需指定 Transformer 层数（`--depth`），自动计算宽度、头数、学习率、训练步数、权重衰减等所有超参数，实现计算最优。
- **混合精度训练**：通过自定义 `Linear` 层，权重存储为 fp32，前向传播中自动转换为 `bfloat16`/`float16`（视硬件自动检测或通过环境变量指定），并可选启用 `GradScaler`。
- **完整 LLM 训练管线**：涵盖 tokenization（tiktoken/rustbpe）、预训练（基于 DCLM CORE 评分基准）、SFT 监督微调、RL 强化学习、评估与推理（含 KV Cache 引擎）。
- **Web 聊天 UI**：使用 FastAPI + Uvicorn 提供 ChatGPT 风格的前端界面，支持一键加载训练好的模型进行对话。
- **分布式与单卡兼容**：通过 `torchrun` 支持 8 GPU 节点分布式训练，也可在单 GPU 上通过梯度累积运行，产生几乎相同结果。
- **自动监控**：集成 wandb 记录验证损失、CORE 评分、训练吞吐量、模型 FLOPS 利用率等指标。

## 硬件/软件要求
- **硬件**：
  - **推荐**：8 张 NVIDIA H100（80GB）GPU 节点（成本约 $24/hr），训练约 2 小时。
  - **兼容**：8 张 A100（80GB）节点（速度略慢）、单张 80GB GPU（训练时间延长 8 倍）。
  - **最小**：任意支持 CUDA 的 GPU（需 ≥80GB 才能运行默认配置；显存不足时需降低 `--device-batch-size`，甚至降至 1）。
  - **CPU / MPS**：支持运行极小模型（用于快速测试），但无法达到强结果。
- **软件**：
  - **Python**：≥3.10
  - **包管理器**：uv（推荐安装方式）
  - **核心依赖**：torch==2.9.1（CUDA 12.8 版或 CPU 版）、datasets、fastapi、psutil、rustbpe、tiktoken、tokenizers、uvicorn、wandb、kernels
  - **开发依赖（可选）**：ipykernel、matplotlib、pytest、transformers
  - **系统**：建议 Ubuntu 等 Linux 系统；CUDA 驱动需支持对应 PyTorch 版本（cu128）。
- **精度限制**：
  - `bfloat16` 需要 CUDA SM 80+（A100/H100 及以上）；SM <80 的 GPU 默认使用 `float32`，可通过 `NANOCHAT_DTYPE` 强制使用 `float16`（需 `GradScaler`）。
  - CPU/MPS 仅支持 `float32`。
