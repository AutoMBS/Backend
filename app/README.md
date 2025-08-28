# Medical Benefits Schedule (MBS) API

## 📋 Overview

The Medical Benefits Schedule (MBS) API is a comprehensive RESTful service that provides access to medical categories data and AI-powered code suggestions using RAG (Retrieval Augmented Generation) technology. It's designed to assist healthcare professionals with medical billing, coding, and service categorization.

## 🏗️ Architecture

The API follows a modular, service-oriented architecture with clear separation of concerns:

```
API/
├── main.py                 # FastAPI application entry point
├── CRUD.py                 # Database operations and data access
├── rag_service.py          # RAG service for AI-powered search
├── rulebook_service.py     # Medical categories data service
├── routers/                # API route definitions
│   ├── rag.py             # RAG-related endpoints
│   └── rulebook.py        # Medical data endpoints
└── README.md               # This documentation
```

### Core Components

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLite**: Lightweight database for medical categories data
- **Qdrant**: Vector database for semantic search and embeddings
- **Sentence Transformers**: AI models for text embedding and reranking
- **Pydantic**: Data validation and serialization

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Docker (for Qdrant vector database)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Qdrant vector database**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

5. **Start the API server**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 File Structure and Purpose

### `main.py` - Application Entry Point
- **Purpose**: Main FastAPI application configuration and startup
- **Key Features**:
  - Application lifecycle management
  - Service initialization (RAG, Rulebook)
  - Middleware configuration (CORS)
  - Router registration
  - Health monitoring

### `CRUD.py` - Database Operations
- **Purpose**: Centralized database access and operations
- **Key Features**:
  - SQLite connection management
  - Medical categories data retrieval
  - DataFrame and dictionary format support
  - Error handling and validation
  - Support for multiple category tables

### `rag_service.py` - RAG Service
- **Purpose**: AI-powered medical code suggestions
- **Key Features**:
  - Text embedding using Sentence Transformers
  - Vector similarity search in Qdrant
  - AI-powered result reranking
  - Medical criteria filtering
  - Vector database management

### `rulebook_service.py` - Medical Data Service
- **Purpose**: Medical categories data access and management
- **Key Features**:
  - Category data retrieval with pagination
  - Advanced filtering by medical criteria
  - Statistical analysis and reporting
  - Health monitoring and diagnostics
  - Flexible query options

### `routers/rag.py` - RAG API Endpoints
- **Purpose**: RAG-related API route definitions
- **Endpoints**:
  - `POST /MBS/code/suggest`: Generate medical code suggestions
  - `POST /MBS/_internal/rag/buildVectorDb`: Build vector database index

### `routers/rulebook.py` - Medical Data API Endpoints
- **Purpose**: Medical categories data API routes
- **Endpoints**:
  - `GET /`: API information and version
  - `GET /categories`: List all medical categories
  - `GET /categories/{category_id}`: Get category-specific data
  - `GET /health`: Service health check
  - `GET /statistics`: Data statistics
  - `GET /filter`: Generic filtering
  - `GET /category1/filter`: Category 1 specific filtering
  - `GET /category3/filter`: Category 3 specific filtering

## 🌐 API Endpoints Overview

### Rulebook API (Medical Data)
Base URL: `/rulebook`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and version details |
| GET | `/categories` | List all available medical categories |
| GET | `/categories/{category_id}` | Retrieve category-specific data |
| GET | `/health` | Service health check and database connectivity |
| GET | `/statistics` | Comprehensive data statistics |
| GET | `/filter` | Generic filtering by age and time |
| GET | `/category1/filter` | Specialized filtering for category 1 |
| GET | `/category3/filter` | Specialized filtering for category 3 |

### RAG API (AI-Powered Search)
Base URL: `/MBS`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/MBS/code/suggest` | Generate medical code suggestions using RAG |
| POST | `/MBS/_internal/rag/buildVectorDb` | Build/rebuild vector database index |

### LLM Reasoning API (Intelligent Medical Coding)
Base URL: `/reasoning`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reasoning/health` | LLM Reasoning service health check |
| POST | `/reasoning/analyze_candidates` | Analyze medical coding candidates with LLM reasoning |
| POST | `/reasoning/select_best_item` | Select best medical coding item with RAG integration |
| POST | `/reasoning/medical_coding_reasoning` | Professional medical coding reasoning endpoint |

## 🔍 Usage Examples

### Get API Information
```bash
curl http://localhost:8000/rulebook/
```

### List Medical Categories
```bash
curl http://localhost:8000/rulebook/categories
```

### Get Category Data
```bash
curl http://localhost:8000/rulebook/categories/1?limit=10&offset=0
```

### Health Check
```bash
curl http://localhost:8000/rulebook/health
```

