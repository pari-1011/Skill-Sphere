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
            # Determine model: prefer secrets override, else pick from available supported names
            model_name = st.secrets.get("gemini_model")
            if not model_name:
                try:
                    preferred = ['models/gemini-2.5-flash', 'models/gemini-pro-latest', 'models/gemini-2.5-pro', 'models/gemini-2.0-flash']
                    models = list(genai.list_models())
                    names = {m.name for m in models if 'generateContent' in getattr(m, 'supported_generation_methods', [])}
                    for cand in preferred:
                        if cand in names:
                            model_name = cand
                            break
                except Exception:
                    pass
            if not model_name:
                model_name = 'models/gemini-2.5-flash'
            self.model = genai.GenerativeModel(model_name)
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
        # Use Chat API since Generate API was removed in 2025
        self.cohere_url = "https://api.cohere.ai/v1/chat"
        self.cohere_model = st.secrets.get("cohere_model", "command-r7b")
    
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
            
            # Generate content (use defaults for maximum compatibility)
            response = self.model.generate_content(prompt)

            # Try to extract text robustly from candidates/parts
            try:
                if hasattr(response, 'candidates') and response.candidates:
                    cand = response.candidates[0]
                    content = getattr(cand, 'content', None)
                    parts = getattr(content, 'parts', None) if content else None
                    if parts:
                        texts = []
                        for p in parts:
                            t = getattr(p, 'text', None)
                            if t:
                                texts.append(t)
                        if texts:
                            return " ".join(texts).strip()
            except Exception:
                pass
            
            # Fallback to response.text if available
            try:
                if getattr(response, 'text', None):
                    txt = response.text.strip()
                    if txt:
                        return txt
            except Exception:
                pass
            
            # Check for safety/prompt feedback
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                return f"Content filtered by safety settings: {response.prompt_feedback}"
            
            return "Empty response from Gemini API"
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
        """Handle Cohere API completion via Chat API"""
        headers = {
            "Authorization": f"Bearer {self.cohere_api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to single prompt for Cohere Chat
        prompt = self._convert_messages_to_prompt(messages)
        
        payload = {
            "model": self.cohere_model,  # Chat-capable model
            "message": prompt,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.cohere_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            # Chat API returns a top-level 'text'
            return result.get("text", "") or "Empty response from Cohere Chat"
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
