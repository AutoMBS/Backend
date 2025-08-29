from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from datetime import datetime
# 使用相对导入
from ..rag_service import RAGService
from ..llm_reasoning_service import LLMReasoningService
from ..llm_extract_service import LLMExtractService

router = APIRouter()

def get_rag(request: Request) -> RAGService:
    return request.app.state.rag 

def get_llm_reasoning(request: Request) -> LLMReasoningService:
    return request.app.state.llm_reasoning

@router.post("/select_best_item",
            summary="LLM reasoning to select best medical coding item",
            description="Use LLM reasoning to select the most appropriate medical coding item based on RAG search results",
            tags=["LLM Reasoning"])
def select_best_item(request: Dict[str, Any], rag: RAGService = Depends(get_rag), llm_reasoning: LLMReasoningService = Depends(get_llm_reasoning), llm_extract_service: LLMExtractService = Depends(get_llm_reasoning)):
    try:
        # Get request parameters
        query = request.get("query", "")
        age = request.get("age")
        operator = request.get("provider")
        duration = request.get("duration")
        location = request.get("location")
        top_n = request.get("top_n", 3)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        # Use RAG search to get candidate medical coding items
        candidates = rag.search(
            query=query,
            age=age,
            operator=operator,
            duration=duration,
            location=location,
            top_n=top_n
        )
        
        if not candidates or isinstance(candidates, dict) and candidates.get("error"):
            return {
                "success": False,
                "message": "RAG search failed or no candidate items found",
                "error": candidates.get("error") if isinstance(candidates, dict) else "No candidate items found",
                "data": {"candidates": [], "selected_item": None}
            }
        
        # Use LLM reasoning to select best medical coding item
        response_complexity = llm_extract_service.predict_complexity(query)
        complexity = response_complexity.get("complexity_level", "")
        query = f"{query} [Complexity: {complexity}]"

        print("="*50)
        print("query with complexity:", query)

        reasoning_result = llm_reasoning.select_best_item(
            patient_info=query,
            candidates=candidates
        )
        
        return {
            "success": True,
            "message": "Successfully selected best medical coding item",
            "data": {
                "query": query,
                "candidates": candidates,
                "reasoning_result": reasoning_result
            },
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning selection failed: {str(e)}")

@router.post("/analyze_candidates",
            summary="LLM analysis of medical coding candidates",
            description="Use LLM to analyze RAG returned medical coding candidates and provide detailed reasoning",
            tags=["LLM Reasoning"])
def analyze_candidates(request: Dict[str, Any], llm_reasoning: LLMReasoningService = Depends(get_llm_reasoning)):
    try:
        # Get request parameters
        patient_info = request.get("patient_info", "")
        candidates = request.get("candidates", [])
        
        if not patient_info:
            raise HTTPException(status_code=400, detail="Patient information cannot be empty")
        
        if not candidates:
            raise HTTPException(status_code=400, detail="Candidate medical coding items list cannot be empty")
        
        # Use LLM reasoning to analyze candidate medical coding items
        reasoning_result = llm_reasoning.select_best_item(
            patient_info=patient_info,
            candidates=candidates
        )
        
        return {
            "success": True,
            "message": "Successfully analyzed candidate medical coding items",
            "data": {
                "patient_info": patient_info,
                "candidates": candidates,
                "reasoning_result": reasoning_result
            },
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis of candidate items failed: {str(e)}")

@router.post("/medical_coding_reasoning",
            summary="Professional medical coding reasoning",
            description="Specialized reasoning endpoint for medical coding scenarios with patient clinical information",
            tags=["LLM Reasoning", "Medical Coding"])
def medical_coding_reasoning(request: Dict[str, Any], llm_reasoning: LLMReasoningService = Depends(get_llm_reasoning)):
    try:
        # Get medical coding reasoning parameters
        patient_info = request.get("patient_info", "")
        candidates = request.get("candidates", [])
        
        if not patient_info:
            raise HTTPException(status_code=400, detail="Patient information cannot be empty")
        
        if not candidates:
            raise HTTPException(status_code=400, detail="Candidate medical coding items list cannot be empty")
        
        # Use LLM reasoning for medical coding selection
        reasoning_result = llm_reasoning.select_best_item(
            patient_info=patient_info,
            candidates=candidates
        )
        
        return {
            "success": True,
            "message": "Medical coding reasoning completed",
            "data": {
                "patient_info": patient_info,
                "candidates": candidates,
                "reasoning_result": reasoning_result
            },
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medical coding reasoning failed: {str(e)}")

@router.get("/health",
            summary="LLM Reasoning service health check",
            description="Check the health status of LLM Reasoning service",
            tags=["LLM Reasoning"])
def health_check():
    return {
        "service": "LLM Reasoning Service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": [
            "Medical coding intelligent reasoning",
            "Clinical information analysis",
            "Multi-dimensional matching assessment",
            "Precise reasoning process"
        ]
    }
