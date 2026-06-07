# CazzKB

个人知识库对话助手 —— 对标 Notebook LM 的深度阅读+问答体验。

## 概述

CazzKB 帮助你构建私有的技术知识库，并通过自然语言对话进行检索和问答。从技术博客出发，逐步发展为通用知识管理工具。

## 当前阶段

**Phase 1：基础 RAG**
- Markdown 语义分块（代码块/表格保护）
- 混合检索（向量 + BM25 + RRF 融合）
- Claude API 驱动（架构预留 Ollama 本地切换）
- React Web UI

## 快速开始

（待实现）

## 参考项目

`ref/` 目录下包含以下参考项目的源码：

- [RAGFlow](https://github.com/infiniflow/ragflow) — Parser factory、元素级 Markdown 解析
- [LlamaIndex](https://github.com/run-llama/llama_index) — MarkdownNodeParser、SemanticSplitter
- [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) — Provider 抽象、Collector/Server 隔离
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) — 知识图谱增强检索
- [Mem0](https://github.com/mem0ai/mem0) — Memory-Augmented AI
- [LangGraph](https://github.com/langchain-ai/langgraph) — Agentic RAG 决策循环

## 设计文档

见 [docs/superpowers/specs/2026-06-07-cazzkb-design.md](docs/superpowers/specs/2026-06-07-cazzkb-design.md)

## 路线图

| Phase | 内容 |
|---|---|
| Phase 1 | 基础 RAG：语义分块 + 混合检索 + Claude API |
| Phase 2 | Graph-RAG：引文知识图谱 + 实体关系查询 |
| Phase 3 | Agentic RAG：自主多轮检索 + 工具调用 |
| Phase 4 | Memory-Augmented + Retrieval-free fallback |
