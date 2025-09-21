# architecture.md
# Architecture Documentation

## Overview

The Code Quality Intelligence Agent is a comprehensive system designed to analyze code repositories and provide intelligent insights about code quality, security vulnerabilities, and maintainability issues.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │    │   (FastAPI)     │    │   Services      │
│                 │    │                 │    │                 │
│ - Web UI        │◄──►│ - REST API      │◄──►│ - Gemini AI     │
│ - Dashboard     │    │ - Analysis      │    │ - GitHub API    │
│ - Q&A Interface │    │ - RAG Engine    │    │ - Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Databases     │
                       │                 │
                       │ - MongoDB       │
                       │ - FAISS Index   │
                       └─────────────────┘
```

## Component Details

### Frontend (React)
- **Technology**: React 18, Material-UI, TypeScript
- **Responsibilities**:
  - User interface for code analysis
  - Real-time progress tracking
  - Interactive reports and dashboards
  - Q&A interface with AI assistant
- **Key Features**:
  - Responsive design
  - Dark theme
  - Real-time updates via WebSocket
  - Rich data visualizations

### Backend (FastAPI)
- **Technology**: Python 3.11, FastAPI, asyncio
- **Responsibilities**:
  - RESTful API endpoints
  - Code analysis orchestration
  - AI integration and processing
  - Data storage and retrieval

#### Core Modules

1. **Analysis Engine** (`app/core/analyzer.py`)
   - Main orchestrator for code analysis
   - Multi-language support
   - Pattern-based issue detection
   - AI-powered analysis integration

2. **AST Parser** (`app/core/ast_parser.py`)
   - Abstract Syntax Tree analysis
   - Deep structural code understanding
   - Language-specific parsing
   - Complex pattern detection

3. **RAG Engine** (`app/core/rag_engine.py`)
   - Retrieval-Augmented Generation
   - Vector similarity search
   - Context-aware responses
   - Semantic code understanding

4. **Severity Scorer** (`app/core/severity_scorer.py`)
   - Automated issue prioritization
   - Impact assessment
   - Risk scoring algorithms
   - Business logic for severity assignment

### Databases

#### MongoDB
- **Purpose**: Primary data storage
- **Schema**:
  ```json
  {
    "report_id": "string",
    "status": "enum",
    "source_info": "object",
    "metrics": "object",
    "issues": "array",
    "file_metrics": "array",
    "created_at": "datetime",
    "completed_at": "datetime"
  }
  ```

#### FAISS Vector Database
- **Purpose**: Semantic search and RAG
- **Data**: Code embeddings, issue vectors
- **Operations**: Similarity search, context retrieval

### External Integrations

1. **Google Gemini AI**
   - Advanced code analysis
   - Natural language processing
   - Q&A response generation

2. **GitHub API**
   - Repository cloning
   - Metadata extraction
   - PR review integration (future)

## Data Flow

### Analysis Workflow
```
User Request → Source Validation → File Discovery → 
Language Detection → Pattern Analysis → AST Parsing → 
AI Analysis → Issue Scoring → Report Generation → 
Vector Indexing → Storage → Response
```

### Q&A Workflow  
```
User Question → Context Retrieval (RAG) → 
Analysis Data Lookup → AI Processing → 
Response Generation → Context Attribution
```

## Scalability Considerations

### Performance Optimizations
- Async processing for I/O operations
- Parallel file analysis
- Efficient vector operations with FAISS
- Database query optimization with indexes

### Scaling Strategies
- Horizontal scaling with load balancers
- Analysis queue with background workers
- Distributed vector database
- CDN for static assets

## Security Architecture

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF tokens

### API Security
- Rate limiting
- Authentication/authorization
- API key management
- Request/response validation

### Infrastructure Security
- Container security scanning
- Network segmentation
- SSL/TLS encryption
- Secrets management

## Deployment Architecture

### Development
```
Local Machine:
├── MongoDB (Docker)
├── Backend (Python venv)
└── Frontend (npm dev server)
```

### Production
```
Docker Compose/Kubernetes:
├── Load Balancer (Nginx)
├── Frontend Container(s)
├── Backend Container(s)
├── MongoDB Cluster
└── Monitoring Stack
```

## API Design

### RESTful Endpoints
- `POST /api/v1/analyze` - Start analysis
- `GET /api/v1/analyze/{id}/status` - Check status
- `GET /api/v1/report/{id}` - Get report
- `POST /api/v1/ask` - Q&A endpoint

### Response Format
```json
{
  "status": "success|error",
  "data": {...},
  "message": "string",
  "timestamp": "iso_datetime"
}
```

## Monitoring and Observability

### Metrics
- Request/response times
- Analysis completion rates
- Error rates by endpoint
- Resource utilization

### Logging
- Structured JSON logging
- Correlation IDs
- Error tracking with Sentry
- Audit trails

### Health Checks
- Database connectivity
- External API availability  
- Service dependencies
- Resource health

## Future Enhancements

### Planned Features
1. **GitHub App Integration**
   - Automated PR reviews
   - Commit status checks
   - Repository webhooks

2. **Enhanced AI Capabilities**
   - Code generation suggestions
   - Automated fix recommendations
   - Learning from user feedback

3. **Advanced Analytics**
   - Quality trends over time
   - Team performance metrics
   - Comparative analysis

4. **Enterprise Features**
   - SSO integration
   - Custom rules engine
   - Advanced reporting
   - Multi-tenant support