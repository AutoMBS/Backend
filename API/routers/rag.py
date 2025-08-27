from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

def get_rag(request: Request):
    rag = getattr(request.app.state, "rag", None)
    if rag is None:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    return rag

@router.post("/code/suggest", summary="RAG建议", tags=["RAG"])
def suggest_codes(note: Dict[str, Any], rag = Depends(get_rag)):
    try:
        query    = note.get("free_text", "")
        age      = note.get("age")
        operator = note.get("provider")
        duration = note.get("duration")
        candidates = rag.search(query, age=age, operator=operator, duration=duration, top_n=10)
        return {
            "success": True,
            "message": "RAG candidates generated",
            "data": {"candidates": candidates},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 生成失败: {str(e)}")

@router.post("/_internal/rag/buildVectorDb", include_in_schema=False)
def buildVectorDb(rag = Depends(get_rag)):
    try:
        return {"ok": True, "stat": rag.buildVectorDb()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}")
