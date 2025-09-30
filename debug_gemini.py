#!/usr/bin/env python3
"""
Debug Gemini API issues and check available models
"""

import os
import sys
import google.generativeai as genai

# Add current directory to path
sys.path.append(os.getcwd())

def test_gemini_api():
    try:
        # Load API key from secrets
        import streamlit as st
        
        print("🔍 Debugging Gemini API...")
        print("=" * 50)
        
        # Check if secrets file exists and load API key
        try:
            api_key = st.secrets["gemini_api_key"]
            print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
        except Exception as e:
            print(f"❌ Failed to load API key: {e}")
            return
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Listing available models...")
        try:
            models = genai.list_models()
            print("Available models:")
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"  - {model.name}")
        except Exception as e:
            print(f"❌ Could not list models: {e}")
        
        # Test different model names
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        print(f"\n🧪 Testing different model names...")
        
        for model_name in model_names:
            try:
                print(f"\nTesting: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Simple test
                response = model.generate_content("Say 'Hello World' and nothing else.")
                print(f"✅ SUCCESS with {model_name}: {response.text.strip()}")
                
                # If successful, update the config
                print(f"\n🎉 Working model found: {model_name}")
                return model_name
                
            except Exception as e:
                print(f"❌ Failed with {model_name}: {str(e)}")
        
        print("\n❌ No working models found!")
        return None
        
    except Exception as e:
        print(f"❌ General error: {e}")
        return None

if __name__ == "__main__":
    working_model = test_gemini_api()
    
    if working_model:
        print(f"\n🔧 Update your free_api_client.py to use: {working_model}")
        print("\nNext steps:")
        print("1. Update the model name in free_api_client.py")
        print("2. Test the API again")
        print("3. Run your Streamlit app")
    else:
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if your API key is valid")
        print("2. Try regenerating your API key")
        print("3. Switch to Groq API as alternative")
        print("4. Check Google AI Studio: https://makersuite.google.com/")
