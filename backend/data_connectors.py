import pandas as pd
import io
import json
from typing import Dict, Any, Optional
import httpx
import boto3
# from google.cloud import bigquery  # Removed due to Python 3.13 compatibility
import pdfplumber
import mysql.connector
import psycopg2
from sqlalchemy import create_engine
import openpyxl
from llm.services import llm_client

class DataConnector:
    def __init__(self):
        self.connectors = {
            'csv': self._connect_csv,
            'excel': self._connect_excel,
            'json': self._connect_json,
            'postgres': self._connect_postgres,
            'mysql': self._connect_mysql,
            # 'bigquery': self._connect_bigquery,  # Removed due to Python 3.13 compatibility
            's3': self._connect_s3,
            'api': self._connect_api,
            'salesforce': self._connect_salesforce,
            'pdf': self._connect_pdf
        }
    
    async def connect(self, source_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to data source and return data preview and profile"""
        try:
            if source_type not in self.connectors:
                raise ValueError(f"Unsupported data source type: {source_type}")
            
            # Get data
            data = await self.connectors[source_type](config)
            
            # Generate preview
            preview = self._generate_preview(data)
            
            # AI-powered first contact analysis
            profile = await self._analyze_first_contact(data, source_type)
            
            return {
                'success': True,
                'data_preview': preview,
                'data_profile': profile,
                'raw_data_sample': data.head(100).to_dict('records') if hasattr(data, 'head') else data[:100]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_preview(self, data):
        """Generate data preview for UI"""
        if isinstance(data, pd.DataFrame):
            return {
                'row_count': len(data),
                'column_count': len(data.columns),
                'columns': list(data.columns),
                'sample_data': data.head(10).to_dict('records'),
                'dtypes': data.dtypes.astype(str).to_dict(),
                'missing_values': data.isnull().sum().to_dict()
            }
        elif isinstance(data, list):
            return {
                'row_count': len(data),
                'sample_data': data[:10],
                'type': 'list'
            }
        else:
            return {'type': 'unknown', 'data': str(data)[:500]}
    
    async def _analyze_first_contact(self, data, source_type: str) -> Dict[str, Any]:
        """AI-powered analysis of initial data contact"""
        if isinstance(data, pd.DataFrame):
            data_str = data.head(50).to_string()
        elif isinstance(data, list):
            data_str = str(data[:50])
        else:
            data_str = str(data)
        
        prompt = f"""
        You are an expert data analyst performing "first contact" analysis. Analyze this data sample from a {source_type} source:
        
        {data_str[:2000]}
        
        Provide a comprehensive analysis including:
        1. Data structure and schema assessment
        2. Data quality issues (missing values, inconsistencies, formatting problems)
        3. Potential data cleansing recommendations
        4. Initial insights about the data content
        5. Suggestions for further analysis
        
        Return your analysis as JSON with keys: structure_assessment, quality_issues, cleansing_recommendations, initial_insights, analysis_suggestions.
        """
        
        result = await llm_client.analyze_data('deepseek', prompt)
        
        try:
            return json.loads(result.get('analysis', '{}'))
        except:
            return {'analysis': result.get('analysis', 'Analysis failed')}
    
    # Individual connector methods
    async def _connect_csv(self, config):
        if 'file_content' in config:
            return pd.read_csv(io.StringIO(config['file_content']))
        elif 'file_path' in config:
            return pd.read_csv(config['file_path'])
        else:
            raise ValueError("CSV config requires file_content or file_path")
    
    async def _connect_excel(self, config):
        if 'file_content' in config:
            return pd.read_excel(io.BytesIO(config['file_content']))
        elif 'file_path' in config:
            return pd.read_excel(config['file_path'])
        else:
            raise ValueError("Excel config requires file_content or file_path")
    
    async def _connect_json(self, config):
        if 'file_content' in config:
            return pd.read_json(io.StringIO(config['file_content']))
        elif 'file_path' in config:
            return pd.read_json(config['file_path'])
        elif 'data' in config:
            return pd.DataFrame(config['data'])
        else:
            raise ValueError("JSON config requires file_content, file_path, or data")
    
    async def _connect_postgres(self, config):
        engine = create_engine(f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}")
        query = config.get('query', f"SELECT * FROM {config.get('table', 'information_schema.tables')} LIMIT 1000")
        return pd.read_sql(query, engine)
    
    async def _connect_mysql(self, config):
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        query = config.get('query', f"SELECT * FROM {config.get('table', 'information_schema.tables')} LIMIT 1000")
        return pd.read_sql(query, conn)
    
    # async def _connect_bigquery(self, config):
    #     client = bigquery.Client.from_service_account_json(config['service_account_key'])
    #     query = config.get('query', "SELECT * FROM `bigquery-public-data.samples.shakespeare` LIMIT 1000")
    #     return client.query(query).to_dataframe()
    
    async def _connect_s3(self, config):
        s3 = boto3.client('s3', 
                         aws_access_key_id=config['access_key'],
                         aws_secret_access_key=config['secret_key'])
        
        obj = s3.get_object(Bucket=config['bucket'], Key=config['key'])
        file_content = obj['Body'].read()
        
        if config['key'].endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_content))
        elif config['key'].endswith('.json'):
            return pd.read_json(io.BytesIO(file_content))
        elif config['key'].endswith(('.xlsx', '.xls')):
            return pd.read_excel(io.BytesIO(file_content))
        else:
            return file_content.decode('utf-8')
    
    async def _connect_api(self, config):
        async with httpx.AsyncClient() as client:
            response = await client.get(config['url'], headers=config.get('headers', {}))
            response.raise_for_status()
            
            if config.get('format') == 'json':
                return pd.DataFrame(response.json())
            else:
                return response.text
    
    async def _connect_salesforce(self, config):
        # Placeholder for Salesforce connection
        # Would use simple_salesforce or similar library
        raise NotImplementedError("Salesforce connector not implemented yet")
    
    async def _connect_pdf(self, config):
        if 'file_content' in config:
            with pdfplumber.open(io.BytesIO(config['file_content'])) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif 'file_path' in config:
            with pdfplumber.open(config['file_path']) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        else:
            raise ValueError("PDF config requires file_content or file_path")
        
        return text

data_connector = DataConnector()