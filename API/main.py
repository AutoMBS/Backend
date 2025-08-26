from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# 创建FastAPI应用实例
app = FastAPI(
    title="Medical Categories Data API",
    description="API for accessing medical categories data from SQLite database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接函数
def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect("../data/medical_categories.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")

# 数据模型
class CategoryInfo(BaseModel):
    category_name: str
    record_count: int

class StatisticsResponse(BaseModel):
    total_categories: int
    total_items: int
    categories: List[CategoryInfo]

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str

# 1. 版本及描述信息API
@app.get("/", response_model=ApiResponse)
async def get_api_info():
    """获取API版本和描述信息"""
    return ApiResponse(
        success=True,
        message="Medical Categories Data API",
        data={
            "api_name": "Medical Categories Data API",
            "version": "1.0.0",
            "description": "API for accessing medical categories data from SQLite database",
            "endpoints": {
                "api_info": "/",
                "health_check": "/health",
                "categories": "/categories",
                "category_data": "/categories/{category_id}",
                "statistics": "/statistics"
            },
            "database": "../data/medical_categories.db"
        },
        timestamp=datetime.now().isoformat()
    )

# 2. 查找所有可用的医疗分类
@app.get("/categories", response_model=ApiResponse)
async def get_all_categories():
    """获取所有可用的医疗分类"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 过滤掉系统表，只保留category_开头的表
        categories = []
        for table in tables:
            table_name = table[0]
            if table_name.startswith('category_') and table_name != 'sqlite_sequence':
                # 获取每个分类的记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                categories.append({
                    "category_id": table_name.replace('category_', ''),
                    "category_name": table_name,
                    "record_count": count
                })
        
        conn.close()
        
        return ApiResponse(
            success=True,
            message=f"成功获取 {len(categories)} 个医疗分类",
            data=categories,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")

# 3. 根据category返回所有的行数据
@app.get("/categories/{category_id}", response_model=ApiResponse)
async def get_category_data(category_id: str, limit: Optional[int] = None, offset: int = 0):
    """根据分类ID获取所有行数据，可选择是否限制返回数量"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建表名
        table_name = f"category_{category_id}"
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"分类 {category_id} 不存在")
        
        # 获取数据总数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        # 根据是否指定limit来决定查询方式
        if limit is not None:
            # 如果指定了limit，使用分页查询
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            message = f"成功获取分类 {category_id} 的数据 (分页模式)"
        else:
            # 如果没有指定limit，返回所有数据
            if offset > 0:
                # 如果指定了offset但没有limit，从offset开始返回所有数据
                cursor.execute(f"SELECT * FROM {table_name} LIMIT -1 OFFSET ?", (offset,))
                rows = cursor.fetchall()
                message = f"成功获取分类 {category_id} 的数据 (从第{offset+1}条开始)"
            else:
                # 返回所有数据
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                message = f"成功获取分类 {category_id} 的所有数据"
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)
        
        conn.close()
        
        return ApiResponse(
            success=True,
            message=message,
            data={
                "category_id": category_id,
                "table_name": table_name,
                "total_records": total_count,
                "returned_records": len(data),
                "limit": limit,
                "offset": offset,
                "query_mode": "pagination" if limit is not None else "all_data",
                "records": data
            },
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

# 4. 健康检查
@app.get("/health", response_model=ApiResponse)
async def health_check():
    """健康检查端点"""
    try:
        # 测试数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查数据库是否可访问
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        return ApiResponse(
            success=True,
            message="API服务运行正常",
            data={
                "status": "healthy",
                "database_accessible": True,
                "total_tables": table_count,
                "timestamp": datetime.now().isoformat()
            },
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
@app.get("/statistics", response_model=ApiResponse)
async def get_statistics():
    """获取统计信息：每个category有多少数据，总共有多少item"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 统计每个分类的数据
        categories_stats = []
        total_items = 0
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('category_') and table_name != 'sqlite_sequence':
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_items += count
                    
                    categories_stats.append({
                        "category_id": table_name.replace('category_', ''),
                        "category_name": table_name,
                        "record_count": count
                    })
                except Exception as e:
                    # 如果某个表访问失败，记录错误但继续处理其他表
                    categories_stats.append({
                        "category_id": table_name.replace('category_', ''),
                        "category_name": table_name,
                        "record_count": 0,
                        "error": str(e)
                    })
        
        conn.close()
        
        return ApiResponse(
            success=True,
            message="成功获取统计信息",
            data={
                "total_categories": len(categories_stats),
                "total_items": total_items,
                "categories": categories_stats,
                "summary": {
                    "average_records_per_category": total_items / len(categories_stats) if categories_stats else 0,
                    "largest_category": max(categories_stats, key=lambda x: x['record_count']) if categories_stats else None,
                    "smallest_category": min(categories_stats, key=lambda x: x['record_count']) if categories_stats else None
                }
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# 6. 根据category_id、age、time过滤数据
@app.get("/filter", response_model=ApiResponse)
async def filter_by_age_and_time(
    category_id: str,
    age: Optional[float] = None,
    time: Optional[float] = None,
    limit: Optional[int] = None,
    offset: int = 0
):
    """根据category_id、age、time过滤数据，返回满足条件的项目"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建表名
        table_name = f"category_{category_id}"
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"分类 {category_id} 不支持年龄过滤")
        
        # 获取表结构以确定字段名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # 根据不同的表结构构建查询条件
        where_conditions = []
        query_params = []
        
        # 检查是否有age相关字段并构建年龄过滤条件
        if age is not None:
            if 'start_age' in column_names and 'end_age' in column_names:
                # 年龄在start_age和end_age之间，或者start_age和end_age为NULL（表示无限制）
                where_conditions.append("? >= start_age AND ? <= end_age")
                query_params.extend([age, age])
            else:
                raise HTTPException(status_code=400, detail=f"分类 {category_id} 不支持年龄过滤")
        
        # 检查是否有time相关字段并构建时间过滤条件
        if time is not None:
            if 'start_time' in column_names and 'end_time' in column_names:
                # category_1: 时间在start_time和end_time之间
                where_conditions.append("? >= start_time AND ? <= end_time")
                query_params.extend([time, time])
            elif 'start_duration' in column_names and 'end_duration' in column_names:
                # category_3: 时间在start_duration和end_duration之间
                where_conditions.append("? >= start_duration AND ? <= end_duration")
                query_params.extend([time, time])
            else:
                raise HTTPException(status_code=400, detail=f"分类 {category_id} 不支持时间过滤")
        
        # 构建SQL查询
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
        else:
            # 如果没有过滤条件，返回所有数据
            sql = f"SELECT * FROM {table_name}"
        
        # 添加分页
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            query_params.extend([limit, offset])
        
        # 执行查询
        cursor.execute(sql, query_params)
        rows = cursor.fetchall()
        
        # 获取总记录数（用于分页信息）
        if where_conditions:
            count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
            # 对于计数查询，需要排除分页参数
            count_params = query_params[:-2] if limit is not None else query_params
            cursor.execute(count_sql, count_params)
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        
        total_count = cursor.fetchone()[0]
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)
        
        conn.close()
        
        # 构建响应消息
        filter_desc = []
        if age is not None:
            filter_desc.append(f"年龄={age}")
        if time is not None:
            filter_desc.append(f"时间={time}")
        
        if filter_desc:
            message = f"成功获取分类 {category_id} 中满足条件 ({', '.join(filter_desc)}) 的数据"
        else:
            message = f"成功获取分类 {category_id} 的所有数据"
        
        return ApiResponse(
            success=True,
            message=message,
            data={
                "category_id": category_id,
                "table_name": table_name,
                "filters_applied": {
                    "age": age,
                    "time": time
                },
                "total_records": total_count,
                "returned_records": len(data),
                "records": data
            },
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"过滤数据失败: {str(e)}")

