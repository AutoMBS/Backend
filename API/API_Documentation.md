# 医疗分类数据 API 使用文档

## 📋 概述

这是一个基于FastAPI构建的医疗分类数据API服务，专门用于访问和查询医疗分类数据库。API提供多种过滤和查询功能，支持医疗服务的分类、筛选和统计。

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
cd API
python main.py
```

### 访问地址
- **API服务**: http://localhost:8000
- **交互式文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## 📊 数据库结构

API连接到 `../data/medical_categories.db` SQLite数据库，包含以下主要表：

- **`category_1`**: 医疗服务提供者相关数据
- **`category_3`**: 治疗类型和过程相关数据

## 🔗 API端点总览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 获取API版本和描述信息 |
| `/health` | GET | 健康检查 |
| `/categories` | GET | 获取所有可用的医疗分类 |
| `/categories/{category_id}` | GET | 根据分类ID获取数据 |
| `/statistics` | GET | 获取统计信息 |
| `/filter` | GET | 通用过滤API（按年龄和时间） |
| `/category1/filter` | GET | Category 1专用过滤API |
| `/category3/filter` | GET | Category 3专用过滤API |

---

## 1. 版本及描述信息 API

### 端点
```
GET /
```

### 描述
获取API版本、描述和所有可用端点信息。

### 响应示例
```json
{
  "success": true,
  "message": "Medical Categories Data API",
  "data": {
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
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 2. 健康检查 API

### 端点
```
GET /health
```

### 描述
检查API服务和数据库连接状态。

### 响应示例
```json
{
  "success": true,
  "message": "API服务运行正常",
  "data": {
    "status": "healthy",
    "database_accessible": true,
    "total_tables": 2,
    "timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 3. 获取所有分类 API

### 端点
```
GET /categories
```

### 描述
获取所有可用的医疗分类及其记录数。

### 响应示例
```json
{
  "success": true,
  "message": "成功获取 2 个医疗分类",
  "data": [
    {
      "category_id": "1",
      "category_name": "category_1",
      "record_count": 1500
    },
    {
      "category_id": "3",
      "category_name": "category_3",
      "record_count": 1200
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 4. 根据分类ID获取数据 API

### 端点
```
GET /categories/{category_id}
```

### 参数
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `category_id` | string | 是 | 分类ID (如: 1, 3) |
| `limit` | integer | 否 | 每页记录数，不传则返回所有数据 |
| `offset` | integer | 否 | 跳过的记录数，默认0 |

### 描述
根据分类ID获取所有行数据，可选择是否限制返回数量。

### 使用示例
```bash
# 获取分类1的所有数据
GET /categories/1

# 获取分类1的前10条数据
GET /categories/1?limit=10

# 获取分类1从第11条开始的数据
GET /categories/1?offset=10

# 分页获取分类1的数据
GET /categories/1?limit=10&offset=0
```

### 响应示例
```json
{
  "success": true,
  "message": "成功获取分类 1 的数据",
  "data": {
    "category_id": "1",
    "table_name": "category_1",
    "total_records": 1500,
    "returned_records": 10,
    "limit": 10,
    "offset": 0,
    "records": [...]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 5. 统计信息 API

### 端点
```
GET /statistics
```

### 描述
获取每个分类的数据量统计和总体统计信息。

### 响应示例
```json
{
  "success": true,
  "message": "成功获取统计信息",
  "data": {
    "total_categories": 2,
    "total_items": 2700,
    "categories": [
      {
        "category_id": "1",
        "category_name": "category_1",
        "record_count": 1500
      },
      {
        "category_id": "3",
        "category_name": "category_3",
        "record_count": 1200
      }
    ],
    "summary": {
      "average_records_per_category": 1350.0,
      "largest_category": {...},
      "smallest_category": {...}
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 6. 通用过滤 API

### 端点
```
GET /filter
```

### 参数
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `category_id` | string | 是 | 分类ID (如: 1, 3) |
| `age` | float | 否 | 年龄值，用于过滤年龄范围 |
| `time` | float | 否 | 时间值，用于过滤时间范围 |
| `limit` | integer | 否 | 限制返回记录数 |
| `offset` | integer | 否 | 跳过的记录数，默认0 |

### 描述
根据category_id、age、time过滤数据，返回满足条件的项目。支持不同表的字段差异。

### 使用示例
```bash
# 按年龄过滤分类1
GET /filter?category_id=1&age=25

# 按时间过滤分类1
GET /filter?category_id=1&time=500

# 组合过滤
GET /filter?category_id=1&age=25&time=500

# 分页过滤
GET /filter?category_id=1&age=25&limit=10&offset=0
```

### 响应示例
```json
{
  "success": true,
  "message": "成功获取分类 1 中满足条件 (年龄=25, 时间=500) 的数据",
  "data": {
    "category_id": "1",
    "table_name": "category_1",
    "filters_applied": {
      "age": 25,
      "time": 500
    },
    "total_records": 150,
    "returned_records": 150,
    "limit": null,
    "offset": 0,
    "records": [...]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 7. Category 1 专用过滤 API

### 端点
```
GET /category1/filter
```

### 参数
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `service_provider` | string | 否 | 服务提供者 (模糊匹配) |
| `location` | string | 否 | 地点 (模糊匹配) |
| `age` | integer | 否 | 年龄 (范围匹配: 0-200) |
| `time` | integer | 否 | 时间 (范围匹配: 0-1000) |
| `restricted_gender` | string | 否 | 性别限制 (male/female) |
| `limit` | integer | 否 | 分页限制 |
| `offset` | integer | 否 | 分页偏移，默认0 |

### 描述
Category 1专用过滤API，支持多个属性过滤，充分利用医疗服务提供者的字段结构。

### 使用示例
```bash
# 按服务提供者过滤
GET /category1/filter?service_provider=general practitioner

# 按地点过滤
GET /category1/filter?location=consulting rooms

# 按年龄过滤
GET /category1/filter?age=25

# 按时间过滤
GET /category1/filter?time=500

# 按性别限制过滤
GET /category1/filter?restricted_gender=male

# 组合过滤
GET /category1/filter?age=25&location=consulting rooms

# 复杂组合过滤
GET /category1/filter?service_provider=general practitioner&age=30&time=1000&limit=5
```

### 响应示例
```json
{
  "success": true,
  "message": "成功获取Category 1中满足条件 (年龄=25, 地点=consulting rooms) 的数据",
  "data": {
    "category": "category_1",
    "filters_applied": {
      "service_provider": null,
      "location": "consulting rooms",
      "age": 25,
      "time": null,
      "restricted_gender": null
    },
    "total_records": 150,
    "returned_records": 150,
    "limit": null,
    "offset": 0,
    "query_mode": "filtered",
    "records": [...]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 8. Category 3 专用过滤 API

### 端点
```
GET /category3/filter
```

### 参数
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `provider` | string | 否 | 提供者 (模糊匹配) |
| `treatment_location` | string | 否 | 治疗地点 (模糊匹配) |
| `therapy_type` | string | 否 | 治疗类型 (模糊匹配) |
| `treatment_course` | string | 否 | 治疗过程 (模糊匹配) |
| `age` | float | 否 | 年龄 (范围匹配: 0.0-200.0) |
| `duration` | float | 否 | 持续时间 (范围匹配: 0.0-1140.0) |
| `limit` | integer | 否 | 分页限制 |
| `offset` | integer | 否 | 分页偏移，默认0 |

### 描述
Category 3专用过滤API，支持多个属性过滤，专门针对治疗类型和过程的查询需求。

### 使用示例
```bash
# 按提供者过滤
GET /category3/filter?provider=medical practitioner

# 按治疗地点过滤
GET /category3/filter?treatment_location=hospital

# 按治疗类型过滤
GET /category3/filter?therapy_type=hyperbaric oxygen therapy

# 按治疗过程过滤
GET /category3/filter?treatment_course=haemodialysis

# 按年龄过滤
GET /category3/filter?age=40.0

# 按持续时间过滤
GET /category3/filter?duration=500.0

# 组合过滤
GET /category3/filter?age=40.0&therapy_type=hyperbaric

# 复杂组合过滤
GET /category3/filter?provider=medical practitioner&treatment_location=hospital&age=50.0&duration=1000.0&limit=5
```

### 响应示例
```json
{
  "success": true,
  "message": "成功获取Category 3中满足条件 (提供者=medical practitioner, 治疗地点=hospital) 的数据",
  "data": {
    "category": "category_3",
    "filters_applied": {
      "provider": "medical practitioner",
      "treatment_location": "hospital",
      "therapy_type": null,
      "treatment_course": null,
      "age": null,
      "duration": null
    },
    "total_records": 25,
    "returned_records": 25,
    "limit": null,
    "offset": 0,
    "query_mode": "filtered",
    "records": [...]
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

## 📊 数据范围说明

### Category 1 数据范围
- **年龄**: 0 到 200 (INTEGER)
- **时间**: 0 到 1000 (INTEGER)

### Category 3 数据范围
- **年龄**: 0.0 到 200.0 (REAL)
- **时间**: 0.0 到 1140.0 (REAL)

---

## 🔍 过滤逻辑说明

### 文本字段过滤
- 使用 `LIKE %value%` 进行模糊匹配
- 支持部分文本搜索

### 数值范围过滤
- 年龄: `age >= start_age AND age <= end_age`
- 时间: `time >= start_time AND time <= end_time`
- 持续时间: `duration >= start_duration AND duration <= end_duration`

### 性别限制过滤 (Category 1)
- `male/m/1`: 查找不允许男性的记录
- `female/f/2`: 查找不允许女性的记录
- 其他值: 查找有性别限制的记录

---

## 📝 响应格式

所有API都返回统一的响应格式：

```json
{
  "success": boolean,        // 操作是否成功
  "message": string,         // 描述性消息
  "data": object,           // 实际数据
  "timestamp": string       // ISO格式时间戳
}
```

### 数据字段说明
- `total_records`: 总记录数
- `returned_records`: 返回的记录数
- `limit`: 分页限制
- `offset`: 分页偏移
- `query_mode`: 查询模式 (filtered/all_data)
- `filters_applied`: 应用的过滤条件
- `records`: 实际数据记录

---

## 🚨 错误处理

### HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `404`: 分类不存在
- `500`: 服务器内部错误

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

---

## 💡 使用建议

### 1. 选择合适的API
- **通用查询**: 使用 `/categories/{id}` 获取分类数据
- **简单过滤**: 使用 `/filter` 按年龄和时间过滤
- **专业过滤**: 使用 `/category1/filter` 或 `/category3/filter`

### 2. 分页使用
- 大数据量查询建议使用分页
- 合理设置 `limit` 值避免响应过慢

### 3. 过滤条件组合
- 可以组合多个过滤条件
- 过滤条件之间是 `AND` 关系

### 4. 数据范围
- 确保过滤参数在数据范围内
- 使用边界值进行测试

---

## 🧪 测试示例

### 使用curl测试
```bash
# 获取API信息
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health

# 获取所有分类
curl http://localhost:8000/categories

# 测试Category 1过滤
curl "http://localhost:8000/category1/filter?age=25&location=consulting rooms"

# 测试Category 3过滤
curl "http://localhost:8000/category3/filter?provider=medical practitioner&age=40.0"
```

### 使用Python requests测试
```python
import requests

base_url = "http://localhost:8000"

# 获取所有分类
response = requests.get(f"{base_url}/categories")
categories = response.json()

# 过滤Category 1数据
response = requests.get(f"{base_url}/category1/filter", params={
    "age": 25,
    "location": "consulting rooms"
})
data = response.json()
```

---

## 📚 更多资源

- **API文档**: http://localhost:8000/docs
- **ReDoc格式**: http://localhost:8000/redoc
- **源码**: `main.py`
- **数据库**: `../data/medical_categories.db`

---

## 🔄 更新日志

### v1.0.0
- 基础API功能
- 分类数据查询
- 统计信息
- 通用过滤功能

### v1.1.0
- 添加Category 1专用过滤API
- 支持服务提供者、地点、年龄、时间、性别限制过滤

### v1.2.0
- 添加Category 3专用过滤API
- 支持提供者、治疗地点、治疗类型、治疗过程、年龄、持续时间过滤

---

## 📄 许可证

本项目遵循项目根目录的许可证规定。
