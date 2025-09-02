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
            
            # Convert raw data sample to ensure JSON serializability
            raw_data_sample = data.head(100).to_dict('records') if hasattr(data, 'head') else data[:100]
            print(f"DEBUG: Raw data sample before conversion: {type(raw_data_sample[0]['OrderID']) if raw_data_sample and 'OrderID' in raw_data_sample[0] else 'N/A'}")
            raw_data_sample = self._convert_numpy_types(raw_data_sample)
            print(f"DEBUG: Raw data sample after conversion: {type(raw_data_sample[0]['OrderID']) if raw_data_sample and 'OrderID' in raw_data_sample[0] else 'N/A'}")
            
            return {
                'success': True,
                'data_preview': preview,
                'data_profile': profile,
                'raw_data_sample': raw_data_sample
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
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
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj

    def _generate_preview(self, data):
        """Generate data preview for UI"""
        if isinstance(data, pd.DataFrame):
            # Convert DataFrame to dict records and convert numpy types
            sample_data = data.head(10).to_dict('records')
            sample_data = self._convert_numpy_types(sample_data)
            
            # Convert missing values counts to native types
            missing_values = data.isnull().sum().to_dict()
            missing_values = self._convert_numpy_types(missing_values)
            
            # Convert row_count and column_count to native types
            row_count = self._convert_numpy_types(len(data))
            column_count = self._convert_numpy_types(len(data.columns))
            
            return {
                'row_count': row_count,
                'column_count': column_count,
                'columns': list(data.columns),
                'sample_data': sample_data,
                'dtypes': data.dtypes.astype(str).to_dict(),
                'missing_values': missing_values
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
        
        # Basic analysis without LLM if API keys are not configured
        if isinstance(data, pd.DataFrame):
            # Convert numpy types to native types
            missing_values = data.isnull().sum().to_dict()
            missing_values = self._convert_numpy_types(missing_values)
            duplicate_rows = self._convert_numpy_types(data.duplicated().sum())
            row_count = self._convert_numpy_types(len(data))
            column_count = self._convert_numpy_types(len(data.columns))
            
            return {
                'structure_assessment': {
                    'row_count': row_count,
                    'column_count': column_count,
                    'columns': list(data.columns),
                    'data_types': data.dtypes.astype(str).to_dict()
                },
                'quality_issues': {
                    'missing_values': missing_values,
                    'duplicate_rows': duplicate_rows
                },
                'cleansing_recommendations': [
                    'Check for consistent data formats across columns',
                    'Validate numerical ranges where applicable',
                    'Standardize categorical values if needed'
                ],
                'initial_insights': [
                    f'Dataset contains {len(data)} records with {len(data.columns)} features',
                    'Perform exploratory analysis to understand distributions and relationships'
                ],
                'analysis_suggestions': [
                    'Statistical summary of numerical columns',
                    'Frequency analysis of categorical columns',
                    'Correlation analysis between variables',
                    'Time series analysis if date columns are present'
                ]
            }
        
        # Fallback for non-DataFrame data
        return {
            'structure_assessment': {'data_type': type(data).__name__, 'size': len(data) if hasattr(data, '__len__') else 'unknown'},
            'quality_issues': {'note': 'Manual inspection required'},
            'cleansing_recommendations': ['Review data structure and formatting'],
            'initial_insights': ['Data requires further analysis'],
            'analysis_suggestions': ['Perform detailed examination based on data type']
        }
    
    # Individual connector methods
    async def _connect_csv(self, config):
        if 'file_content' in config:
            # Handle both string and bytes input
            if isinstance(config['file_content'], bytes):
                content = config['file_content']
                # Auto-detect separator
                try:
                    # Try to detect separator from first line
                    first_line = content.split(b'\n')[0].decode('utf-8', errors='ignore')
                    if '\t' in first_line and first_line.count('\t') > first_line.count(','):
                        return pd.read_csv(io.BytesIO(content), sep='\t')
                    else:
                        return pd.read_csv(io.BytesIO(content))
                except:
                    # Fallback to tab separator
                    return pd.read_csv(io.BytesIO(content), sep='\t')
            else:
                content = config['file_content']
                # Auto-detect separator for string content
                try:
                    first_line = content.split('\n')[0]
                    if '\t' in first_line and first_line.count('\t') > first_line.count(','):
                        return pd.read_csv(io.StringIO(content), sep='\t')
                    else:
                        return pd.read_csv(io.StringIO(content))
                except:
                    return pd.read_csv(io.StringIO(content), sep='\t')
        elif 'file_path' in config:
            # Auto-detect separator for file path
            try:
                with open(config['file_path'], 'r') as f:
                    first_line = f.readline()
                if '\t' in first_line and first_line.count('\t') > first_line.count(','):
                    return pd.read_csv(config['file_path'], sep='\t')
                else:
                    return pd.read_csv(config['file_path'])
            except:
                return pd.read_csv(config['file_path'], sep='\t')
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