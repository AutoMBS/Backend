from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from datetime import datetime
# 使用绝对导入避免包导入问题
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_service import RAGService

router = APIRouter()

def get_rag(request: Request) -> RAGService:
    return request.app.state.rag 

@router.post("/code/suggest",
            summary="RAG建议",
            description="基于自然语言查询和过滤条件，使用RAG技术生成医疗Item建议",
            tags=["RAG"])
def suggest_codes(note: Dict[str, Any], rag: RAGService = Depends(get_rag)):
    try:
        query = note.get("free_text", "")
        age = note.get("age")
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
def buildVectorDb(rag: RAGService = Depends(get_rag)):
    try:
        stat = rag.buildVectorDb()
        return {"ok": True, "stat": stat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}")
