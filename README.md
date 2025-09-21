
# 🚀 Code Quality Intelligence Agent

> AI-powered code analysis platform that provides comprehensive quality assessment, security vulnerability detection, and intelligent insights for your codebase.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## ✨ Features

### 🎯 Core Capabilities
- **🔍 Multi-Language Analysis**: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP
- **🤖 AI-Powered Insights**: Advanced analysis using Google Gemini AI
- **💬 Interactive Q&A**: Natural language queries about your codebase
- **📊 Rich Reports**: Comprehensive dashboards with actionable recommendations
- **🔗 GitHub Integration**: Direct repository analysis from GitHub URLs

### 🛡️ Analysis Categories
- **Security**: Vulnerability detection, injection flaws, authentication issues
- **Performance**: Bottlenecks, inefficient algorithms, resource optimization
- **Code Quality**: Duplication, complexity, naming conventions
- **Maintainability**: Technical debt, documentation, test coverage
- **Best Practices**: Language-specific patterns and conventions

### 🔧 Advanced Technology
- **AST Parsing**: Deep structural code analysis
- **RAG Engine**: Vector-based intelligent responses using FAISS
- **Severity Scoring**: Automated issue prioritization
- **Real-time Updates**: Live analysis progress tracking

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd code-quality-intelligence-agent

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Manual Setup
```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start development servers
make dev
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- MongoDB 7.0+

### Environment Configuration
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional but recommended  
GITHUB_TOKEN=your_github_token_here
```

### Step-by-Step Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

3. **Database Setup**
```bash
# Using Docker
docker run -d --name mongodb -p 27017:27017 mongo:7.0

# Or install MongoDB locally
```

4. **Start Services**
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend  
cd frontend && npm start
```

## 💻 Usage

### Web Interface

1. **📁 Upload/Connect Code**
   - Upload zip/tar archives
   - Connect GitHub repositories
   - Select analysis options

2. **⚡ Run Analysis**
   - Real-time progress tracking
   - Multi-language detection
   - Comprehensive scanning

3. **📊 Review Results**
   - Quality scores and metrics
   - Issue categorization
   - Actionable recommendations

4. **💬 Ask Questions**
   - Natural language queries
   - Context-aware responses
   - Source attribution

### CLI Usage

```bash
# Analyze local directory
python -m app.cli analyze /path/to/code

# Analyze GitHub repository
python -m app.cli analyze https://github.com/user/repo

# Interactive Q&A
python -m app.cli qa --report-id abc123

# Export reports
python -m app.cli export abc123 --format json

# Health check
python -m app.cli health
```

### API Usage

```bash
# Start analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "source_type=github" \
  -F "source_path=https://github.com/user/repo"

# Check status
curl http://localhost:8000/api/v1/analyze/{report_id}/status

# Ask questions
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the security issues?"}'
```

## 🏗️ Architecture

```mermaid
graph TB
    A[Frontend React] --> B[FastAPI Backend]
    B --> C[Analysis Engine]
    B --> D[RAG Engine]
    B --> E[MongoDB]
    B --> F[FAISS Vector DB]
    B --> G[Gemini AI]
    C --> H[AST Parser]
    C --> I[Pattern Matcher]
    C --> J[Severity Scorer]
```

### Key Components
- **Analysis Engine**: Core code processing and issue detection
- **AST Parser**: Deep structural analysis for supported languages
- **RAG Engine**: Vector-based retrieval for intelligent Q&A
- **Severity Scorer**: Automated risk assessment and prioritization

## 🧪 Testing

```bash
# Run all tests
make test

# Backend only
cd backend && pytest tests/ -v --cov=app

# Frontend only  
cd frontend && npm test

# Integration tests
pytest tests/integration/ -v -m integration
```

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Start code analysis |
| GET | `/api/v1/analyze/{id}/status` | Get analysis status |
| GET | `/api/v1/report/{id}` | Retrieve analysis report |
| POST | `/api/v1/ask` | Ask questions about code |

## 🚢 Deployment

### Production Deployment
```bash
# Build and deploy
./scripts/deploy.sh production

# Or using Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install pre-commit hooks
pre-commit install

# Format code
make format

# Run lints
make lint
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced code analysis
- **FAISS** for efficient vector similarity search
- **FastAPI** for the robust backend framework
- **React & Material-UI** for the modern frontend
- **MongoDB** for flexible data storage

---

**Built with ❤️ for developers who care about code quality**

*Need help? Check our [documentation](./docs/) or open an [issue](../../issues)*






































































# Code Quality Intelligence Agent

AI-powered code analysis tool that provides comprehensive quality assessment, security vulnerability detection, and actionable insights for your codebase.

## Features

### Core Features ✅
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C, C#, Ruby, PHP
- **Comprehensive Analysis**: Security, Performance, Code Quality, Maintainability, Testing, Documentation
- **AI-Powered Insights**: Advanced analysis using Google's Gemini AI
- **Interactive Q&A**: Ask natural language questions about your codebase
- **GitHub Integration**: Analyze repositories directly from GitHub URLs

