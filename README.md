<div align="center">

<img src="https://img.shields.io/badge/status-alpha-cyan?style=for-the-badge" alt="status">
<img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="python">
<img src="https://img.shields.io/badge/react-19-06b6d4?style=for-the-badge&logo=react" alt="react">
<img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="license">

</div>

<br>

# CazzKB

> Your private AI knowledge base — semantic search, hybrid reranking, multi-model chat.

**CazzKB** is a lightweight, self-hosted knowledge base system. Upload Markdown documents and talk to your knowledge in natural language. All data stays on your machine — zero cloud dependencies.

<br>

<p align="center">
  <img src="images/struct.png" alt="Architecture" width="720">
</p>

<br>

## Highlights

<p align="center">

|  |  |
|---|---|
| **Semantic Chunking** | YAML frontmatter extraction · code/table/math protection · CJK token estimation |
| **Hybrid Retrieval** | Dense vector + BM25 sparse → RRF fusion → Cross-Encoder reranker |
| **Multi-Provider LLM** | DeepSeek / Anthropic via registry factory · SSE streaming |
| **Local Embedding** | Ollama + bge-m3 · 1024-dim · zero API cost |
| **Professional UI** | DeepSeek-GUI design system · conversation history · Markdown code highlighting · message editing |

</p>

<br>

## Quick Start

```bash
# 1. Pull embedding model
ollama pull bge-m3

# 2. Clone & install
git clone https://github.com/YangCazz/CazzKB.git
cd CazzKB/backend
conda create -n cazzkb python=3.11 -y && conda activate cazzkb
uv pip install -r requirements.txt

# 3. Configure
cp .env.example .env          # add your DEEPSEEK_API_KEY

# 4. Launch
uvicorn app.main:app --reload --port 8000      # Terminal 1: backend
cd ../frontend && npm install && npm run dev    # Terminal 2: frontend
```

Open `http://localhost:5173` and start chatting.

<br>

<p align="center">
  <img src="images/Pipeline.png" alt="Retrieval Pipeline" width="720">
</p>

<br>

## Documentation

Full setup guide, API reference, local deployment, and contribution guide → [GUIDE.md](GUIDE.md)

## License

MIT © YangCazz
