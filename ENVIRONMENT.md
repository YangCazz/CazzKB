# Environment — CazzKB

## Backend

```bash
conda create -n cazzkb python=3.11 -y
conda activate cazzkb
cd backend
uv pip install -r requirements.txt
cp .env.example .env   # Add your DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

## Docker

```bash
cd platform/cazz-kb
docker compose up -d    # Backend + Frontend
docker compose --profile ollama up -d  # + Local LLM
```

## Key Dependencies

- Backend: FastAPI, ChromaDB, sentence-transformers, ollama
- Frontend: React 19, TypeScript, Vite, Tailwind CSS
- Optional: Ollama (local embeddings)
```