### Advanced Features ✅
- **AST Parsing**: Deep structural code analysis
- **RAG Engine**: Retrieval-Augmented Generation for intelligent responses
- **Severity Scoring**: Automated issue prioritization
- **Vector Database**: FAISS-powered similarity search
- **Real-time Progress**: Live analysis status updates
- **Detailed Reports**: Comprehensive quality reports with visualizations

## Architecture

### Backend (FastAPI)
- **Analysis Engine**: Core code quality analyzer with AI integration
- **AST Parser**: Advanced structural analysis for supported languages  
- **RAG Engine**: Vector-based retrieval system using FAISS and Sentence Transformers
- **Severity Scorer**: Intelligent issue prioritization system
- **Services**: Analysis, GitHub integration, Q&A, and vector operations
- **Database**: MongoDB for analysis results, FAISS for vector search

### Frontend (React)
- **Modern UI**: Material-UI with dark theme
- **Real-time Updates**: Live analysis progress tracking
- **Interactive Reports**: Rich visualizations and detailed issue breakdown
- **Q&A Interface**: Conversational AI assistant
- **Responsive Design**: Works on desktop and mobile

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- MongoDB 7.0+
- Git

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
GITHUB_TOKEN=your_github_token_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=code_quality_db
```

### Method 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone 
cd code-quality-intelligence-agent
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Method 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start MongoDB (if not using Docker)
mongod --dbpath ./data/db

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### CLI Usage

The CLI tool provides direct access to analysis capabilities:

```bash
# Install CLI dependencies
cd backend
pip install -r requirements.txt

# Analyze local directory
python -m app.cli analyze /path/to/your/code

# Analyze GitHub repository
python -m app.cli analyze https://github.com/user/repo

# Advanced options
python -m app.cli analyze /path/to/code \
  --languages python,javascript \
  --exclude "*.test.js,__pycache__" \
  --output-format json \
  --output-file report.json
```

## API Documentation

### Analysis Endpoints

#### Start Analysis
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

{
  "source_type": "github|upload|local",
  "source_path": "path_or_url",
  "languages": "python,javascript", // optional
  "include_tests": true,
  "exclude_patterns": "*.test.js"    // optional
}
```

#### Get Analysis Status
```http
GET /api/v1/analyze/{report_id}/status
```

#### Cancel Analysis
```http
DELETE /api/v1/analyze/{report_id}
```

### Reports Endpoints

#### Get Report
```http
GET /api/v1/report/{report_id}?detailed=true
```

### Q&A Endpoints

#### Ask Question
```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "What are the security issues?",
  "report_id": "optional_report_id",
  "context": {}  // optional
}
```

## Usage Examples

### Web Interface

1. **Upload or Connect Repository**
   - Choose GitHub URL or upload archive
   - Select languages to analyze
   - Configure analysis options

2. **Monitor Progress**
   - Real-time status updates
   - Progress tracking
   - Cancel option available

3. **Review Results**
   - Quality scores and metrics
   - Issue breakdown by severity/category
   - Detailed file analysis
   - Actionable recommendations

4. **Ask Questions**
   - Natural language queries
   - Context-aware responses
   - Source attribution

### CLI Examples

```bash
# Basic analysis
python -m app.cli analyze ./my-project

# GitHub repository
python -m app.cli analyze https://github.com/user/repo

# Specific languages only
python -m app.cli analyze ./project --languages python,javascript

# Export detailed report
python -m app.cli analyze ./project --output-format json --output-file detailed-report.json

# Interactive Q&A mode
python -m app.cli qa --report-id abc123
> What are the most critical issues?
> Which files need the most attention?
```

## Supported Languages & Analysis Types

### Languages ✅
- **Python**: Full AST parsing, security patterns, performance analysis
- **JavaScript/TypeScript**: Syntax analysis, best practices, security checks
- **Java**: Basic pattern matching, security vulnerabilities
- **Go**: Performance patterns, code quality checks
- **Rust**: Safety analysis, performance optimization
- **C/C++**: Memory safety, performance bottlenecks
- **C#**: .NET best practices, security patterns
- **Ruby**: Rails security, code quality
- **PHP**: Web security, performance issues

### Analysis Categories ✅

1. **Security Issues**
   - Code injection vulnerabilities
   - Authentication/authorization flaws
   - Data exposure risks
   - Cryptographic weaknesses

2. **Performance Problems**
   - Algorithmic inefficiencies
   - Memory leaks
   - Database query issues
   - Resource usage optimization

3. **Code Quality**
   - Code duplication
   - Complex functions
   - Naming conventions
   - Design patterns

4. **Maintainability**
   - Technical debt
   - Code organization
   - Documentation quality
   - Test coverage

5. **Testing Gaps**
   - Missing unit tests
   - Low coverage areas
   - Test quality issues

6. **Documentation Issues**
   - Missing docstrings
   - Outdated comments
   - API documentation gaps

