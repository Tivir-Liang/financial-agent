# 📈 Financial Agent (Advanced Teaching Agent)

Financial Agent 是一个专为金融量化分析与学术研究设计的智能体（Agent）。它采用“规划-执行-解读”的 Meta-Agent 双层架构，能够将自然语言的财务或市场研究需求，自动转化为 Python 量化代码，在本地沙盒中抓取数据、计算指标、进行统计回归，并最终将晦涩的数据结果翻译为通俗易懂的业务解析。

## ✨ 核心特性

* **🧠 双层智能架构**：外层大脑负责架构设计与稳健性约束（如异常处理、缩尾处理），内层 Agent 负责编写并执行高标准 Python 脚本。
* **🛡️ 金融级数据稳健性**：内置极其严格的容错与审计机制（如动态抓取 `yfinance` 字段、多层索引拍平、时区对齐、缺失值与流失率预警）。
* **🔄 闭环自动 Debug**：沙盒若执行报错，Agent 会自动捕获 Error 堆栈，并根据金融语境进行至多 2 次代码自我修复与重试。
* **🎓 零基础友好**：只需提出研究问题（如“帮我算一下苹果公司上季度的Beta值”），Agent 会自动完成从取数到解读的全流程。

---

## 🛠️ 快速安装

为了保证依赖包不与你电脑上的其他项目冲突，**强烈建议使用虚拟环境进行安装**。整个过程无需安装 Git。

### 1. 创建并激活虚拟环境

请打开你的命令行终端（Windows 用户打开 CMD 或 PowerShell，Mac/Linux 用户打开 Terminal），在你想存放项目的文件夹下执行以下命令：

**对于 Windows 用户：**
```bash
# 1. 创建名为 venv 的虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate
```

**对于 macOS / Linux 用户：**
```bash
# 1. 创建名为 venv 的虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate
```
*(成功激活后，你的命令行提示符最前方会出现 `(venv)` 字样。)*

### 2. 一键安装 Financial Agent

在确保虚拟环境已激活的情况下，直接通过下方的链接安装项目（此步骤会自动下载源码并安装所需的第三方库，如 `pandas`, `numpy`, `yfinance`, `statsmodels`, `openai` 等）：

```bash
pip install https://github.com/Tivir-Liang/financial-agent/archive/refs/heads/main.zip
```

---

## 🚀 使用指南

### 1. 准备 DeepSeek API Key
本 Agent 强依赖 DeepSeek 的 API 进行逻辑推理和代码生成。你需要在 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册并获取一个 API Key（以 `sk-` 开头）。

### 2. 启动 Agent
在终端中直接输入以下命令即可唤醒你的智能体：

```bash
financial-agent
```

### 3. 配置密钥与交互
* **环境变量优先**：如果你在系统中配置了 `DEEPSEEK_API_KEY` 环境变量，Agent 会自动读取。
* **手动输入兜底**：如果没有配置环境变量，运行程序后，终端会弹出提示 `🔑 请直接在此粘贴你的 DeepSeek API Key (sk-...) 并回车：`，按提示粘贴即可。
* **开始对话**：看到 `🎓 你的 financial Agent 已上线！` 后，就可以直接输入你的量化研究需求了。

**使用示例：**
> **You:** "帮我用 Fama-French 三因子模型跑一下特斯拉最近一年的日度超额收益率回归，看看它的 Alpha 是否显著。"
> 
> *(Agent 会自动规划下载数据、对齐时间戳、执行 OLS 回归，并返回带通俗解释的最终结论。)*

---

## ⚠️ 注意事项

1. **环境依赖**：请确保你的电脑上安装了 Python 3.8 或更高版本。
2. **沙盒安全**：Agent 会在你的本地环境中自动执行生成的 Python 代码。虽然 Agent 已被施加了严格的 Prompt 限制（如禁止执行系统破坏性指令、必须保持面向过程风格），但仍建议在此专用的虚拟环境中运行。
3. **数据源访问**：系统默认使用 `yfinance` 和 `pandas_datareader` 作为数据源，请确保你的网络环境能够正常访问 Yahoo Finance 等海外接口。
