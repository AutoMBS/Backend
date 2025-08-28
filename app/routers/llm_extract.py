# routers/llm_extract.py
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
# 使用相对导入
from ..llm_extract_service import LLMExtractService

router = APIRouter(tags=["LLM Extract"])

def get_llm(request: Request) -> LLMExtractService:
    svc = getattr(request.app.state, "llm_extract", None)
    if svc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="LLMExtract service not initialized")
    return svc

# ---------- I/O Schemas ----------

class LLMExtractRequest(BaseModel):
    note: str = Field(..., description="原始临床笔记/自由文本")

class PredictResult(BaseModel):
    complexity_level: str = Field(..., description="Ordinary complexity|Complexity that is more than ordinary but not high|High complexity")
    reasoning: str = Field("", description="简要理由")
    raw_text: str = Field("", description="模型原始输出(用于审计/调试)")

class LLMExtractResponse(BaseModel):
    predict_result: PredictResult
    timestamp: str

# ---------- Route ----------

@router.post(
    "/extract",
    summary="复杂度判定",
    description="把 note 发到 Vertex AI Endpoint，请求判定 complexity level。",
    response_model=LLMExtractResponse,
)
def llm_extract(payload: LLMExtractRequest, llm: LLMExtractService = Depends(get_llm)):
    try:
        result: Dict[str, Any] = llm.predict_complexity(payload.note)
        return LLMExtractResponse(
            predict_result=PredictResult(**result),
            timestamp=datetime.now().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 提取失败: {e}")