## Technical Implementation

### Core Technologies
- **Backend**: FastAPI, Python 3.11, asyncio
- **Frontend**: React 18, Material-UI, TypeScript
- **AI**: Google Gemini 1.5 Pro, Sentence Transformers
- **Database**: MongoDB 7.0, FAISS Vector DB
- **Analysis**: Python AST, regex patterns, static analysis
- **DevOps**: Docker, Docker Compose, Nginx

### Key Components

#### 1. Analysis Engine (`app/core/analyzer.py`)
```python
class CodeQualityAnalyzer:
    async def analyze_repository(self, repo_path: str, report_id: str) -> AnalysisResult
    async def _analyze_file(self, file_path: str, repo_root: str) -> tuple[List[CodeIssue], FileMetrics]
    async def _ai_analyze_code(self, content: str, file_path: str, language: str) -> List[CodeIssue]
```

#### 2. AST Parser (`app/core/ast_parser.py`)
```python
class ASTAnalyzer:
    async def analyze(self, content: str, file_path: str, language: str) -> List[CodeIssue]
    # Python AST visitor for deep structural analysis
    class PythonASTVisitor(ast.NodeVisitor)
```

#### 3. RAG Engine (`app/core/rag_engine.py`)
```python
class RAGEngine:
    async def index_analysis_result(self, result: AnalysisResult)
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]
    async def get_relevant_context(self, query: str) -> str
```

#### 4. Severity Scorer (`app/core/severity_scorer.py`)
```python
class SeverityScorer:
    async def calculate_impact_score(self, issue: CodeIssue) -> float
    def prioritize_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]
```

### Data Models

#### Analysis Result
```python
class AnalysisResult(BaseModel):
    report_id: str
    status: AnalysisStatus
    source_info: Dict[str, Any]
    metrics: RepositoryMetrics
    issues: List[CodeIssue]
    file_metrics: List[FileMetrics]
    created_at: datetime
    completed_at: Optional[datetime]
```

#### Code Issue
```python
class CodeIssue(BaseModel):
    id: str
    category: IssueCategory  # security, performance, code_quality, etc.
    severity: IssueSeverity  # critical, high, medium, low, info
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    suggestion: str
    impact_score: float      # 0.0 to 10.0
    confidence: float        # 0.0 to 1.0
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests  
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run integration tests
cd tests
python -m pytest integration/ -v
```

## Deployment

### Production Deployment

1. **Environment Setup**
```bash
# Production environment variables
export GEMINI_API_KEY=your_production_key
export MONGODB_URL=mongodb://user:pass@prod-mongo:27017/db
export ENVIRONMENT=production
```

2. **Docker Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Kubernetes Deployment**
```yaml
# k8s manifests available in ./k8s/
kubectl apply -f k8s/
```

### Performance Considerations

- **MongoDB Indexing**: Optimized queries with proper indexes
- **FAISS Vector DB**: Efficient similarity search for RAG
- **Async Processing**: Non-blocking analysis pipeline  
- **Caching**: Redis for frequently accessed data
- **Load Balancing**: Nginx for frontend, multiple backend instances

### Monitoring & Observability

- **Health Checks**: `/health` endpoint with service status
- **Metrics**: Prometheus integration for performance monitoring
- **Logging**: Structured JSON logging with correlation IDs
- **Error Tracking**: Sentry integration for error monitoring

## Troubleshooting

### Common Issues

1. **Analysis Fails**
   - Check Gemini API key validity
   - Verify file permissions for uploaded content
   - Monitor MongoDB connection status

2. **Slow Performance**
   - Check available memory for FAISS operations
   - Monitor MongoDB query performance
   - Verify network connectivity for GitHub cloning

3. **Q&A Not Working**
   - Confirm FAISS index initialization
   - Check vector database file permissions
   - Verify sentence-transformers model download

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart backend

# Frontend development mode
cd frontend && npm start
```

## Contributing

### Development Setup
```bash
# Pre-commit hooks
pre-commit install

# Code formatting
black backend/app
prettier --write frontend/src

# Type checking
mypy backend/app
```

### Architecture Decisions

1. **FastAPI over Flask**: Better async support, automatic API docs
2. **MongoDB over PostgreSQL**: Flexible schema for analysis results
3. **FAISS over Elasticsearch**: Optimized for vector similarity search
4. **React over Vue**: Rich ecosystem, Material-UI integration
5. **Gemini over OpenAI**: Cost-effective, good code analysis capabilities

## License

MIT License - see LICENSE file for details.

## Changelog

### v1.0.0
- ✅ Core analysis engine with multi-language support
- ✅ AI-powered insights using Gemini 1.5 Pro
- ✅ Interactive web interface with real-time updates  
- ✅ Q&A system with RAG capabilities
- ✅ GitHub integration for repository analysis
- ✅ Docker deployment with MongoDB and FAISS
- ✅ Comprehensive test suite and documentation

---

**Built with ❤️ for developers who care about code quality**