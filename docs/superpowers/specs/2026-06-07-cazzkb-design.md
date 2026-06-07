# CazzKB 设计文档

个人知识库对话助手。对标 Notebook LM 的深度阅读+问答体验，轻量、可自部署、开源。

## 参考项目

| 项目 | 路径 | 借鉴要点 |
|---|---|---|
| RAGFlow | `ref/ragflow` | Parser factory、元素级 Markdown 解析、protected ranges、hybrid retrieval |
| LlamaIndex | `ref/llama_index` | MarkdownNodeParser、header-path 元数据、SemanticSplitter |
| AnythingLLM | `ref/anything-llm` | Collector/Server 进程隔离、40+ LLM Provider 接口、15/15/70 上下文分配 |
| Microsoft GraphRAG | `ref/graphrag` | 知识图谱增强检索（Phase 2） |
| Mem0 | `ref/mem0` | Memory.add/search API、跨会话记忆（Phase 4） |
| LangGraph | `ref/langgraph` | Agentic RAG 自主决策循环（Phase 3） |
| Dify | (未克隆，已研究) | 两级检索架构、视觉化 Pipeline DSL |

## 总体架构

四层分离，单进程可运行，预留分布式扩展：

```
┌──────────────────────────────────────────────┐
│          Web UI (React 18 + Vite + Tailwind)  │
├──────────────────────────────────────────────┤
│          API Layer (FastAPI)                  │
│    REST + SSE streaming + WebSocket           │
├──────────┬──────────┬──────────┬─────────────┤
│ Pipeline │Retrieval │Generation│ KB Manager  │
│  引擎    │  引擎    │  引擎    │ (CRUD+Config)│
├──────────┴──────────┴──────────┴─────────────┤
│          Storage Layer                        │
│  Chroma(向量) + SQLite(元数据) + FS(文档)     │
└──────────────────────────────────────────────┘
```

## 一、文档摄取管线（Ingestion Pipeline）

### Parser Factory

```
ParserFactory
├── MarkdownParser       (博客主力)
│   ├── YAML frontmatter 提取 → 元数据
│   ├── 代码块保护（不切割）
│   ├── 数学公式块保护
│   ├── 表格结构保留
│   └── Mermaid 代码块按纯文本处理
├── PlainTextParser      (通用降级)
└── CodeParser           (后续支持代码仓库)
```

### 分块策略

两步走（借鉴 RAGFlow 的元素提取→合并模式）：

1. **元素提取**：逐行解析 Markdown，按标题/代码块/列表/引用块/表格/文本块提取为语义元素
2. **智能合并**：相邻小元素按 token 限制合并（默认 512 tokens），代码块和表格受 protected ranges 保护不切割

### Chunk 元数据

```python
{
    "content": "chunk 文本",
    "source_file": "2026-06-02-mamba-ssm.md",
    "title": "Mamba 全栈解析",
    "header_path": "/状态空间模型基础/连续时间状态空间模型",
    "element_type": "text",  # header|code|table|text|list|quote
    "date": "2026-06-02",
    "categories": ["深度学习"],
    "tags": ["Mamba", "SSM"],
    "chunk_index": 3,
    "prev_chunk_id": "...",
    "next_chunk_id": "...",
    "entities": [],        # Phase 2 Graph-RAG 填充
    "relations": []        # Phase 2 Graph-RAG 填充
}
```

## 二、检索引擎（Retrieval Engine）

### 两层检索架构

```
用户问题
  → Query Rewrite (可选)
  → 混合检索（向量 dense + BM25 sparse）
  → RRF 融合 (Reciprocal Rank Fusion, k=60)
  → Reranker (可选 cross-encoder)
  → Top-K 结果
```

### 索引/查询分离

| 层级 | 配置项 | 默认值 |
|---|---|---|
| 索引级 | embedding 模型、向量维度、分块策略 | text-embedding-3-small / 1536 / semantic |
| 查询级 | Top-K、相似度阈值、rerank 开关 | K=8 / 0.65 / 关 |

