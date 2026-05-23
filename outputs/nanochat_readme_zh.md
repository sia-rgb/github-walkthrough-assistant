# README 中文翻译

- 来源：https://github.com/karpathy/nanochat
- 仓库：karpathy/nanochat
- 默认分支：master
- README 路径：README.md

---

## 中文 README

# nanochat

![nanochat 标志](dev/nanochat.png)
![规模定律](dev/scaling_laws_jan26.png)

nanochat 是训练大型语言模型（LLM）的最简实验框架。它设计为在单个 GPU 节点上运行，代码精简/可定制，并覆盖了所有主要的 LLM 阶段，包括分词、预训练、微调、评估、推理和聊天界面。例如，你可以训练自己的 GPT-2 级别 LLM（2019 年训练成本约为 43,000 美元），仅需 48 美元（约 2 小时 8XH100 GPU 节点），然后通过熟悉的类似 ChatGPT 的网页界面与它对话。在竞价实例上，总成本可以接近 15 美元。更一般地，nanochat 开箱即用，只需设置一个复杂度调节旋钮：`--depth`（GPT 变压器模型中的层数），即可训练整个计算最优模型系列（GPT-2 能力大致对应 depth 26）。所有其他超参数（变压器宽度、注意力头数、学习率调整、训练步数、权重衰减……）都会自动以最优方式计算。

