# CazzKB NotebookLM-like 改造交接文档

更新时间：2026-09-09  
当前分支：`codex/notebooklm-foundation`  
当前目标：把 CazzKB 从“知识库聊天”升级为类似 NotebookLM 的“Notebook + Sources + Studio Artifacts”研究工作台。

## 当前仓库位置

- 本地路径：`C:\Users\Administrator\Documents\ChatGPT\YangCazzV2\CazzKB`
- GitHub 仓库：`https://github.com/YangCazz/CazzKB`
- 基线提交：`d04f633`
- 第一轮基础提交：
  - `ff0af87 Add notebook source and artifact foundation`

## 已完成内容

### 1. 后端数据模型

在 `backend/app/models/db.py` 中新增/扩展：

- `Document.source_type`
- `Document.summary`
- `Document.enabled`
- `Artifact` 表
  - `title`
  - `artifact_type`
  - `content`
  - `metadata_json`
  - `created_at`
  - `updated_at`

并补了轻量 schema migration：

- 老 SQLite 数据库启动时会自动补 `document` 表缺失字段。
- `Artifact` 表会在 `init_db()` 时创建。

### 2. 后端 Notebook / Sources / Artifacts API

在 `backend/app/api/routes.py` 中新增：

- Notebook alias
  - `POST /api/notebooks`
  - `GET /api/notebooks`
- Sources
  - `GET /api/kb/{kb_id}/sources`
  - `GET /api/notebooks/{notebook_id}/sources`
  - `GET /api/sources/{source_id}`
  - `PATCH /api/sources/{source_id}`
- Artifacts
  - `GET /api/kb/{kb_id}/artifacts`
  - `GET /api/notebooks/{notebook_id}/artifacts`
  - `POST /api/kb/{kb_id}/artifacts`
  - `POST /api/notebooks/{notebook_id}/artifacts`
  - `GET /api/artifacts/{artifact_id}`
  - `DELETE /api/artifacts/{artifact_id}`

在 `backend/app/kb_manager/manager.py` 中新增对应管理方法：

- `list_sources`
- `get_source`
- `update_source`
- `list_artifacts`
- `create_artifact`
- `get_artifact`
- `delete_artifact`

### 3. 前端 API 与类型

在 `frontend/src/types.ts` 中新增：

- `Notebook`
- `UploadedDocument`
- `Source`
- `SourceChunk`
- `SourceDetail`
- `Artifact`

在 `frontend/src/api/client.ts` 中新增：

- `listNotebooks`
- `createNotebook`
- `listSources`
- `getSource`
- `updateSource`
- `listArtifacts`
- `createArtifact`
- `getArtifact`
- `deleteArtifact`

并修正了 `uploadDocument` 的返回类型，避免与浏览器 DOM `Document` 类型撞名。

### 4. 第一版 Notebook Panel UI

新增 `frontend/src/components/NotebookPanel.tsx`，并挂载到 `Workbench` 右侧：

- 显示当前知识库的 Sources
- 显示当前知识库的 Studio Artifacts
- 支持手动创建一个 note 类型 Artifact

在 `frontend/src/store/chat-store.ts` 中新增：

- `sources`
- `artifacts`
- `loadNotebookAssets`
- `createArtifact`

目前这是“可见的骨架”，不是最终 NotebookLM 体验。

## 已验证

### 后端测试

运行命令：

```powershell
$env:PYTHONPATH = (Resolve-Path 'CazzKB\backend').Path
& 'CazzKB\.venv\Scripts\python.exe' -m pytest CazzKB\backend\tests -q
```

结果：

```text
22 passed, 1 xfailed, 1 xpassed, 28 warnings
```

### 前端构建

运行命令：

```powershell
$env:PATH = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;' + $env:PATH
npm --prefix CazzKB\frontend run build
```

结果：

```text
✓ built
```

注意：Vite 仍提示部分 chunk 大于 500KB，这是现有 Mermaid/KaTeX/Cytoscape 等依赖导致，当前不阻塞功能，但后续需要 code splitting。

## 当前已知不足

### 高优先级

1. `Document.enabled` 还没有真正影响检索  
   现在只是数据层和 UI 层有 enabled 字段；聊天检索仍可能搜到所有已索引 chunk。下一轮应在 retrieval/orchestrator 或 search 过滤链路中加入 source allowlist / enabled filter。

2. Sources 还不能删除或重新索引  
   NotebookLM-like 产品需要：
   - 删除 source
   - 替换 source
   - re-index source
   - source 状态：pending / indexing / ready / failed

3. Artifacts 只是存储和展示，还不是 AI 生成  
   下一轮应新增 “generate artifact” API，例如：
   - briefing doc
   - FAQ
   - study guide
   - timeline
   - mind map outline

4. 引用还不够 NotebookLM  
   当前聊天已有 sources 概念，但还缺：
   - 可点击 citation
   - citation 定位到 source chunk
   - source viewer 高亮证据片段

### 中优先级

5. 上传格式过窄  
   当前侧栏只接 `.md,.txt`。应扩展：
   - PDF
   - DOCX
   - HTML/web page
   - YouTube/transcript
   - audio transcript

6. 依赖过重  
   `backend/requirements.txt` 会拉 `FlagEmbedding` / Torch 相关大依赖，安装很慢。建议拆成：
   - `requirements.txt`：最小可运行
   - `requirements-rerank.txt`：可选 reranker
   - `requirements-dev.txt`：测试和开发工具

7. 前端 bundle 偏大  
   Mermaid/KaTeX/Cytoscape 进入主构建包，建议用动态 import 或 manual chunks。

8. 还没有 Notebook 级设置  
   需要支持：
   - 默认回答语言
   - citation 严格度
   - 是否允许无来源回答
   - source selection mode

## 下一轮建议任务

建议按这个顺序继续：

1. 检索过滤：让 disabled sources 不参与回答  
   修改检索链路，给 chunk metadata 加 `document_id/source_id`，并在 query 时过滤 enabled source。

2. Source viewer：点击右侧 source 打开详情  
   用 `GET /api/sources/{source_id}` 展示 chunks，后续 citation 可跳转到具体 chunk。

3. Artifact generation API  
   新增：
   - `POST /api/kb/{kb_id}/artifacts/generate`
   - body: `{ artifact_type, source_ids?, instruction? }`
   - 返回并保存 Artifact。

4. Studio UI  
   在右侧 Studio 区提供按钮：
   - 生成简报
   - 生成 FAQ
   - 生成学习指南
   - 生成时间线
   - 生成思维导图

5. Citation UX  
   在回答中渲染 `[1] [2]`，点击后打开 source chunk，并高亮证据。

6. 依赖拆分和启动文档  
   让新用户能用最小依赖跑起来，把 reranker 作为可选增强。

## 给下一个 Codex 的建议开场

可以直接说：

> 请继续 `C:\Users\Administrator\Documents\ChatGPT\YangCazzV2\CazzKB` 的 `codex/notebooklm-foundation` 分支。先读 `HANDOFF.md`，然后优先实现 “disabled sources 不参与检索” 和 “Source viewer 点击查看 chunks”。注意不要提交 `frontend/tsconfig.tsbuildinfo`，它是构建缓存。

## 操作注意

- 当前项目是嵌套在 `YangCazzV2` 下的独立 Git 仓库。
- `frontend/tsconfig.tsbuildinfo` 会在 `npm run build` 后变化，不建议提交。
- `.venv` 和 `node_modules` 是本地环境产物，不需要提交。
- 后端测试依赖本地 `.venv`，它使用的是 Codex bundled Python 创建的环境。