### RAG Code Suggestions
```bash
curl -X POST http://localhost:8000/MBS/code/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "free_text": "medical consultation for adult patient",
    "age": 25,
    "provider": "general practitioner",
    "duration": 30
  }'
```

### Build Vector Database
```bash
curl -X POST http://localhost:8000/MBS/_internal/rag/buildVectorDb \
  -H "Content-Type: application/json" \
  -d '{"category_id": "1"}'
```

### LLM Reasoning for Medical Coding

#### Method 1: Analyze Medical Coding Candidates
```bash
curl -X POST http://localhost:8000/reasoning/analyze_candidates \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": "Male with facial and foot injury. HOPC: Cage fell off, struck face, and landed on left foot. No other injuries. Tenderness over right mandible. Bruising over midfoot with significant swelling. Pain with weight bearing. PMH: Hypertension. Meds: Anti-hypertensive. Allergies: Testamental. SH: Lives at home. O/E: GCS 15, Normal eye movement, Pupil size 3, equal and reactive, Mouth opening normal, Bruising over midfoot with significant swelling Pain with weight bearing. Impression: Facial and foot injury. Management Plan: Pain management, CT left foot, CT brain, CT facial bones. Follow-up with investigations review. CT showed medial cuneform avulsion fracture. Treatment Cammbot review by orthopaedic consultant in clinic. Age: 55Y",
    "candidates": [
      {
        "score": 0.229,
        "payload": {
          "category_code": 1,
          "category_name": "Professional Attendance",
          "item_number": 5263,
          "group_name": "A23",
          "subheading_code": 3.0,
          "subheading_mutually_exclusive": 1,
          "service_provider": "medical practitioner (other than a general practitioner)",
          "location": "residential aged care facility or consulting rooms within such a",
          "start_age": 0,
          "end_age": 100,
          "start_time": 20,
          "end_time": 40
        }
      },
      {
        "score": 0.185,
        "payload": {
          "category_code": 1,
          "category_name": "Professional Attendance",
          "item_number": 5012,
          "group_name": "A23",
          "subheading_code": 2.0,
          "subheading_mutually_exclusive": 1,
          "service_provider": "medical practitioner (other than a general practitioner)",
          "location": "consulting rooms",
          "start_age": 4,
          "end_age": 75,
          "start_time": 15,
          "end_time": 30
        }
      }
    ]
  }'
```

#### Method 2: Professional Medical Coding Reasoning
```bash
curl -X POST http://localhost:8000/reasoning/medical_coding_reasoning \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": "Male with facial and foot injury. HOPC: Cage fell off, struck face, and landed on left foot. Age: 55Y. Diagnosis: Facial and foot injury, medial cuneiform avulsion fracture. Management: CT scans, orthopaedic consultation.",
    "candidates": [
      {
        "score": 0.229,
        "payload": {
          "item_number": 5263,
          "category_name": "Professional Attendance",
          "service_provider": "medical practitioner (other than a general practitioner)",
          "location": "consulting rooms",
          "start_age": 0,
          "end_age": 100,
          "start_time": 20,
          "end_time": 40
        }
      }
    ]
  }'
```

#### Method 3: Select Best Item with RAG Integration
```bash
curl -X POST http://localhost:8000/reasoning/select_best_item \
  -H "Content-Type: application/json" \
  -d '{
    "query": "facial and foot injury evaluation",
    "age": 55,
    "provider": "medical practitioner (other than a general practitioner)",
    "duration": 25,
    "location": "consulting rooms",
    "top_n": 3
  }'
```

#### Example Response
```json
{
  "success": true,
  "message": "Successfully analyzed candidate medical coding items",
  "data": {
    "patient_info": "Male with facial and foot injury...",
    "candidates": [...],
    "reasoning_result": {
      "selected_item": {
        "score": 0.229,
        "payload": {
          "item_number": 5263,
          "category_name": "Professional Attendance",
          "service_provider": "medical practitioner (other than a general practitioner)",
          "location": "consulting rooms"
        }
      },
      "selected_item_index": 0,
      "confidence": 0.85,
      "reasoning": "Item 5263 is appropriate for professional attendance by a medical practitioner in consulting rooms. The patient's age (55) falls within the valid range (0-100) and the service provider type matches the requirement.",
      "key_factors": ["age appropriateness", "provider type match", "location suitability"],
      "raw_text": "...",
      "truncated": false,
      "total_candidates": 2
    }
  },
  "timestamp": "2025-01-XX..."
}
```

## 🔄 Complete LLM Reasoning Workflow

### Step 1: Build Vector Database
```bash
# First, build the vector database for medical coding items
curl -X POST http://localhost:8000/MBS/_internal/rag/buildVectorDb \
  -H "Content-Type: application/json" \
  -d '{"category_id": "1"}'
```

