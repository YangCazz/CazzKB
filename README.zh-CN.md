<div align="right">
  <a href="README.md">English</a>
</div>

<div align="center">

<img src="https://img.shields.io/badge/status-alpha-cyan?style=for-the-badge" alt="status">
<img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="python">
<img src="https://img.shields.io/badge/react-19-06b6d4?style=for-the-badge&logo=react" alt="react">
<img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="license">

</div>

<br>

# CazzKB

> 你的私有 AI 知识库助手 — 语义检索 · 混合重排 · 多模型对话

**CazzKB** 是轻量级、可自部署的个人知识库系统。上传 Markdown 文档，用自然语言与你的知识对话。所有数据 100% 留在你的机器上，零云服务依赖。

<br>

<p align="center">
  <img src="images/struct.png" alt="Architecture" width="720">
</p>

<br>

## 亮点

<p align="center">

|  |  |
|---|---|
| **语义分块** | YAML 元数据提取 · 代码块/表格/公式保护 · CJK token 估算 |
| **混合检索** | 向量 Dense + BM25 Sparse → RRF 融合 → Cross-Encoder 精排 |
| **多 Provider LLM** | Registry 工厂模式 · DeepSeek / Anthropic 双后端 · SSE 流式生成 |
| **本地 Embedding** | Ollama + bge-m3 · 1024 维 · 零 API 费用 |
| **专业 UI** | DeepSeek-GUI 设计系统 · 对话历史管理 · Markdown 代码高亮 · 消息编辑回退 |

</p>

<br>

## 快速开始

```bash
# 1. 拉取嵌入模型
ollama pull bge-m3

# 2. 克隆 & 安装
git clone https://github.com/YangCazz/CazzKB.git
cd CazzKB/backend
conda create -n cazzkb python=3.11 -y && conda activate cazzkb
uv pip install -r requirements.txt

# 3. 配置
cp .env.example .env          # 填入你的 DEEPSEEK_API_KEY

# 4. 启动
uvicorn app.main:app --reload --port 8000      # 终端 1：后端
cd ../frontend && npm install && npm run dev    # 终端 2：前端
```

打开 `http://localhost:5173` 开始对话。

<br>

<p align="center">
  <img src="images/Pipeline.png" alt="Retrieval Pipeline" width="720">
</p>

<br>

## 文档

完整指南 → [GUIDE.zh-CN.md](GUIDE.zh-CN.md) | Full guide → [GUIDE.md](GUIDE.md)

## License

MIT © YangCazz
