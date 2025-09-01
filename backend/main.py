from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import json

import models, schemas, auth, database, data_connectors, ai_assistant
from auth import get_current_active_user
from database import get_db, init_db

app = FastAPI(title="Project Phoenix: Symbiotic Analysis Environment", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:6000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Project management endpoints
@app.get("/projects", response_model=List[schemas.Project])
def get_projects(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()

@app.post("/projects", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_project = models.Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/{project_id}", response_model=schemas.ProjectWithDetails)
def get_project(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

# Data source endpoints
@app.post("/projects/{project_id}/data-sources", response_model=schemas.DataSource)
async def create_data_source(
    project_id: int,
    source_type: str = Form(...),
    config: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse config
    try:
        connection_config = json.loads(config)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid config JSON")
    
    # Handle file upload if present
    if file:
        file_content = await file.read()
        if source_type in ['csv', 'excel', 'json', 'pdf']:
            connection_config['file_content'] = file_content
    
    # Connect to data source
    result = await data_connectors.data_connector.connect(source_type, connection_config)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Create data source record
    db_data_source = models.DataSource(
        project_id=project_id,
        name=connection_config.get('name', f'{source_type}_source'),
        type=source_type,
        connection_config=connection_config,
        data_preview=result['data_preview'],
        data_profile=result['data_profile'],
        raw_data=json.dumps(result['raw_data_sample']) if result['raw_data_sample'] else None
    )
    
    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    
    return db_data_source

@app.get("/projects/{project_id}/data-sources", response_model=List[schemas.DataSource])
def get_project_data_sources(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project.data_sources

# AI Analysis endpoints
@app.post("/projects/{project_id}/analyze", response_model=schemas.AnalysisResult)
async def analyze_project_data(
    project_id: int,
    analysis_config: schemas.AnalysisConfig,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify project ownership and get data sources
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project or not project.data_sources:
        raise HTTPException(status_code=404, detail="Project or data sources not found")
    
    # Get data from the first data source (simplified)
    data_source = project.data_sources[0]
    
    # Convert data preview back to DataFrame (simplified)
    # In real implementation, would fetch actual data
    data_sample = pd.DataFrame(data_source.data_preview['sample_data'])
    
    # Run AI analysis
    insights = await ai_assistant.analyze_data(data_sample)
    
    # Save analysis
    db_analysis = models.Analysis(
        project_id=project_id,
        name=analysis_config.name,
        type=analysis_config.analysis_type,
        config=analysis_config.dict(),
        results={"insights": insights},
        insights=insights
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return {
        "analysis_id": db_analysis.id,
        "insights": insights,
        "summary": f"Generated {len(insights)} insights from data analysis"
    }

@app.post("/projects/{project_id}/ask", response_model=schemas.AIResponse)
async def ask_question(
    project_id: int,
    question: schemas.Question,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify project ownership and get data
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project or not project.data_sources:
        raise HTTPException(status_code=404, detail="Project or data sources not found")
    
    data_source = project.data_sources[0]
    data_sample = pd.DataFrame(data_source.data_preview['sample_data'])
    
    # Answer question
    answer = await ai_assistant.answer_question(
        question.question, 
        data_sample, 
        {"project_name": project.name, "data_source": data_source.name}
    )
    
    # Save conversation
    db_conversation = models.AIConversation(
        project_id=project_id,
        message_type="user_query",
        content=question.question,
        metadata=answer
    )
    
    db.add(db_conversation)
    db.commit()
    
    return answer

# Storytelling endpoints
@app.post("/projects/{project_id}/stories", response_model=schemas.Story)
async def create_story(
    project_id: int,
    story_config: schemas.StoryConfig,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get analyses and insights
    analyses = project.analyses
    all_insights = []
    
    for analysis in analyses:
        if analysis.insights:
            all_insights.extend(analysis.insights)
    
    # Generate narrative
    narrative = await ai_assistant.generate_narrative(
        all_insights,
        {"project_name": project.name, "analysis_count": len(analyses)}
    )
    
    # Create story
    db_story = models.Story(
        project_id=project_id,
        title=story_config.title,
        narrative=narrative,
        components=story_config.components,
        export_formats=story_config.export_formats
    )
    
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    return db_story

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Project Phoenix API is running", "version": "1.0.0"}

# Keep legacy endpoints for backward compatibility
@app.post("/api/eda/conventional", response_class=HTMLResponse)
async def conventional_eda(file: UploadFile = File(...), tool: str = Form(...)):
    # Legacy endpoint implementation
    pass

@app.post("/api/eda/ai/analyze", response_class=JSONResponse)
async def ai_analyze(file: UploadFile = File(...), llm_choice: str = Form(...)):
    # Legacy endpoint implementation
    pass

@app.post("/api/eda/ai/transform", response_class=JSONResponse)
async def ai_transform(file: UploadFile = File(...), llm_choice: str = Form(...), transformation_prompt: str = Form(...)):
    # Legacy endpoint implementation
    pass