关于仓库的问题，我推荐使用 Devin/Cognition 的 [DeepWiki](https://deepwiki.com/karpathy/nanochat) 提问，或者使用 [讨论标签页](https://github.com/karpathy/nanochat/discussions)，或者加入 Discord 上的 [#nanochat](https://discord.com/channels/1020383067459821711/1427295580895314031) 频道。

## 达到 GPT-2 时间排行榜

目前，开发主要集中于优化预训练阶段，该阶段消耗的计算资源最多。受 modded-nanogpt 仓库的启发，为了激励进展和社区协作，nanochat 维护了一个“GPT-2 速度冲刺”排行榜，记录将 nanochat 模型训练到 GPT-2 级别能力所需的挂钟时间，通过 DCLM CORE 分数衡量。[runs/speedrun.sh](runs/speedrun.sh) 脚本始终反映训练 GPT-2 级别模型并与之对话的参考方法。当前排行榜如下：

| # | 时间 | val_bpb | CORE | 描述 | 日期 | 提交 | 贡献者 |
|---|-------------|---------|------|-------------|------|--------|--------------|
| 0 | 168 小时 | - | 0.2565 | 原始 OpenAI GPT-2 检查点 | 2019 | - | OpenAI |
| 1 | 3.04 | 0.74833 | 0.2585 | d24 基线，稍微过训练 | 2026 年 1 月 29 日 | 348fbb3 | @karpathy |
| 2 | 2.91 | 0.74504 | 0.2578 | d26 稍微欠训练 **+fp8** | 2026 年 2 月 2 日 | a67eba3 | @karpathy |
| 3 | 2.76 | 0.74645 | 0.2602 | 将总批大小提高到 100 万个 token | 2026 年 2 月 5 日 | 2c062aa | @karpathy |
| 4 | 2.02 | 0.71854 | 0.2571 | 将数据集更改为 NVIDIA ClimbMix | 2026 年 3 月 4 日 | 324e69c | @ddudek @karpathy |
| 5 | 1.80 | 0.71808 | 0.2690 | 自动研究 [第 1 轮](https://x.com/karpathy/status/2031135152349524125) | 2026 年 3 月 9 日 | 6ed7d1d | @karpathy |
| 6 | 1.65 | 0.71800 | 0.2626 | 自动研究第 2 轮 | 2026 年 3 月 14 日 | a825e63 | @karpathy |

我们主要关心的指标是“达到 GPT-2 的时间”——在 8XH100 GPU 节点上超越 GPT-2（1.6B）CORE 指标所需的挂钟时间。GPT-2 CORE 分数是 0.256525。2019 年，GPT-2 的训练成本约为 43,000 美元，令人难以置信的是，由于 7 年间全栈的诸多进步，我们现在可以快得多地做到，且成本远低于 100 美元（例如，当前约 3 美元/GPU/小时，8XH100 节点约 24 美元/小时，因此 2 小时约 48 美元）。

有关如何解读和贡献排行榜的更多文档，请参阅 [dev/LEADERBOARD.md](dev/LEADERBOARD.md)。

## 快速开始

### 设置

nanochat 使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理。安装：

```bash
uv sync --extra gpu    # 用于 CUDA（A100/H100 等）
uv sync --extra cpu    #（或）仅用于 CPU / MPS
source .venv/bin/activate
```

用于开发（添加 pytest、matplotlib、ipykernel、transformers 等）：

```bash
uv sync --extra gpu --group dev
```

### 复现并对话 GPT-2

最有趣的事情是训练自己的 GPT-2 并与它对话。整个流程包含在单个文件 [runs/speedrun.sh](runs/speedrun.sh) 中，设计用于 8XH100 GPU 节点。从你喜欢的供应商处启动一个 8XH100 GPU 实例（例如，我使用并推荐 [Lambda](https://lambda.ai/service/gpu-cloud)），然后启动训练脚本：

```bash
bash runs/speedrun.sh
```

你可能希望在 screen 会话中运行，因为这需要大约 3 小时。完成后，可以通过类似 ChatGPT 的网页界面与它对话。确保本地 uv 虚拟环境已激活（运行 `source .venv/bin/activate`），然后启动服务：

```bash
python -m scripts.chat_web
```

然后访问显示的 URL。确保正确访问，例如在 Lambda 上使用节点的公共 IP 加端口，例如 [http://209.20.xxx.xxx:8000/](http://209.20.xxx.xxx:8000/)。然后像平常使用 ChatGPT 一样与你的 LLM 对话！让它写故事或诗歌，问它你是谁看看幻觉，问它天为什么是蓝的，或者为什么是绿的。速度冲刺模型是 4e19 FLOPs 能力模型，所以有点像和一个幼儿园小朋友对话 :)。

---

<img width="2672" height="1520" alt="图像" src="https://github.com/user-attachments/assets/ed39ddf8-2370-437a-bedc-0f39781e76b5" />

---

更多说明：

- 代码在 Ampere 8XA100 GPU 节点上也能正常运行，但稍慢一些。
- 所有代码在单个 GPU 上也能正常运行（省略 `torchrun`），结果几乎相同（代码会自动切换到梯度累积），但你需要等待 8 倍时间。
- 如果你的 GPU 显存小于 80GB，你需要调整一些超参数，否则会 OOM / VRAM 不足。在脚本中查找 `--device-batch-size` 并减小它直到适合。例如从 32（默认）改为 16、8、4、2 甚至 1。小于 1 就需要更多经验并发挥创意。
- 大部分代码是相当原生的 PyTorch，因此应该能在任何支持它的硬件上运行——xpu、mps 等，但我个人没有测试所有路径，可能存在一些边缘问题。

## 研究

如果你是研究人员，希望帮助改进 nanochat，两个感兴趣的脚本是 [runs/scaling_laws.sh](runs/scaling_laws.sh) 和 [runs/miniseries.sh](runs/miniseries.sh)。有关文档，请参阅 [1 月 7 日迷你系列 v1](https://github.com/karpathy/nanochat/discussions/420)。对于快速实验（约 5 分钟预训练运行），我最喜欢的是训练一个 12 层模型（GPT-1 大小），例如：

```
OMP_NUM_THREADS=1 torchrun --standalone --nproc_per_node=8 -m scripts.base_train -- \
    --depth=12 \
    --run="d12" \
    --model-tag="d12" \
    --core-metric-every=999999 \
    --sample-every=-1 \
    --save-every=-1 \
```

这使用了 wandb（运行名 "d12"），仅在最后一步运行 CORE 指标，不采样和保存中间检查点。我喜欢在代码中修改一些内容，重新运行 d12（或 d16 等）并在迭代循环中查看是否有帮助。要查看某个运行是否有帮助，我喜欢监控 wandb 的以下图表：

1. `val_bpb`（验证损失，以与词表大小无关的单位“比特每字节”表示）相对于 `step`、`total_training_time` 和 `total_training_flops` 的函数。
2. `core_metric`（DCLM CORE 分数）
3. VRAM 利用率、`train/mfu`（模型 FLOPS 利用率）、`train/tok_per_sec`（训练吞吐量）

示例见 [此处](https://github.com/karpathy/nanochat/pull/498#issuecomment-3850720044)。

需要注意的重要事项：nanochat 是围绕一个复杂度旋钮——变压器深度——编写和配置的。这一个整数自动确定所有其他超参数（变压器宽度、注意力头数、学习率调整、训练步数、权重衰减…），使得训练出的模型是计算最优的。思路是用户不需要考虑或设置这些，只需用 `--depth` 请求更小或更大的模型，一切“即插即用”。通过扫描不同的深度，你可以得到 nanochat 在不同大小下的计算最优模型系列。GPT-2 能力模型（目前最受关注）在当前代码下大致在 d24-d26 范围内。但任何对仓库的候选更改都必须有足够的原则性，使其适用于所有深度设置。

## 在 CPU / MPS 上运行

脚本 [runs/runcpu.sh](runs/runcpu.sh) 展示了一个在 CPU 或 Apple Silicon 上运行的非常简单的示例。它大幅缩小了正在训练的 LLM，以适应数十分钟的合理训练时间。这样不会得到强大的结果。

## 精度 / 数据类型

nanochat 不使用 `torch.amp.autocast`。相反，精度通过一个全局 `COMPUTE_DTYPE`（在 `nanochat/common.py` 中定义）显式管理。默认情况下，它根据你的硬件自动检测：

| 硬件 | 默认数据类型 | 原因 |
|----------|--------------|-----|
| CUDA SM 80+（A100、H100 等） | `bfloat16` | 原生 bf16 张量核心 |
| CUDA SM < 80（V100、T4 等） | `float32` | 无 bf16；可通过 `NANOCHAT_DTYPE=float16` 使用 fp16（使用 GradScaler） |
| CPU / MPS | `float32` | 无低精度张量核心 |

你可以使用 `NANOCHAT_DTYPE` 环境变量覆盖默认值：

```bash
NANOCHAT_DTYPE=float32 python -m scripts.chat_cli -p "hello"   # 强制 fp32
NANOCHAT_DTYPE=bfloat16 torchrun --nproc_per_node=8 -m scripts.base_train  # 强制 bf16
```

工作原理：模型权重以 fp32 存储（用于优化器精度），但我们自定义的 `Linear` 层在前向传递中将它们转换为 `COMPUTE_DTYPE`。嵌入直接以 `COMPUTE_DTYPE` 存储以节省显存。这为我们提供了与 autocast 相同的混合精度优势，但完全显式控制哪些运行在哪种精度下。

注意：`float16` 训练会自动在 `base_train.py` 中启用 `GradScaler` 以防止梯度下溢。SFT 也支持此功能，但 RL 目前不支持。fp16 推理在任何地方工作良好。

## 指南

我发布了一些可能包含有用信息的指南，从最新到最旧：

- [2026 年 2 月 1 日：以 <<100 美元击败 GPT-2：nanochat 之旅](https://github.com/karpathy/nanochat/discussions/481)
- [1 月 7 日迷你系列 v1](https://github.com/karpathy/nanochat/discussions/420) 记录了第一个 nanochat 模型迷你系列。
- 要向 nanochat 添加新能力，请参阅 [指南：在草莓中数 r（以及一般如何添加能力）](https://github.com/karpathy/nanochat/discussions/164)。
- 要自定义你的 nanochat，请参阅讨论中的 [指南：向你的 nanochat 注入身份](https://github.com/karpathy/nanochat/discussions/139)，其中描述了如何通过合成数据生成并将该数据混入 SFT 阶段来调整 nanochat 的个性。
- [2025 年 10 月 13 日：原始 nanochat 帖子](https://github.com/karpathy/nanochat/discussions/1) 介绍了 nanochat，但现在包含一些过时的信息，模型比当前主分支更旧（结果更差）。

## 文件结构

```
.
├── LICENSE
├── README.md
├── dev
│   ├── gen_synthetic_data.py       # 用于身份生成的示例合成数据
│   ├── generate_logo.html
│   ├── nanochat.png
│   └── repackage_data_reference.py # 预训练数据分片生成
├── nanochat
│   ├── __init__.py                 # 空
│   ├── checkpoint_manager.py       # 保存/加载模型检查点
│   ├── common.py                   # 各种小工具、生活质量改进
│   ├── core_eval.py                # 评估基础模型 CORE 分数（DCLM 论文）
│   ├── dataloader.py               # 分词分布式数据加载器
│   ├── dataset.py                  # 预训练数据的下载/读取工具
│   ├── engine.py                   # 使用 KV 缓存的高效模型推理
│   ├── execution.py                # 允许 LLM 执行 Python 代码作为工具
│   ├── gpt.py                      # GPT nn.Module 变压器
│   ├── logo.svg
│   ├── loss_eval.py                # 评估比特每字节（而非损失）
│   ├── optim.py                    # AdamW + Muon 优化器，单 GPU 和分布式
│   ├── report.py                   # 用于编写 nanochat 报告的工具
│   ├── tokenizer.py                # 以 GPT-4 风格包装的 BPE 分词器
│   └── ui.html                     # nanochat 前端的 HTML/CSS/JS
├── pyproject.toml
├── runs
│   ├── miniseries.sh               # 迷你系列训练脚本
│   ├── runcpu.sh                   # 在 CPU/MPS 上运行的简单示例
│   ├── scaling_laws.sh             # 规模定律实验
│   └── speedrun.sh                 # 训练约 100 美元的 nanochat d20
├── scripts
│   ├── base_eval.py                # 基础模型：CORE 分数、比特每字节、样本
│   ├── base_train.py               # 基础模型：训练
│   ├── chat_cli.py                 # 聊天模型：通过 CLI 对话
│   ├── chat_eval.py                # 聊天模型：评估任务
│   ├── chat_rl.py                  # 聊天模型：强化学习
│   ├── chat_sft.py                 # 聊天模型：训练 SFT
│   ├── chat_web.py                 # 聊天模型：通过 WebUI 对话
│   ├── tok_eval.py                 # 分词器：评估压缩率
│   └── tok_train.py                # 分词器：训练
├── tasks
│   ├── arc.py                      # 多项选择科学问题
│   ├── common.py                   # TaskMixture | TaskSequence
│   ├── customjson.py               # 从任意 jsonl 对话创建任务
│   ├── gsm8k.py                    # 8K 小学算术题
│   ├── humaneval.py                # 误称；简单的 Python 编码任务
│   ├── mmlu.py                     # 多项选择问题，广泛主题
│   ├── smoltalk.py                 # 来自 HuggingFace SmolTalk 的聚合数据集
│   └── spellingbee.py              # 教模型拼写/数数字的任务
├── tests
│   └── test_engine.py
└── uv.lock
```

## 贡献

nanochat 的目标是改进微型模型的最新技术水平，使其在预算 < 1000 美元的情况下可端到端访问。可访问性涉及总体成本，也涉及认知复杂性——nanochat 不是一个详尽可配置的 LLM“框架”；代码库中没有巨大的配置对象、模型工厂或 if-then-else 怪物。它是一个单一、内聚、极简、可读、可定制、最大程度可分叉的“强基线”代码库，设计为从头到尾运行，生成一个你可以与之对话的 ChatGPT 模型。目前，我个人最感兴趣的是加速达到 GPT-2 的延迟（即获得高于 0.256525 的 CORE 分数）。目前这需要大约 3 小时，但通过改进预训练阶段我们可以进一步改进。

当前 AI 政策：披露。提交 PR 时，请声明任何部分中有重大 LLM 贡献，且是你未编写或不完全理解的。

## 致谢

- 名称 nanochat 源自我的早期项目 [nanoGPT](https://github.com/karpathy/nanoGPT)，该项目仅涵盖预训练。
- nanochat 也受到 [modded-nanoGPT](https://github.com/KellerJordan/modded-nanogpt) 的启发，该仓库通过清晰的指标和排行榜游戏化 nanoGPT，并借鉴了其许多想法和预训练的部分实现。
- 感谢 [HuggingFace](https://huggingface.co/) 提供 fineweb 和 smoltalk。
- 感谢 [Lambda](https://lambda.ai/service/gpu-cloud) 提供用于开发此项目的计算资源。
- 感谢首席 LLM 传教士 🧙‍♂️ Alec Radford 提供的建议和指导。
- 感谢仓库总管 Sofie [@svlandeg](https://github.com/svlandeg) 帮助管理 nanochat 的问题、拉取请求和讨论。

## 引用

如果您在研究中使用 nanochat，请简单引用为：

```bibtex
@misc{nanochat,
  author = {Andrej Karpathy},
  title = {nanochat: The best ChatGPT that \$100 can buy},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/karpathy/nanochat}
}
```

## 许可证

MIT

---

## 专业术语注释

- **LLM**：Large Language Model，大型语言模型，如 GPT 系列。
- **GPT-2**：OpenAI 在 2019 年发布的第二代生成式预训练变压器模型，参数规模 1.6B。
- **GPU 节点**：通常指配备多块 GPU 的服务器实例。本项目中常用 8 块 H100（8XH100）节点进行训练。
- **tokenization**（分词）：将文本切分成词元（token）的过程，是 LLM 的输入预处理步骤。
- **pretraining**（预训练）：在大量无标注文本上训练 LLM 的基础阶段，学习语言知识。
- **finetuning**（微调）：在预训练基础上，使用特定任务数据（如对话数据）进一步训练模型。
- **evaluation**（评估）：衡量模型性能的过程，本项目中主要使用 DCLM CORE 分数和 val_bpb。
- **inference**（推理）：使用训练好的模型生成输出（如回答问题）。
- **chat UI**：聊天界面，本项目提供基于 Web 的聊天界面（chat_web）和命令行界面（chat_cli）。
- **scaling laws**（规模定律）：描述模型性能随计算量、数据量、参数量等变化的经验规律。
- **compute-optimal models**（计算最优模型）：在给定计算预算下，参数量和训练数据量达到最佳平衡的模型。
- **depth**（深度）：变压器模型中解码器层的数量，是 nanochat 调节模型复杂度的主要旋钮。
- **宽度、注意力头数、学习率调整、训练步数、权重衰减**：深度学习超参数，nanochat 根据 depth 自动优化选择。
- **val_bpb**：验证集上的损失，以“比特每字节”（bits per byte）表示，与词表大小无关，便于跨模型比较。
- **CORE score**：DCLM（DataComp for Language Models）基准中的核心指标，衡量模型在语言理解任务上的综合能力。GPT-2 的 CORE 分数为 0.256525。
- **DCLM**：DataComp for Language Models，由 NVIDIA 等推出的语言模型数据质量和性能评估基准。
- **FLOPs**：浮点运算次数，衡量计算量。项目中使用 total_training_flops 表示总训练计算量。
- **MFU（Model FLOPS Utilization）**：模型 FLOPs 利用率，衡量模型利用 GPU 计算能力的效率。
- **VRAM**：显存（GPU 内存），本项目中许多配置针对 80GB VRAM 的 GPU 设计。
- **SFT**：Supervised Fine-Tuning，监督微调，使用人工标注的对话数据微调模型。
- **RL**：强化学习，在聊天模型中进一步优化对话策略。
- **BPE**：字节对编码（Byte-Pair Encoding），一种子词分词算法，GPT-4 也采用此类分词器。
- **KV Cache**：键值缓存，在推理时缓存注意力机制中的 Key 和 Value 矩阵以加速生成。
- **AdamW**：一种优化器，结合 Adam 和权重衰减。
- **Muon**：NVIDIA 提出的另一种优化器，本项目在优化器中同时包含 AdamW 和 Muon。
- **GradScaler**：梯度缩放器，用于混合精度训练 fp16 时防止梯度下溢。
- **torchrun**：PyTorch 的分布式启动工具，用于多 GPU 训练。
- **wandb**：Weights & Biases，实验追踪工具，用于记录训练指标、超参数和可视化。
- **SM（Streaming Multiprocessor）**：CUDA 核心的流多处理器，SM 80+ 对应 A100/H100 等支持 bf16 的硬件。
- **bf16 / fp16 / fp32**：bfloat16、float16、float32 三种浮点格式，bf16 具有与 fp32 相同的指数范围，适合混合精度训练。
- **pre-training data shard**：预训练数据分片，将大型数据集切分成小块便于分布式加载。
- **miniseries**：nanochat 提供的模型系列，通过改变 depth 生成一系列计算最优模型。
- **leaderboard**：排行榜，记录不同训练配置达到 GPT-2 级别能力的挂钟时间。
