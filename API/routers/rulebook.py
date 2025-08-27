"""
Medical Categories Rulebook API Router
======================================

This module defines the FastAPI routes for medical categories data access.
It provides comprehensive endpoints for querying, filtering, and analyzing
medical billing codes and service information.

Key Endpoints:
- GET /: API information and version details
- GET /categories: List all available medical categories
- GET /categories/{category_id}: Retrieve category-specific data
- GET /health: Service health check and database connectivity
- GET /statistics: Comprehensive data statistics
- POST /filter: Generic filtering by age and time
- POST /category1/filter: Specialized filtering for category 1
- POST /category3/filter: Specialized filtering for category 3

Features:
- Flexible data pagination and filtering
- Medical criteria-based filtering (age, time, provider)
- Comprehensive error handling and validation
- Standardized API response format
- Health monitoring and diagnostics

Author: Medical Coding Team
Version: 2.0.0
Last Updated: 2025-08-27
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Use absolute imports to avoid package import issues
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rulebook_service import RulebookService


# =============================================================================
# ROUTER INSTANCE
# =============================================================================

router = APIRouter()


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_rulebook(request: Request) -> RulebookService:
    """
    Dependency function to retrieve RulebookService instance from application state.
    
    This function extracts the RulebookService instance that was initialized
    during application startup and makes it available to route handlers.
    
    Args:
        request (Request): FastAPI request object containing application state
        
    Returns:
        RulebookService: Initialized rulebook service instance
        
    Raises:
        HTTPException: If rulebook service is not available in application state
        
    Note:
        This dependency ensures that all rulebook endpoints have access to the
        same service instance with proper initialization.
    """
    rulebook_service = request.app.state.rulebook
    
    if not rulebook_service:
        raise HTTPException(
            status_code=500,
            detail="Rulebook service not available. Please check service initialization."
        )
    
    return rulebook_service

# =============================================================================
# DATA MODELS (Pydantic BaseModels)
# =============================================================================

class CategoryInfo(BaseModel):
    """
    Medical category information model.
    
    This model represents basic information about a medical category
    including its name and record count.
    
    Attributes:
        category_name (str): Name of the medical category (e.g., "category_1")
        record_count (int): Number of records in this category
    """
    category_name: str
    record_count: int


class StatisticsResponse(BaseModel):
    """
    Comprehensive statistics response model.
    
    This model provides aggregated statistics about all medical categories
    including total counts and per-category breakdowns.
    
    Attributes:
        total_categories (int): Total number of available categories
        total_items (int): Total number of medical items across all categories
        categories (List[CategoryInfo]): Detailed information for each category
    """
    total_categories: int
    total_items: int
    categories: List[CategoryInfo]


class ApiResponse(BaseModel):
    """
    Standardized API response model.
    
    This model provides a consistent response format across all endpoints
    with success status, message, data payload, and timestamp.
    
    Attributes:
        success (bool): Operation success status
        message (str): Human-readable response message
        data (Optional[Any]): Response data payload (can be any type)
        timestamp (str): ISO format timestamp of response generation
    """
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str

# =============================================================================
# API INFORMATION ENDPOINT
# =============================================================================

@router.get("/", 
            response_model=ApiResponse,
            summary="API Information and Version",
            description="""
            Get comprehensive information about the Medical Categories Data API.
            
            This endpoint provides version details, available endpoints,
            and general information about the API capabilities.
            
            **Information Provided:**
            - API name and version
            - Description and purpose
            - Available endpoints with descriptions
            - Database configuration details
            - Service status and capabilities
            """,
            tags=["rulebook"],
            response_description="API information and endpoint details")
async def get_api_info():
    """
    Retrieve API information and version details.
    
    This endpoint provides comprehensive information about the Medical
    Categories Data API including available endpoints, version information,
    and service capabilities.
    
    Returns:
        ApiResponse: Standardized response containing:
            - success (bool): Always True for this endpoint
            - message (str): API description
            - data (Dict): Detailed API information
            - timestamp (str): ISO format timestamp
            
    Example Response:
        {
            "success": true,
            "message": "Medical Categories Data API",
            "data": {
                "api_name": "Medical Categories Data API",
                "version": "2.0.0",
                "description": "Comprehensive API for medical categories data access",
                "endpoints": {...},
                "database": "../data/medical_categories.db"
            },
            "timestamp": "2025-08-27T20:15:15.338084"
        }
    """
    return ApiResponse(
        success=True,
        message="Medical Categories Data API v2.0.0",
        data={
            "api_name": "Medical Categories Data API",
            "version": "2.0.0",
            "description": "Comprehensive API for accessing medical categories data from SQLite database with advanced filtering and analysis capabilities",
            "endpoints": {
                "api_info": "/",
                "health_check": "/health",
                "categories": "/categories",
                "category_data": "/categories/{category_id}",
                "statistics": "/statistics",
                "filter": "/filter",
                "category1_filter": "/category1/filter",
                "category3_filter": "/category3/filter"
            },
            "database": "../data/medical_categories.db",
            "features": [
                "Medical categories data access",
                "Advanced filtering by age, time, and provider",
                "Pagination and offset support",
                "Health monitoring and diagnostics",
                "Comprehensive statistics and reporting"
            ]
        },
        timestamp=datetime.now().isoformat()
    )

# 2. 查找所有可用的医疗分类
@router.get("/categories", response_model=ApiResponse)
async def get_all_categories(rulebook: RulebookService = Depends(get_rulebook)):
    """获取所有可用的医疗分类"""
    try:
        categories = rulebook.get_all_categories()
        return ApiResponse(
            success=True,
            message=f"成功获取 {len(categories)} 个医疗分类",
            data=categories,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")

# 3. 根据category返回所有的行数据
@router.get("/categories/{category_id}", response_model=ApiResponse)
async def get_category_data(
    category_id: str, 
    limit: Optional[int] = None, 
    offset: int = 0,
    rulebook: RulebookService = Depends(get_rulebook)
):
    """根据分类ID获取所有行数据，可选择是否限制返回数量"""
    try:
        result = rulebook.get_category_data(category_id, limit, offset)
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

# 4. 健康检查
@router.get("/health", response_model=ApiResponse)
async def health_check(rulebook: RulebookService = Depends(get_rulebook)):
    """健康检查端点"""
    try:
        health_data = rulebook.health_check()
        if health_data["status"] == "healthy":
            return ApiResponse(
                success=True,
                message="API服务运行正常",
                data=health_data,
                timestamp=datetime.now().isoformat()
            )
        else:
            return ApiResponse(
                success=False,
                message="API服务异常",
                data=health_data,
                timestamp=datetime.now().isoformat()
            )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="API服务异常",
            data={
                "status": "unhealthy",
                "database_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat()
        )

# 5. 返回统计信息
@router.get("/statistics", response_model=ApiResponse)
async def get_statistics(rulebook: RulebookService = Depends(get_rulebook)):
    """获取统计信息：每个category有多少数据，总共有多少item"""
    try:
        stats_data = rulebook.get_statistics()
        return ApiResponse(
            success=True,
            message="成功获取统计信息",
            data=stats_data,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# 6. 根据category_id、age、time过滤数据
@router.get("/filter", response_model=ApiResponse)
async def filter_by_age_and_time(
    category_id: str,
    age: Optional[float] = None,
    time: Optional[float] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    rulebook: RulebookService = Depends(get_rulebook)
):
    """根据category_id、age、time过滤数据，返回满足条件的项目"""
    try:
        result = rulebook.filter_by_age_and_time(category_id, age, time, limit, offset)
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"过滤数据失败: {str(e)}")

# 7. Category 1 专用API - 支持多个属性过滤
@router.get("/category1/filter", response_model=ApiResponse)
async def filter_category1(
    service_provider: Optional[str] = None,
    location: Optional[str] = None,
    age: Optional[int] = None,
    time: Optional[int] = None,
    restricted_gender: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    rulebook: RulebookService = Depends(get_rulebook)
):
    """Category 1 专用过滤API，支持多个属性过滤"""
    try:
        result = rulebook.filter_category1(
            service_provider, location, age, time, restricted_gender, limit, offset
        )
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category 1过滤失败: {str(e)}")

# 8. Category 3 专用API - 支持多个属性过滤
@router.get("/category3/filter", response_model=ApiResponse)
async def filter_category3(
    provider: Optional[str] = None,
    treatment_location: Optional[str] = None,
    therapy_type: Optional[str] = None,
    treatment_course: Optional[str] = None,
    age: Optional[float] = None,
    duration: Optional[float] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    rulebook: RulebookService = Depends(get_rulebook)
):
    """Category 3 专用过滤API，支持多个属性过滤"""
    try:
        result = rulebook.filter_category3(
            provider, treatment_location, therapy_type, treatment_course, age, duration, limit, offset
        )
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category 3过滤失败: {str(e)}")
