import streamlit as st
import google.generativeai as genai
import requests
import json
from typing import Dict, List, Optional
import time


class FreeAPIClient:
    """Unified client for multiple free AI APIs"""
    
    def __init__(self):
        self.api_provider = st.secrets.get("api_provider", "gemini").lower()
        self.setup_client()
    
    def setup_client(self):
        """Setup the appropriate client based on provider"""
        if self.api_provider == "gemini":
            self.setup_gemini()
        elif self.api_provider == "groq":
            self.setup_groq()
        elif self.api_provider == "cohere":
            self.setup_cohere()
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def setup_gemini(self):
        """Setup Google Gemini API"""
        try:
            api_key = st.secrets["gemini_api_key"]
            genai.configure(api_key=api_key)
            # Use the correct model name for v1 API
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Failed to setup Gemini API: {e}")
            raise
    
    def setup_groq(self):
        """Setup Groq API"""
        self.groq_api_key = st.secrets["groq_api_key"]
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = st.secrets.get("groq_model", "llama3-8b-8192")
    
    def setup_cohere(self):
        """Setup Cohere API"""
        self.cohere_api_key = st.secrets["cohere_api_key"]
        self.cohere_url = "https://api.cohere.ai/v1/generate"
    
    def chat_completion(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Universal chat completion method"""
        try:
            if self.api_provider == "gemini":
                return self._gemini_completion(messages, max_tokens, temperature)
            elif self.api_provider == "groq":
                return self._groq_completion(messages, max_tokens, temperature)
            elif self.api_provider == "cohere":
                return self._cohere_completion(messages, max_tokens, temperature)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _gemini_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Handle Gemini API completion"""
        try:
            # Convert OpenAI-style messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Check if response is blocked or empty
            if not response.text or response.text.strip() == "":
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    return f"Content filtered by safety settings: {response.prompt_feedback}"
                return "Empty response from Gemini API"
            
            return response.text.strip()
        except Exception as e:
            if "quota" in str(e).lower():
                return "API quota exceeded. Please try again later or switch to a different API provider."
            if "safety" in str(e).lower():
                return "Content filtered by safety settings. Try rephrasing your request."
            return f"Gemini API Error: {str(e)}"
    
    def _groq_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Handle Groq API completion"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.groq_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.groq_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Groq API Error: {str(e)}"
    
    def _cohere_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Handle Cohere API completion"""
        headers = {
            "Authorization": f"Bearer {self.cohere_api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to single prompt for Cohere
        prompt = self._convert_messages_to_prompt(messages)
        
        payload = {
            "model": "command-light",  # Free tier model
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.cohere_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result["generations"][0]["text"]
        except Exception as e:
            return f"Cohere API Error: {str(e)}"
    
    def _convert_messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert OpenAI-style messages to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)


# Global client instance
_client = None

def get_client():
    """Get or create the global API client"""
    global _client
    if _client is None:
        _client = FreeAPIClient()
    return _client

def ask_ai(messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
    """Simple function to ask AI - compatible with existing code"""
    client = get_client()
    return client.chat_completion(messages, max_tokens, temperature)

# Compatibility function for existing azure_openai_api.py usage
def ask_azure_openai(messages: List[Dict]) -> str:
    """Compatibility function to replace Azure OpenAI calls"""
    return ask_ai(messages, max_tokens=500, temperature=1.0)
