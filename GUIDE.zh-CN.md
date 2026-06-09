<div align="right">
  <a href="GUIDE.md">English</a>
</div>

# CazzKB 指南

- [前置条件](#前置条件)
- [安装启动](#安装启动)
- [配置详解](#配置详解)
- [本地部署](#本地部署)
- [API 参考](#api-参考)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)
- [路线图](#路线图)

---

## 前置条件

| 依赖 | 用途 | 安装 |
|------|------|------|
| Python 3.11+ | 后端 | `conda create -n cazzkb python=3.11` |
| Node.js 18+ | 前端 | `winget install OpenJS.NodeJS` |
| Ollama | 本地 Embedding | `ollama pull bge-m3` |

---

## 安装启动

### 1. 克隆

```bash
git clone https://github.com/YangCazz/CazzKB.git
cd CazzKB
```

### 2. 后端

```bash
cd backend
conda create -n cazzkb python=3.11 -y
conda activate cazzkb
uv pip install -r requirements.txt
```

### 3. 前端

```bash
cd frontend
npm install
```

### 4. 配置

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 填入 API key：

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. 启动

```bash
# 终端 1 — 后端
cd backend && uvicorn app.main:app --reload --port 8000

# 终端 2 — 前端
cd frontend && npm run dev
```

打开 `http://localhost:5173`。

---

## 配置详解

编辑 `backend/config/default.yaml`：

### LLM

```yaml
llm:
  factory: "anthropic"                      # Anthropic SDK → DeepSeek 兼容端点
  model: "deepseek-v4-pro[1m]"
  api_key: "${DEEPSEEK_API_KEY}"            # 从 .env 注入
  base_url: "https://api.deepseek.com/anthropic"
  max_tokens: 4096
```

可用 factory：`anthropic`、`deepseek`

### Embedding

```yaml
embedding:
  factory: "ollama"
  model: "bge-m3"
  dimension: 1024
```

可用 factory：`ollama`、`openai`

### Retrieval

```yaml
retrieval:
  rrf_k: 60
  dense_weight: 0.7
  candidate_multiplier: 3

reranker:
  factory: "none"         # none | bge | llm
  model: "BAAI/bge-reranker-v2-m3"
```

### Storage

```yaml
storage:
  chroma_path: "data/chroma"
  db_path: "data/cazzkb.db"
  upload_path: "data/uploads"
```

所有路径均为本地路径，零云服务依赖。

---

## 本地部署

完全离线方案，无需任何云 API：

| 组件 | 方案 | 配置 |
|------|------|------|
| LLM | Ollama + qwen2.5 / deepseek-r1 | 需添加 `OllamaProvider`（欢迎 PR） |
| Embedding | Ollama + bge-m3 | `embedding.factory: ollama` |
| Reranker | FlagEmbedding + bge-reranker-v2-m3 | `pip install FlagEmbedding` + `reranker.factory: bge` |

---

## API 参考

| Method | Endpoint | 说明 |
|--------|----------|------|
| `POST` | `/api/kb` | 创建知识库 |
| `GET` | `/api/kb` | 列表知识库 |
| `GET` | `/api/kb/{id}` | 知识库详情 |
| `DELETE` | `/api/kb/{id}` | 删除知识库 |
| `POST` | `/api/kb/{id}/upload` | 上传 Markdown |
| `GET` | `/api/kb/{id}/chunks` | 浏览分块 |
| `POST` | `/api/kb/{id}/chat` | 对话 (SSE) |
| `GET` | `/api/kb/{id}/conversations` | 对话历史 |
| `GET` | `/api/conversations/{id}` | 对话详情 |
| `PATCH` | `/api/conversations/{id}` | 重命名对话 |
| `DELETE` | `/api/conversations/{id}` | 删除对话 |

### SSE 事件格式

```
data: {"type":"meta","conversation_id":42}
data: {"type":"token","data":"Mamba"}
data: {"type":"token","data":" 是一种"}
...
data: {"type":"done"}
```

---

## 项目结构

```
CazzKB/
├── backend/
│   ├── app/
│   │   ├── api/              FastAPI routes + SSE
│   │   ├── ingestion/        Markdown parser + chunker
│   │   ├── retrieval/        Embedding + BM25 + RRF + Reranker
│   │   ├── generation/       LLM providers + RAG prompts
│   │   ├── kb_manager/       中枢编排
│   │   └── models/           Peewee ORM (SQLite)
│   ├── config/default.yaml
│   ├── scripts/              数据导入工具
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── chat/         MessageTimeline · FloatingComposer
│       │   ├── sidebar/      SidebarFrame · TreeRow · SearchField
│       │   └── shared/       CopyButton · DevBadge · MarkdownComponents
│       ├── store/            Zustand 5
│       └── api/              REST + SSE client
├── images/                   架构图 & 流水线图
├── GUIDE.md                  本文件
├── LICENSE
└── README.md
```

---

## 贡献指南

欢迎 Issue 和 PR。

```bash
# 安装开发依赖
cd backend && uv pip install -e ".[dev]"
cd frontend && npm install

# 运行测试
cd backend && python -m pytest tests/ -v --rootdir=.
```

请遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新功能
fix: 修复 Bug
docs: 更新文档
chore: 维护工作
test: 增加或修改测试
```

---

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| **1. RAG** | ✓ 已完成 | 语义分块 + 混合检索 + Reranker + 多 Provider + Web UI |
| **2. Graph** | 计划中 | 知识图谱 · 实体关系查询 |
| **3. Agentic** | 计划中 | 自主多轮检索 · 工具调用 |
| **4. Memory** | 计划中 | 跨会话记忆 · Retrieval-free fallback |
