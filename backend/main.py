from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import pandas as pd

import models, schemas, auth, database, data_connectors, ai_assistant
from auth import get_current_active_user
from database import get_db, init_db

# Convert numpy types to native Python types for JSON serialization
def convert_numpy_types(obj):
    import numpy as np
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

# Export generation functions
def generate_html_export(story):
    """Generate HTML export for a story"""
    # Handle narrative with proper line breaks
    narrative_html = story.narrative.replace('\n', '<br/>') if story.narrative else 'No narrative available'
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{story.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c5282; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .insight {{ background: #f7fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #4299e1; }}
        .date {{ color: #718096; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{story.title}</h1>
    <div class="date">Generated on {story.created_at.strftime('%Y-%m-%d %H:%M')}</div>
    
    <div class="narrative">
        {narrative_html}
    </div>
    
    <h2>Key Insights</h2>
    """
    
    # Add insights/components
    if story.components and isinstance(story.components, list):
        for component in story.components:
            if component.get('type') == 'insight' and component.get('insight'):
                insight = component['insight']
                html_content += f"""
    <div class="insight">
        <h3>{component.get('title', 'Insight')}</h3>
        <p>{insight.get('message', insight.get('analysis', 'No insight message'))}</p>
    </div>
    """
    
    html_content += """
</body>
</html>
"""
    return html_content

def generate_pdf_export(story):
    """Generate PDF export for a story - simplified HTML version for now"""
    # For now, return HTML that can be converted to PDF by the browser
    # In production, you'd use a library like ReportLab or WeasyPrint
    return generate_html_export(story)

def generate_pptx_export(story):
    """Generate PowerPoint export for a story - placeholder"""
    # Placeholder - in production, use python-pptx library
    pptx_content = f"{story.title}\n\n{story.narrative or 'No narrative'}"
    return pptx_content.encode('utf-8')

app = FastAPI(title="Project Phoenix: Symbiotic Analysis Environment", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:6000", "http://localhost:5173"],
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
    try:
        print(f"DEBUG: Starting data source creation for project {project_id}, type {source_type}")
        
        # Verify project ownership
        project = db.query(models.Project).filter(
            models.Project.id == project_id,
            models.Project.owner_id == current_user.id
        ).first()
        
        if not project:
            print(f"DEBUG: Project {project_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Project not found")

        # Parse config
        try:
            connection_config = json.loads(config)
            print(f"DEBUG: Config parsed successfully: {list(connection_config.keys())}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            raise HTTPException(status_code=400, detail="Invalid config JSON")

        # Handle file upload if present
        file_content = None
        if file:
            print(f"DEBUG: Processing file upload: {file.filename}, size: {file.size}")
            file_content = await file.read()
            print(f"DEBUG: File content read: {len(file_content)} bytes")
            if source_type in ['csv', 'excel', 'json', 'pdf']:
                connection_config['file_uploaded'] = True
                connection_config['original_filename'] = file.filename
                print(f"DEBUG: File-based source detected, added metadata")

        # Connect to data source - pass file content separately for file-based sources
        if source_type in ['csv', 'excel', 'json', 'pdf'] and file_content:
            connection_config['file_content'] = file_content
            print(f"DEBUG: Added file_content to connection config")

        print(f"DEBUG: Calling data connector for {source_type}")
        result = await data_connectors.data_connector.connect(source_type, connection_config)
        print(f"DEBUG: Data connector result: success={result.get('success')}")

        if not result['success']:
            print(f"DEBUG: Data connector failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result['error'])

        # Create data source record - ensure we don't store file content in config
        safe_config = connection_config.copy()
        if 'file_content' in safe_config:
            del safe_config['file_content']
            print(f"DEBUG: Removed file_content from safe_config")

        print(f"DEBUG: Creating DataSource object")
        db_data_source = models.DataSource(
            project_id=project_id,
            name=connection_config.get('name', f'{source_type}_source'),
            type=source_type,
            connection_config=safe_config,
            data_preview=result['data_preview'],
            data_profile=result['data_profile'],
            raw_data=json.dumps(result['raw_data_sample']) if result['raw_data_sample'] else None
        )

        print(f"DEBUG: Adding to database session")
        db.add(db_data_source)
        db.commit()
        db.refresh(db_data_source)
        print(f"DEBUG: Data source created successfully with ID: {db_data_source.id}")

        return db_data_source
        
    except Exception as e:
        print(f"ERROR: Exception in create_data_source: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
    assistant = ai_assistant.AIResearchAssistant()
    insights = await assistant.analyze_data(data_sample)
    
    # Convert insights for JSON serialization
    serializable_insights = convert_numpy_types(insights)
    
    # Convert analysis config
    analysis_config_dict = analysis_config.dict()
    converted_config = convert_numpy_types(analysis_config_dict)
    
    # Save analysis
    db_analysis = models.Analysis(
        project_id=project_id,
        name=analysis_config.name,
        type=analysis_config.analysis_type,
        config=converted_config,
        results={"insights": serializable_insights},
        insights=serializable_insights
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return {
        "analysis_id": db_analysis.id,
        "insights": serializable_insights,
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
    assistant = ai_assistant.AIResearchAssistant()
    answer = await assistant.answer_question(
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
    assistant = ai_assistant.AIResearchAssistant()
    narrative = await assistant.generate_narrative(
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

# Export endpoints
@app.get("/stories/{story_id}/export/{format}")
async def export_story(
    story_id: int,
    format: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export story in specified format (pdf, html, pptx)"""
    # Verify story ownership
    story = db.query(models.Story).join(models.Project).filter(
        models.Story.id == story_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if format not in ["pdf", "html", "pptx"]:
        raise HTTPException(status_code=400, detail="Unsupported export format")
    
    # Generate export content based on format
    if format == "pdf":
        content = generate_pdf_export(story)
        media_type = "application/pdf"
        filename = f"{story.title}.pdf"
    elif format == "html":
        content = generate_html_export(story)
        media_type = "text/html"
        filename = f"{story.title}.html"
    elif format == "pptx":
        content = generate_pptx_export(story)
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = f"{story.title}.pptx"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

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