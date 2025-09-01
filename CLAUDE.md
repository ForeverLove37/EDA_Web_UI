# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is **Project Phoenix: The Symbiotic Analysis Environment** - a comprehensive, project-based analysis platform with:
- **Frontend**: React + Vite application with Tailwind CSS, React Router, and interactive dashboards
- **Backend**: FastAPI server with SQLAlchemy ORM, authentication, and AI-powered analysis
- **Database**: SQLite (default) with project-based data model
- **AI Integration**: Deepseek and ChatAI API LLM services with proactive insight generation

## Key Components

### Backend Structure
- `backend/main.py`: Main FastAPI application with project-based endpoints
- `backend/models.py`: SQLAlchemy ORM models (User, Project, DataSource, Analysis, Story)
- `backend/schemas.py`: Pydantic models for API request/response validation
- `backend/auth.py`: JWT authentication and user management
- `backend/database.py`: Database connection and session management
- `backend/data_connectors.py`: Universal data connectivity (CSV, Excel, PostgreSQL, MySQL, BigQuery, S3, API, PDF)
- `backend/ai_assistant.py`: AI research assistant with proactive insight generation
- `backend/llm/services.py`: LLM client integration (Deepseek, ChatAI API)

### Frontend Structure
- `frontend/src/App.jsx`: Main application with routing
- `frontend/src/contexts/AuthContext.jsx`: Authentication state management
- `frontend/src/components/Layout/`: Main layout components (Sidebar, Header)
- `frontend/src/components/Auth/`: Login and registration components
- `frontend/src/components/Dashboard/`: Project dashboard
- `frontend/src/components/Project/`: Project-specific components:
  - `ProjectView.jsx`: Main project interface
  - `DataSourceManager.jsx`: Universal data connectivity UI
  - `AnalysisDashboard.jsx`: Interactive analysis dashboard
  - `AIAssistant.jsx`: AI research assistant chat interface
  - `StoryTelling.jsx`: Narrative generation and export

## Development Commands

### Frontend Development
```bash
cd frontend
npm run dev      # Start development server (http://localhost:5173)
npm run build    # Build for production
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload  # Start FastAPI server with auto-reload (http://localhost:8000)
```

### Database Management
```bash
cd backend
python -c "from database import init_db; init_db()"  # Initialize database
```

### Full Stack Development
```bash
docker-compose up --build  # Build and run both services
```

## Environment Variables

Backend requires these environment variables:
- `DATABASE_URL`: Database connection string (default: sqlite:///./phoenix.db)
- `SECRET_KEY`: JWT secret key for authentication
- `DEEPSEEK_API_KEY`: API key for Deepseek LLM service
- `CHATAIAPI_API_KEY`: API key for ChatAI API service

## API Endpoints

### Authentication
- `POST /token`: User login
- `POST /register`: User registration

### Project Management
- `GET /projects`: List user projects
- `POST /projects`: Create new project
- `GET /projects/{project_id}`: Get project details

### Data Sources
- `POST /projects/{project_id}/data-sources`: Connect data source
- `GET /projects/{project_id}/data-sources`: List project data sources

### AI Analysis
- `POST /projects/{project_id}/analyze`: Run AI-powered analysis
- `POST /projects/{project_id}/ask`: Ask natural language questions

### Storytelling
- `POST /projects/{project_id}/stories`: Create data story

## Data Flow

1. User authenticates and creates projects
2. User connects multiple data sources (files, databases, APIs)
3. AI performs "first contact" analysis and data quality assessment
4. User interacts with AI assistant for natural language queries
5. System generates proactive insights and recommendations
6. User creates data stories with AI-generated narratives
7. Stories can be exported to multiple formats (PDF, HTML, PowerPoint)

## Key Features

- **Universal Data Connectivity**: CSV, Excel, JSON, PostgreSQL, MySQL, BigQuery, S3, APIs, PDFs
- **AI-Powered First Contact**: Automated data profiling and quality assessment
- **Proactive Insight Generation**: AI identifies patterns and suggests analyses
- **Natural Language Interface**: Chat-based interaction with data
- **Interactive Dashboard**: Real-time filtering and visualization
- **Storytelling Mode**: AI-generated narratives from insights
- **Multi-Format Export**: PDF, HTML, PowerPoint reports