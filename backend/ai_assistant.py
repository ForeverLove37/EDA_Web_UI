import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose
from typing import Dict, List, Any, Optional
import json
from llm.services import llm_client

class AIResearchAssistant:
    def __init__(self):
        self.insight_generators = {
            'statistical': self._generate_statistical_insights,
            'clustering': self._generate_clustering_insights,
            'anomaly': self._generate_anomaly_insights,
            'seasonality': self._generate_seasonality_insights,
            'correlation': self._generate_correlation_insights
        }
    
    async def analyze_data(self, data: pd.DataFrame, data_type: str = 'tabular') -> List[Dict[str, Any]]:
        """Comprehensive AI-powered data analysis"""
        insights = []
        
        # Generate insights from all available methods
        for insight_type, generator in self.insight_generators.items():
            try:
                if insight_type == 'statistical':
                    insight = await generator(data)
                else:
                    insight = generator(data)
                
                if insight:
                    insights.append({
                        'type': insight_type,
                        'insight': insight,
                        'confidence': self._calculate_confidence(insight),
                        'actionable': self._is_actionable(insight)
                    })
            except Exception as e:
                print(f"Error generating {insight_type} insight: {e}")
        
        # Sort by confidence and actionable score
        insights.sort(key=lambda x: (x['confidence'], x['actionable']), reverse=True)
        
        return insights
    
    async def generate_narrative(self, insights: List[Dict[str, Any]], data_context: Dict[str, Any]) -> str:
        """Generate cohesive narrative from insights"""
        prompt = f"""
        You are an expert data storyteller. Create a compelling narrative based on these data insights:
        
        Data Context: {json.dumps(data_context, indent=2)}
        
        Insights:
        {json.dumps(insights, indent=2)}
        
        Create a professional narrative that:
        1. Starts with an executive summary
        2. Presents key findings in logical order
        3. Explains the significance of each finding
        4. Provides actionable recommendations
        5. Concludes with next steps
        
        Write in clear, business-friendly language.
        """
        
        result = await llm_client.analyze_data('deepseek', prompt)
        return result.get('analysis', 'Narrative generation failed')
    
    async def answer_question(self, question: str, data: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Answer natural language questions about the data"""
        # First, try to answer with statistical analysis
        statistical_answer = self._answer_with_statistics(question, data)
        if statistical_answer:
            return statistical_answer
        
        # Fall back to LLM for complex questions
        data_sample = data.head(50).to_string()
        prompt = f"""
        Answer this question about the dataset:
        Question: {question}
        
        Data sample:
        {data_sample}
        
        Context: {json.dumps(context)}
        
        Provide a comprehensive answer with:
        1. Direct answer to the question
        2. Supporting evidence from the data
        3. Any limitations or assumptions
        4. Suggested next steps for deeper analysis
        """
        
        result = await llm_client.analyze_data('deepseek', prompt)
        return {
            'answer': result.get('analysis', 'Unable to answer question'),
            'source': 'ai_analysis',
            'confidence': 0.7
        }
    
    def _answer_with_statistics(self, question: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Try to answer simple statistical questions directly"""
        question_lower = question.lower()
        
        # Simple statistical questions
        if 'average' in question_lower and 'of' in question_lower:
            parts = question_lower.split('of')
            if len(parts) > 1:
                column = parts[1].strip().split()[0]
                if column in data.columns:
                    avg = data[column].mean()
                    return {
                        'answer': f"The average {column} is {avg:.2f}",
                        'source': 'statistical_calculation',
                        'confidence': 0.9
                    }
        
        elif 'count' in question_lower:
            if 'rows' in question_lower or 'records' in question_lower:
                count = len(data)
                return {
                    'answer': f"There are {count} records in the dataset",
                    'source': 'statistical_calculation',
                    'confidence': 0.95
                }
        
        return None
    
    async def _generate_statistical_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical insights using LLM"""
        stats_summary = data.describe().to_string()
        prompt = f"""
        Analyze this statistical summary and provide key insights:
        
        {stats_summary}
        
        Focus on:
        1. Data distribution characteristics
        2. Notable patterns or anomalies
        3. Potential data quality issues
        4. Interesting statistical properties
        
        Return as JSON with keys: distribution_insights, patterns, data_quality_issues, statistical_properties.
        """
        
        result = await llm_client.analyze_data('deepseek', prompt)
        try:
            return json.loads(result.get('analysis', '{}'))
        except:
            return {'analysis': result.get('analysis', 'Statistical analysis failed')}
    
    def _generate_clustering_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify data clusters"""
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) < 2:
            return {}
        
        # Simple clustering analysis
        kmeans = KMeans(n_clusters=min(3, len(numeric_data)), random_state=42)
        clusters = kmeans.fit_predict(numeric_data.dropna())
        
        return {
            'cluster_count': len(set(clusters)),
            'cluster_sizes': np.bincount(clusters).tolist(),
            'message': f"Found {len(set(clusters))} natural clusters in the data"
        }
    
    def _generate_anomaly_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in data"""
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) == 0:
            return {}
        
        # Anomaly detection
        clf = IsolationForest(contamination=0.1, random_state=42)
        anomalies = clf.fit_predict(numeric_data.dropna())
        anomaly_count = sum(anomalies == -1)
        
        if anomaly_count > 0:
            return {
                'anomaly_count': anomaly_count,
                'anomaly_percentage': (anomaly_count / len(anomalies)) * 100,
                'message': f"Detected {anomaly_count} potential anomalies ({anomaly_count/len(anomalies)*100:.1f}% of data)"
            }
        return {}
    
    def _generate_seasonality_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonality patterns"""
        # Look for datetime columns and numeric columns
        datetime_cols = data.select_dtypes(include=['datetime']).columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            # Simple seasonality check - would be enhanced in real implementation
            return {
                'message': "Time series data detected. Consider running time series analysis for seasonality patterns."
            }
        return {}
    
    def _generate_correlation_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Find strong correlations"""
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) < 2:
            return {}
        
        corr_matrix = numeric_data.corr()
        strong_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.7:  # Strong correlation
                    strong_correlations.append({
                        'variables': [corr_matrix.columns[i], corr_matrix.columns[j]],
                        'correlation': corr,
                        'strength': 'strong'
                    })
        
        if strong_correlations:
            return {
                'strong_correlations': strong_correlations,
                'message': f"Found {len(strong_correlations)} strong correlations between variables"
            }
        return {}
    
    def _calculate_confidence(self, insight: Dict[str, Any]) -> float:
        """Calculate confidence score for insight"""
        # Simple confidence calculation based on insight content
        if 'message' in insight:
            return 0.8
        elif 'analysis' in insight:
            return 0.7
        else:
            return 0.5
    
    def _is_actionable(self, insight: Dict[str, Any]) -> bool:
        """Determine if insight is actionable"""
        # Simple heuristic for actionability
        actionable_keywords = ['recommend', 'suggest', 'should', 'consider', 'action', 'next steps']
        insight_str = str(insight).lower()
        return any(keyword in insight_str for keyword in actionable_keywords)

ai_assistant = AIResearchAssistant()