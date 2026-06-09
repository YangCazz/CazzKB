from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from app.api.deps import get_kb_manager
from app.kb_manager.manager import KBManager

router = APIRouter(prefix="/api")


class CreateKBRequest(BaseModel):
    name: str
    description: str = ""


class ChatRequest(BaseModel):
    query: str
    conversation_id: int | None = None


@router.post("/kb")
def create_kb(req: CreateKBRequest, manager: KBManager = Depends(get_kb_manager)):
    kb = manager.create_kb(name=req.name, description=req.description)
    return {"id": kb.id, "name": kb.name, "description": kb.description}


@router.get("/kb")
def list_kbs(manager: KBManager = Depends(get_kb_manager)):
    kbs = manager.list_kbs()
    return [{"id": kb.id, "name": kb.name, "description": kb.description,
             "chunk_count": kb.chunk_count, "created_at": kb.created_at.isoformat()}
            for kb in kbs]


@router.get("/kb/{kb_id}")
def get_kb(kb_id: int, manager: KBManager = Depends(get_kb_manager)):
    try:
        kb = manager.get_kb(kb_id)
        return {"id": kb.id, "name": kb.name, "description": kb.description,
                "chunk_count": kb.chunk_count, "created_at": kb.created_at.isoformat()}
    except Exception:
        raise HTTPException(status_code=404, detail="Knowledge base not found")


@router.delete("/kb/{kb_id}")
def delete_kb(kb_id: int, manager: KBManager = Depends(get_kb_manager)):
    try:
        manager.delete_kb(kb_id)
        return {"status": "deleted"}
    except Exception:
        raise HTTPException(status_code=404, detail="Knowledge base not found")


@router.post("/kb/{kb_id}/upload")
async def upload_document(kb_id: int, file: UploadFile = File(...),
                          manager: KBManager = Depends(get_kb_manager)):
    content = await file.read()
    doc = manager.ingest_document(kb_id, file.filename, content)
    return {"id": doc.id, "filename": doc.filename, "title": doc.title,
            "chunk_count": doc.chunk_count}


@router.get("/kb/{kb_id}/chunks")
def list_chunks(kb_id: int, offset: int = 0, limit: int = 50,
                manager: KBManager = Depends(get_kb_manager)):
    return manager.get_chunks(kb_id, offset, limit)


@router.post("/kb/{kb_id}/chat")
async def chat(kb_id: int, req: ChatRequest,
               manager: KBManager = Depends(get_kb_manager)):
    async def event_stream():
        for event in manager.chat(kb_id, req.query, req.conversation_id):
            yield f"data: {event}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/kb/{kb_id}/conversations")
def list_conversations(kb_id: int, manager: KBManager = Depends(get_kb_manager)):
    return manager.list_conversations(kb_id)


@router.get("/conversations/{conv_id}")
def get_conversation(conv_id: int, manager: KBManager = Depends(get_kb_manager)):
    conv = manager.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: int, manager: KBManager = Depends(get_kb_manager)):
    manager.delete_conversation(conv_id)
    return {"status": "deleted"}


class RenameRequest(BaseModel):
    title: str


@router.patch("/conversations/{conv_id}")
def rename_conversation(conv_id: int, req: RenameRequest, manager: KBManager = Depends(get_kb_manager)):
    manager.rename_conversation(conv_id, req.title)
    return {"status": "ok"}
