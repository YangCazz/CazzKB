<div align="center">

<img src="https://img.shields.io/badge/status-alpha-cyan?style=flat-square" alt="status">
<img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python" alt="python">
<img src="https://img.shields.io/badge/react-19-06b6d4?style=flat-square&logo=react" alt="react">
<img src="https://img.shields.io/badge/design-DeepSeek_GUI-0088ff?style=flat-square" alt="design">
<img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">

</div>

<br>

# CazzKB

> 你私有的 AI 知识库助手 — 深度语义检索 × 多模型对话

CazzKB 是轻量级、可自部署的个人知识库系统。上传 Markdown 文档，用自然语言与你的知识对话。语义分块保护代码、表格和公式完整性；混合检索融合向量与关键词，确保精准命中；多 Provider 架构无缝切换 LLM。

</br>

---

## 架构

```
┌────────────────────────────────────────────────┐
│              Web UI · React 19 + Tailwind 3       │
│              SSE Streaming                       │
├────────────────────────────────────────────────┤
│              API Layer · FastAPI                 │
│              REST + SSE streaming                │
├─────────┬──────────┬────────────┬───────────────┤
│ Parser  │ Retrieval│ Generation │  KB Manager   │
│ 语义分块 │ 混合检索  │ 多Provider  │  CRUD + 配置   │
├─────────┴──────────┴────────────┴───────────────┤
│              Storage · Chroma + SQLite + FS      │
└────────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 特性 |
|------|------|
| **Markdown Parser** | YAML frontmatter 提取 · 代码块/表格/公式保护 · Mermaid 识别 · header-path 层级追踪 |
| **Semantic Chunker** | 两步分块（元素提取→智能合并） · CJK token 估算 · protected range · 重叠窗口 |
| **Hybrid Retrieval** | 向量 dense + BM25 sparse → RRF 融合 (k=60) · 可插拔 Cross-Encoder Reranker |
| **LLM Provider** | DeepSeek / Anthropic 双后端 · registry 工厂模式 · SSE 流式生成 |
| **Web UI** | DeepSeek-GUI 设计系统 · 浅色主题 · 对话历史管理 · 流式渲染 · Markdown 代码高亮 · 消息编辑回退 |

---

## 快速开始

```bash
# 1. 环境
conda create -n cazzkb python=3.11
conda activate cazzkb

# 2. 安装依赖
cd backend
uv pip install -r requirements.txt

# 3. 配置 API keys
cp .env.example .env
# 编辑 .env 填入你的 API key

# 4. 启动后端 (terminal 1)
uvicorn app.main:app --reload --port 8000

# 5. 启动前端 (terminal 2)
cd frontend-v2
npm install
npm run dev
```

访问 `http://localhost:5173` 开始使用。

---

## 配置

编辑 `backend/config/default.yaml`：

```yaml
llm:
  factory: "deepseek"        # deepseek | anthropic
  model: "deepseek-chat"
  api_key: "${DEEPSEEK_API_KEY}"

embedding:
  factory: "openai"          # openai | ollama
  model: "text-embedding-3-small"

retrieval:
  rrf_k: 60
  dense_weight: 0.7
  top_k: 8
```

API key 通过 `.env` 注入，不走配置文件。

---

## API

| Method | Endpoint | 说明 |
|--------|----------|------|
| `POST` | `/api/kb` | 创建知识库 |
| `GET` | `/api/kb` | 列表所有知识库 |
| `GET` | `/api/kb/{id}` | 查询知识库详情 |
| `DELETE` | `/api/kb/{id}` | 删除知识库 |
| `POST` | `/api/kb/{id}/upload` | 上传 Markdown 文档 |
| `GET` | `/api/kb/{id}/chunks` | 浏览已索引分块 |
| `POST` | `/api/kb/{id}/chat` | 对话 (SSE streaming) |
| `GET` | `/api/kb/{id}/conversations` | 对话历史列表 |
| `GET` | `/api/conversations/{id}` | 获取对话详情 |
| `PATCH` | `/api/conversations/{id}` | 重命名对话 |
| `DELETE` | `/api/conversations/{id}` | 删除对话 |

---

## 项目结构

```
CazzKB/
├── backend/
│   ├── app/
│   │   ├── api/           FastAPI routes + SSE
│   │   ├── ingestion/     Markdown parser + chunker
│   │   ├── retrieval/     Embedding + BM25 + RRF
│   │   ├── generation/    LLM providers + prompts
│   │   ├── kb_manager/    中枢编排
│   │   └── models/        Peewee ORM
│   ├── config/
│   │   └── default.yaml   全局配置
│   └── tests/
├── frontend-v2/
│   └── src/
│       ├── components/
│       │   ├── chat/      MessageTimeline · MessageBubble · FloatingComposer · ChatStarterGrid
│       │   ├── sidebar/   SidebarFrame · TreeRow · CommandRow · SearchField
│       │   └── shared/    CopyButton · DevBadge · MarkdownComponents
│       ├── store/         Zustand 5 (chat-store)
│       ├── api/           REST + SSE client
│       └── hooks/         useResizableSidebar
└── docs/
    └── superpowers/
        ├── specs/         设计文档
        └── plans/         实现计划
```

---

## 路线图

| Phase | 内容 |
|-------|------|
| **1. RAG** ✓ | 语义分块 + 混合检索 + 多 LLM Provider |
| **2. Graph** | 引文知识图谱 · 实体关系查询 |
| **3. Agentic** | 自主多轮检索 · 工具调用 |
| **4. Memory** | 跨会话记忆 · Retrieval-free fallback |
