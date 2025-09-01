from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    data_sources = relationship("DataSource", back_populates="project")
    analyses = relationship("Analysis", back_populates="project")
    stories = relationship("Story", back_populates="project")

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    type = Column(String)  # csv, postgres, mysql, bigquery, s3, api, pdf, etc.
    connection_config = Column(JSON)  # Connection details
    raw_data = Column(Text)  # For small files, store directly
    data_preview = Column(JSON)  # First 100 rows for quick preview
    data_profile = Column(JSON)  # Initial AI analysis results
    data_quality_issues = Column(JSON)  # Detected issues
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="data_sources")
    transformations = relationship("DataTransformation", back_populates="data_source")

class DataTransformation(Base):
    __tablename__ = "data_transformations"
    
    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"))
    transformation_type = Column(String)  # clean, join, filter, aggregate, etc.
    transformation_config = Column(JSON)  # Configuration for the transformation
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    data_source = relationship("DataSource", back_populates="transformations")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    type = Column(String)  # eda, statistical, machine_learning, etc.
    config = Column(JSON)  # Analysis configuration
    results = Column(JSON)  # Analysis results
    insights = Column(JSON)  # AI-generated insights
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="analyses")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    narrative = Column(Text)  # AI-generated narrative
    components = Column(JSON)  # Charts, tables, insights included
    export_formats = Column(JSON)  # Export configurations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="stories")

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    message_type = Column(String)  # user_query, ai_response, insight, suggestion
    content = Column(Text)
    conversation_metadata = Column(JSON)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project")