#!/usr/bin/env python3
"""
Debug all API providers to find working one
"""

import os
import sys
import requests
import json

# Add current directory to path
sys.path.append(os.getcwd())

def test_groq_api():
    print("🦦 Testing Groq API...")
    try:
        import streamlit as st
        api_key = st.secrets["groq_api_key"]
        model = st.secrets.get("groq_model", "llama-3.1-8b-instant")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Exception: {str(e)}"

def test_gemini_api():
    print("\n💎 Testing Gemini API...")
    try:
        import streamlit as st
        import google.generativeai as genai
        
        api_key = st.secrets["gemini_api_key"]
        genai.configure(api_key=api_key)
        
        # Prefer a known-supported model; fallback to pro-latest
        preferred = ['models/gemini-2.5-flash', 'models/gemini-pro-latest', 'models/gemini-2.5-pro']
        chosen = None
        try:
            models = list(genai.list_models())
            names = {m.name for m in models if 'generateContent' in getattr(m, 'supported_generation_methods', [])}
            for cand in preferred:
                if cand in names:
                    chosen = cand
                    break
        except Exception:
            pass
        if chosen is None:
            chosen = 'models/gemini-pro-latest'
        
        model = genai.GenerativeModel(chosen)
        resp = model.generate_content("Say 'Hello from Gemini!' and nothing else.")
        # Robust extract
        try:
            if hasattr(resp, 'candidates') and resp.candidates:
                c = resp.candidates[0]
                parts = getattr(getattr(c, 'content', None), 'parts', None)
                if parts:
                    texts = [getattr(p, 'text', '') for p in parts if getattr(p, 'text', None)]
                    if texts:
                        return ' '.join(texts).strip()
        except Exception:
            pass
        if getattr(resp, 'text', None):
            return resp.text.strip()
        return 'Empty response from Gemini API'
        
    except Exception as e:
        return f"Exception: {str(e)}"

def test_cohere_api():
    print("\n🔷 Testing Cohere API...")
    try:
        import streamlit as st
        
        api_key = st.secrets["cohere_api_key"]
        model_candidates = [st.secrets.get("cohere_model", "command-r7b"), "command-r-plus", "command-light", "command"]
        
        url = "https://api.cohere.ai/v1/chat"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        for model in model_candidates:
            payload = {
                "model": model,
                "message": "Say 'Hello from Cohere!' and nothing else.",
                "temperature": 0.7
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result.get("text") or f"Empty text from Cohere Chat (model {model})"
            # Try next model on 404 or model removed
            if response.status_code not in (404, 400):
                # Some other error; break and report
                return f"Error {response.status_code}: {response.text}"
        return f"Error: No working Cohere chat model from candidates {model_candidates}"
            
    except Exception as e:
        return f"Exception: {str(e)}"

if __name__ == "__main__":
    print("🔍 Testing All API Providers...")
    print("=" * 50)
    
    # Test Groq
    groq_result = test_groq_api()
    print(f"Groq Result: {groq_result}")
    
    # Test Gemini
    gemini_result = test_gemini_api()
    print(f"Gemini Result: {gemini_result}")
    
    # Test Cohere
    cohere_result = test_cohere_api()
    print(f"Cohere Result: {cohere_result}")
    
    print("\n" + "=" * 50)
    print("🎯 WORKING APIS:")
    
    if "Hello from Groq" in groq_result:
        print("✅ Groq API is working!")
    else:
        print("❌ Groq API failed")
        
    if "Hello from Gemini" in gemini_result:
        print("✅ Gemini API is working!")
    else:
        print("❌ Gemini API failed")
        
    if "Hello from Cohere" in cohere_result:
        print("✅ Cohere API is working!")
    else:
        print("❌ Cohere API failed")
