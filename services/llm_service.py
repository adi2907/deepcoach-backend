# ============================================================================
# File: services/llm_service.py
# Enhanced LLM service with OpenRouter structured output support
# ============================================================================

import requests
import json
import os
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, model: str = "openai/gpt-oss-20b:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model
        
    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Basic LLM generation for unstructured output"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://learning-platform.com",
            "X-Title": "Learning Platform"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def generate_structured(self, 
                          system_prompt: str, 
                          user_prompt: str, 
                          response_model: Type[BaseModel],
                          temperature: float = 0.3) -> BaseModel:
        """Generate structured output using OpenRouter's JSON schema feature"""
        
        # Generate JSON schema from Pydantic model
        schema = response_model.model_json_schema()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://learning-platform.com",
            "X-Title": "Learning Platform"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__.lower(),
                    "strict": True,
                    "schema": schema
                }
            }
        }
        
        logger.info(f"Making structured request to {self.model}")
        logger.debug(f"Schema: {schema}")
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Structured API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse and validate with Pydantic
        try:
            data = json.loads(content)
            return response_model(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse structured response: {content}")
            raise Exception(f"Failed to parse structured response: {e}")
    
    def set_model(self, model: str):
        """Switch models on the fly"""
        self.model = model
        logger.info(f"Switched to model: {model}")