### 扩展点

- `GraphRetriever` 插件：检索实体关系图谱（Phase 2）
- `AgenticRetriever`：多轮自主检索（Phase 3）
- 检索置信度分数 + `needs_refinement` 标志

## 三、生成引擎（Generation Engine）

### LLM Provider 抽象

```python
class LLMProvider(ABC):
    def chat(self, messages, stream=False) -> ChatResponse
    def chat_stream(self, messages) -> Iterator[str]
    def prompt_window_limit(self) -> int

class AnthropicProvider(LLMProvider): ...   # Phase 1 主力
class DeepSeekProvider(LLMProvider): ...    # Phase 1 备选
class OllamaProvider(LLMProvider): ...      # Phase 3 本地切换
```

Embedding Provider 同理：OpenAI → 后续换本地模型。

### 上下文窗口分配

| 区域 | 占比 | 用途 |
|---|---|---|
| System Prompt | ~15% | 角色设定 + 回答格式 |
| Chat History | ~15% | 最近 N 轮摘要 |
| Retrieved Context | ~70% | 检索 chunk + 来源引用 |

### 生成策略

| 场景 | 行为 |
|---|---|
| 有检索结果 | 标准 RAG prompt：根据资料回答 + 引用标注 |
| 检索无结果 | 降级为 retrieval-free 推理 |
| 检索低置信度 | 附加免责声明 |

## 四、存储层

| 组件 | 技术 | 说明 |
|---|---|---|
| 向量存储 | Chroma（嵌入式） | 零外部依赖，可迁移至 Qdrant |
| 元数据 | SQLite + Peewee ORM | 文档、chunk、对话记录 |
| 文档缓存 | 文件系统 | 原始 Markdown + 解析缓存 |
| 配置 | YAML | KB 配置、分块参数、模型设置 |

## 五、API Layer

```
POST   /api/kb                    # 创建知识库
GET    /api/kb/{id}               # 查询知识库状态
POST   /api/kb/{id}/upload        # 上传文档
POST   /api/kb/{id}/chat          # 对话（SSE streaming）
GET    /api/kb/{id}/chunks        # 浏览已索引 chunks
DELETE /api/kb/{id}               # 删除知识库
```

## 六、Web UI

React 18 + Vite + Tailwind，三栏布局：

```
┌─────────────────────────────────────────┐
│  CazzKB                    [设置] [源]  │
├────────────┬────────────────────────────┤
│  知识库列表 │    对话区                    │
│  · 技术博客 │    Q: Mamba的选择性机制?    │
│  · 论文笔记 │    A: [引用来源] ...        │
│            │                            │
│  + 新建    │    ┌──────────────────┐    │
│            │    │ 输入...     [发送]│    │
│            │    └──────────────────┘    │
└────────────┴────────────────────────────┘
```

核心交互：SSE 流式生成、引用标注可点击展开来源、暗色主题。

## 七、进阶路线图

```
Phase 1 (当前)    → 基础 RAG：语义分块 + 混合检索 + Claude API
Phase 2 (后续)    → Graph-RAG：引文知识图谱 + 实体关系查询
Phase 3 (后续)    → Agentic RAG：自主多轮检索 + 工具调用
Phase 4 (后续)    → Memory-Augmented：跨会话记忆 + Retrieval-free fallback
```

## 八、项目结构

```
CazzKB/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── ingestion/        # Markdown parser + chunker
│   │   ├── retrieval/        # Hybrid search + rerank
│   │   ├── generation/       # LLM + Embedding providers
│   │   ├── kb_manager/       # KB CRUD
│   │   └── models/           # Peewee ORM models
│   ├── config/
│   │   └── default.yaml
│   └── tests/
├── frontend/                 # React + Vite + Tailwind
├── ref/                      # 参考项目（不提交）
├── docs/
│   └── superpowers/
│       └── specs/
└── data/                     # 运行时数据（不提交）
    ├── chroma/
    └── cazzkb.db
```