# 7. Category 1 专用API - 支持多个属性过滤
@app.get("/category1/filter", response_model=ApiResponse)
async def filter_category1(
    service_provider: Optional[str] = None,
    location: Optional[str] = None,
    age: Optional[int] = None,
    time: Optional[int] = None,
    restricted_gender: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0
):
    """Category 1 专用过滤API，支持多个属性过滤"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        # 1. Service Provider 过滤
        if service_provider is not None:
            where_conditions.append("service_provider LIKE ?")
            query_params.append(f"%{service_provider}%")
        
        # 2. Location 过滤
        if location is not None:
            where_conditions.append("location LIKE ?")
            query_params.append(f"%{location}%")
        
        # 3. Age 过滤
        if age is not None:
            where_conditions.append("? >= start_age AND ? <= end_age")
            query_params.extend([age, age])
        
        # 4. Time 过滤
        if time is not None:
            where_conditions.append("? >= start_time AND ? <= end_time")
            query_params.extend([time, time])
        
        # 5. Restricted Gender 过滤
        if restricted_gender is not None:
            if restricted_gender.lower() in ['male', 'm', '1']:
                # 查找不允许男性的记录 (restrictions_gender_not_allowed = 1 或包含 'male' 的文本)
                where_conditions.append("(restrictions_gender_not_allowed = 1 OR special_restrictions LIKE '%male%')")
            elif restricted_gender.lower() in ['female', 'f', '2']:
                # 查找不允许女性的记录 (restrictions_gender_not_allowed = 2 或包含 'female' 的文本)
                where_conditions.append("(restrictions_gender_not_allowed = 2 OR special_restrictions LIKE '%female%')")
            else:
                # 查找有性别限制的记录
                where_conditions.append("(restrictions_gender_not_allowed IS NOT NULL OR special_restrictions LIKE '%gender%')")
        
        # 构建SQL查询
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            sql = f"SELECT * FROM category_1 WHERE {where_clause}"
        else:
            # 如果没有过滤条件，返回所有数据
            sql = "SELECT * FROM category_1"
        
        # 添加分页
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            query_params.extend([limit, offset])
        
        # 执行查询
        cursor.execute(sql, query_params)
        rows = cursor.fetchall()
        
        # 获取总记录数（用于分页信息）
        if where_conditions:
            count_sql = f"SELECT COUNT(*) FROM category_1 WHERE {where_clause}"
            # 对于计数查询，需要排除分页参数
            count_params = query_params[:-2] if limit is not None else query_params
            cursor.execute(count_sql, count_params)
        else:
            cursor.execute("SELECT COUNT(*) FROM category_1")
        
        total_count = cursor.fetchone()[0]
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)
        
        conn.close()
        
        # 构建响应消息
        filter_desc = []
        if service_provider is not None:
            filter_desc.append(f"服务提供者={service_provider}")
        if location is not None:
            filter_desc.append(f"地点={location}")
        if age is not None:
            filter_desc.append(f"年龄={age}")
        if time is not None:
            filter_desc.append(f"时间={time}")
        if restricted_gender is not None:
            filter_desc.append(f"性别限制={restricted_gender}")
        
        if filter_desc:
            message = f"成功获取Category 1中满足条件 ({', '.join(filter_desc)}) 的数据"
        else:
            message = "成功获取Category 1的所有数据"
        
        return ApiResponse(
            success=True,
            message=message,
            data={
                "category": "category_1",
                "filters_applied": {
                    "service_provider": service_provider,
                    "location": location,
                    "age": age,
                    "time": time,
                    "restricted_gender": restricted_gender
                },
                "total_records": total_count,
                "returned_records": len(data),
                "limit": limit,
                "offset": offset,
                "query_mode": "filtered" if any([service_provider, location, age, time, restricted_gender]) else "all_data",
                "records": data
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category 1过滤失败: {str(e)}")

# 8. Category 3 专用API - 支持多个属性过滤
@app.get("/category3/filter", response_model=ApiResponse)
async def filter_category3(
    provider: Optional[str] = None,
    treatment_location: Optional[str] = None,
    therapy_type: Optional[str] = None,
    treatment_course: Optional[str] = None,
    age: Optional[float] = None,
    duration: Optional[float] = None,
    limit: Optional[int] = None,
    offset: int = 0
):
    """Category 3 专用过滤API，支持多个属性过滤"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        # 1. Provider 过滤
        if provider is not None:
            where_conditions.append("provider LIKE ?")
            query_params.append(f"%{provider}%")
        
        # 2. Treatment Location 过滤
        if treatment_location is not None:
            where_conditions.append("treatment_location LIKE ?")
            query_params.append(f"%{treatment_location}%")
        
        # 3. Therapy Type 过滤
        if therapy_type is not None:
            where_conditions.append("therapy_type LIKE ?")
            query_params.append(f"%{therapy_type}%")
        
        # 4. Treatment Course 过滤
        if treatment_course is not None:
            where_conditions.append("treatment_course LIKE ?")
            query_params.append(f"%{treatment_course}%")
        
        # 5. Age 过滤
        if age is not None:
            where_conditions.append("? >= start_age AND ? <= end_age")
            query_params.extend([age, age])
        
        # 6. Duration 过滤
        if duration is not None:
            where_conditions.append("? >= start_duration AND ? <= end_duration")
            query_params.extend([duration, duration])
        
        # 构建SQL查询
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            sql = f"SELECT * FROM category_3 WHERE {where_clause}"
        else:
            # 如果没有过滤条件，返回所有数据
            sql = "SELECT * FROM category_3"
        
        # 添加分页
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            query_params.extend([limit, offset])
        
        # 执行查询
        cursor.execute(sql, query_params)
        rows = cursor.fetchall()
        
        # 获取总记录数（用于分页信息）
        if where_conditions:
            count_sql = f"SELECT COUNT(*) FROM category_3 WHERE {where_clause}"
            # 对于计数查询，需要排除分页参数
            count_params = query_params[:-2] if limit is not None else query_params
            cursor.execute(count_sql, count_params)
        else:
            cursor.execute("SELECT COUNT(*) FROM category_3")
        
        total_count = cursor.fetchone()[0]
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)
        
        conn.close()
        
        # 构建响应消息
        filter_desc = []
        if provider is not None:
            filter_desc.append(f"提供者={provider}")
        if treatment_location is not None:
            filter_desc.append(f"治疗地点={treatment_location}")
        if therapy_type is not None:
            filter_desc.append(f"治疗类型={therapy_type}")
        if treatment_course is not None:
            filter_desc.append(f"治疗过程={treatment_course}")
        if age is not None:
            filter_desc.append(f"年龄={age}")
        if duration is not None:
            filter_desc.append(f"持续时间={duration}")
        
        if filter_desc:
            message = f"成功获取Category 3中满足条件 ({', '.join(filter_desc)}) 的数据"
        else:
            message = "成功获取Category 3的所有数据"
        
        return ApiResponse(
            success=True,
            message=message,
            data={
                "category": "category_3",
                "filters_applied": {
                    "provider": provider,
                    "treatment_location": treatment_location,
                    "therapy_type": therapy_type,
                    "treatment_course": treatment_course,
                    "age": age,
                    "duration": duration
                },
                "total_records": total_count,
                "returned_records": len(data),
                "limit": limit,
                "offset": offset,
                "query_mode": "filtered" if any([provider, treatment_location, therapy_type, treatment_course, age, duration]) else "all_data",
                "records": data
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category 3过滤失败: {str(e)}")

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
