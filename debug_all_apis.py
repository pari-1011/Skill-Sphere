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
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print(f"API Key: {api_key[:15]}...")
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
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello from Gemini!' and nothing else.")
        
        return response.text.strip()
        
    except Exception as e:
        return f"Exception: {str(e)}"

def test_cohere_api():
    print("\n🔷 Testing Cohere API...")
    try:
        import streamlit as st
        
        api_key = st.secrets["cohere_api_key"]
        
        url = "https://api.cohere.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "command-light",
            "prompt": "Say 'Hello from Cohere!' and nothing else.",
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result["generations"][0]["text"]
        else:
            return f"Error {response.status_code}: {response.text}"
            
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