### Step 2: RAG Search for Candidates
```bash
# Search for relevant medical coding candidates
curl -X POST http://localhost:8000/MBS/code/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "free_text": "facial and foot injury evaluation",
    "age": 55,
    "provider": "medical practitioner (other than a general practitioner)",
    "duration": 25,
    "location": "consulting rooms"
  }'
```

### Step 3: LLM Reasoning Analysis
```bash
# Use LLM reasoning to select the best medical coding item
curl -X POST http://localhost:8000/reasoning/analyze_candidates \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": "Male with facial and foot injury. HOPC: Cage fell off, struck face, and landed on left foot. Age: 55Y. Diagnosis: Facial and foot injury, medial cuneiform avulsion fracture. Management: CT scans, orthopaedic consultation.",
    "candidates": [
      {
        "score": 0.229,
        "payload": {
          "item_number": 5263,
          "category_name": "Professional Attendance",
          "service_provider": "medical practitioner (other than a general practitioner)",
          "location": "consulting rooms",
          "start_age": 0,
          "end_age": 100
        }
      }
    ]
  }'
```

### Workflow Benefits
- **🎯 Precision**: LLM analyzes clinical relevance, age appropriateness, and provider matching
- **📊 Confidence Scoring**: Provides confidence levels with detailed reasoning
- **🔍 Clinical Justification**: Links patient symptoms, diagnosis, and treatment to coding selection
- **⚡ Efficiency**: Automated reasoning reduces manual coding errors
- **📋 Documentation**: Detailed reasoning process for audit and compliance

## 🗄️ Database Configuration

### SQLite Database
- **Location**: `../data/medical_categories.db`
- **Tables**: `category_1`, `category_3`, etc.
- **Key Fields**: `item_number`, `service_summary`, `start_age`, `end_age`, `start_time`, `end_time`, `service_provider`

### Qdrant Vector Database
- **URL**: `http://localhost:6333`
- **Collection**: `MBS`
- **Purpose**: Store medical service embeddings for semantic search

## 🤖 RAG System Configuration

### AI Models
- **Embedding Model**: `BAAI/bge-m3` (Sentence Transformers)
- **Reranker Model**: `BAAI/bge-reranker-large` (Cross Encoder)
- **Device**: Auto-detects CUDA/CPU

### Vector Database
- **Collection Name**: `MBS`
- **Distance Metric**: Cosine similarity
- **Vector Dimension**: Auto-detected from embedding model

### LLM Reasoning Configuration
- **Service**: Google Cloud Vertex AI
- **Model**: Custom fine-tuned model for medical coding
- **Temperature**: 0.5 (balanced creativity and precision)
- **Max Tokens**: 64,000
- **Authentication**: Service account credentials
- **Features**: 
  - Clinical information analysis
  - Multi-dimensional matching assessment
  - Precise reasoning process
  - English-only output

## 🚨 Error Handling

The API implements comprehensive error handling:

- **HTTP Status Codes**: Standard REST status codes
- **Error Messages**: Descriptive error descriptions
- **Validation**: Input validation using Pydantic models
- **Graceful Degradation**: Continues functioning even if Qdrant is unavailable

## 🔧 Development and Testing

### Code Style
- **Comments**: Comprehensive English documentation
- **Type Hints**: Full type annotation support
- **Docstrings**: Detailed function documentation
- **Error Handling**: Robust exception management

### Testing
```bash
# Test syntax
python -m py_compile main.py
python -m py_compile rag_service.py
python -m py_compile rulebook_service.py
python -m py_compile CRUD.py

# Test API endpoints
curl http://localhost:8000/rulebook/health
```

## 📊 Performance Considerations

- **Vector Search**: Optimized for medical code similarity
- **Database Queries**: Efficient SQLite operations with proper indexing
- **Caching**: Consider Redis for production caching
- **Async Support**: FastAPI async capabilities for high concurrency

## 🔒 Security and Production

### CORS Configuration
- Currently allows all origins (`*`)
- Configure appropriately for production environments

### Database Security
- SQLite file permissions
- Input validation and sanitization
- Rate limiting considerations

### Production Deployment
- Use production ASGI server (Gunicorn + Uvicorn)
- Environment variable configuration
- Logging and monitoring
- Health checks and metrics

## 📝 API Response Format

All API responses follow a standardized format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data payload
  },
  "timestamp": "2025-08-27T20:15:15.338084"
}
```

## 🔄 Version History

- **v2.0.0** (Current): Refactored architecture with modular services
- **v1.0.0**: Initial implementation with monolithic structure

## 📞 Support

For technical support or questions:
- **Team**: Medical Coding Team
- **Email**: coding@medical.org
- **Documentation**: Check API docs at `/docs` endpoint

