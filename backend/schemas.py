from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectWithDetails(Project):
    data_sources: List['DataSource'] = []
    analyses: List['Analysis'] = []
    stories: List['Story'] = []

# Data source schemas
class DataSourceBase(BaseModel):
    name: str
    type: str
    connection_config: Dict[str, Any]

class DataSourceCreate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: int
    project_id: int
    data_preview: Optional[Dict[str, Any]] = None
    data_profile: Optional[Dict[str, Any]] = None
    data_quality_issues: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisConfig(BaseModel):
    name: str
    analysis_type: str = "eda"
    parameters: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    analysis_id: int
    insights: List[Dict[str, Any]]
    summary: str

class Analysis(BaseModel):
    id: int
    project_id: int
    name: str
    type: str
    config: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI conversation schemas
class Question(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str
    source: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

# Storytelling schemas
class StoryConfig(BaseModel):
    title: str
    components: List[Dict[str, Any]]
    export_formats: List[str] = ["pdf", "html"]

class Story(BaseModel):
    id: int
    project_id: int
    title: str
    narrative: str
    components: Dict[str, Any]
    export_formats: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Update forward references
ProjectWithDetails.update_forward_refs()