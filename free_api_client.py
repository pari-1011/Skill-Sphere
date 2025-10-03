import streamlit as st
import google.generativeai as genai
import requests
import json
import os
from typing import Dict, List, Optional
import time


class FreeAPIClient:
    """Unified client for multiple free AI APIs"""
    
    def __init__(self):
        self.api_provider = st.secrets.get("api_provider", "gemini").lower()
        self.setup_client()
    
    def setup_client(self):
        """Setup the appropriate client based on provider. Falls back if a provider is misconfigured."""
        order = [self.api_provider] + [p for p in ["gemini", "groq", "cohere"] if p != self.api_provider]
        errors = {}
        for prov in order:
            try:
                if prov == "gemini":
                    self.setup_gemini()
                elif prov == "groq":
                    self.setup_groq()
                elif prov == "cohere":
                    self.setup_cohere()
                self.api_provider = prov
                return
            except Exception as e:
                errors[prov] = str(e)
                continue
        # If we reach here, none worked
        msg = (
            "No working AI provider configured. Set at least one of GEMINI_API_KEY/GOOGLE_API_KEY, GROQ_API_KEY, or COHERE_API_KEY "
            "in environment variables or Streamlit secrets. Details: " + json.dumps(errors)
        )
        st.error(msg)
        raise RuntimeError(msg)
    
    def setup_gemini(self):
        """Setup Google Gemini API"""
        try:
            api_key = (
                st.secrets.get("gemini_api_key")
                or st.secrets.get("GEMINI_API_KEY")
                or st.secrets.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_API_KEY")
            )
            if not api_key:
                raise KeyError("gemini_api_key missing")
            genai.configure(api_key=api_key)
            # Determine model: prefer secrets override, else pick from available supported names
            model_name = (
                st.secrets.get("gemini_model")
                or st.secrets.get("GEMINI_MODEL")
            )
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
            # Do not show error here; allow fallback to other providers
            raise
    
    def setup_groq(self):
        """Setup Groq API"""
        self.groq_api_key = (
            st.secrets.get("groq_api_key")
            or st.secrets.get("GROQ_API_KEY")
            or os.environ.get("GROQ_API_KEY")
        )
        if not self.groq_api_key:
            raise KeyError("groq_api_key missing")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = (
            st.secrets.get("groq_model")
            or st.secrets.get("GROQ_MODEL")
            or "llama-3.1-8b-instant"
        )
    
    def setup_cohere(self):
        """Setup Cohere API"""
        self.cohere_api_key = (
            st.secrets.get("cohere_api_key")
            or st.secrets.get("COHERE_API_KEY")
            or os.environ.get("COHERE_API_KEY")
        )
        if not self.cohere_api_key:
            raise KeyError("cohere_api_key missing")
        # Use Chat API since Generate API was removed in 2025
        self.cohere_url = "https://api.cohere.ai/v1/chat"
        self.cohere_model = (
            st.secrets.get("cohere_model")
            or st.secrets.get("COHERE_MODEL")
            or "command-r7b"
        )
    
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
