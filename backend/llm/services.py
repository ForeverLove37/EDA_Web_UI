import httpx
import os
import json

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY_PLACEHOLDER")
CHATAIAPI_API_KEY = os.environ.get("CHATAIAPI_API_KEY", "CHATAIAPI_API_KEY_PLACEHOLDER")

class LLMClient:
    def __init__(self):
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.chataiapi_url = "https://www.chataiapi.com/v1/chat/completions"

    async def _call_api(self, url: str, headers: dict, data: dict):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
            except Exception as e:
                return {"error": str(e)}

    async def analyze_data(self, llm_choice: str, text_data: str):
        prompt = f"""
        You are an expert data analyst. Analyze the following text data and provide a summary of:
        1. Key themes and topics.
        2. Any identifiable named entities (people, places, organizations).
        3. The overall sentiment (positive, negative, neutral).
        4. A brief summary of the data's meaning and potential quality issues.

        Data to analyze:
        ---
        {text_data}
        ---
        """
        
        if llm_choice == "deepseek":
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response_data = await self._call_api(self.deepseek_url, headers, data)
        elif llm_choice == "chataiapi":
            headers = {"Authorization": f"Bearer {CHATAIAPI_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "default-model", "messages": [{"role": "user", "content": prompt}]} # Assuming a default model
            response_data = await self._call_api(self.chataiapi_url, headers, data)
        else:
            return {"error": "Invalid LLM choice"}

        if "error" in response_data:
            return response_data
        
        return {"analysis": response_data["choices"][0]["message"]["content"]}

    async def transform_data(self, llm_choice: str, text_data: str, transformation_prompt: str):
        prompt = f"""
        You are a data transformation expert. Convert the following unstructured data into a structured JSON format based on the user's request.
        The output MUST be a valid JSON object or a JSON array.

        User's request: "{transformation_prompt}"

        Unstructured data:
        ---
        {text_data}
        ---
        """

        if llm_choice == "deepseek":
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
            response_data = await self._call_api(self.deepseek_url, headers, data)
        elif llm_choice == "chataiapi":
            headers = {"Authorization": f"Bearer {CHATAIAPI_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "default-model", "messages": [{"role": "user", "content": prompt}]} # Assuming a default model
            response_data = await self._call_api(self.chataiapi_url, headers, data)
        else:
            return {"error": "Invalid LLM choice"}

        if "error" in response_data:
            return response_data
            
        try:
            content = response_data["choices"][0]["message"]["content"]
            # The content might be a stringified JSON, so we parse it.
            return {"transformed_data": json.loads(content)}
        except (json.JSONDecodeError, KeyError) as e:
            return {"error": f"Failed to parse LLM response: {str(e)}", "raw_response": content}

llm_client = LLMClient()
