# 🚀 Free API Setup Guide for Career Coach App

## Overview

This project has been migrated from Azure-based services to **completely free APIs**! No more paid subscriptions needed.

## 🆓 Free APIs Available

### 1. **Google Gemini API** (Recommended)
- **Free tier**: 15 requests per minute, 1500 requests per day
- **Best for**: General use, good quality responses
- **Get API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. **Groq API** 
- **Free tier**: Very fast inference, generous limits
- **Best for**: Speed, real-time applications  
- **Get API Key**: [Groq Console](https://console.groq.com/keys)

### 3. **Cohere API**
- **Free tier**: 1000 generations per month
- **Best for**: Alternative option
- **Get API Key**: [Cohere Dashboard](https://dashboard.cohere.com/api-keys)

## 📝 Step-by-Step Setup

### Option 1: Google Gemini (Recommended)

1. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated API key

2. **Update Configuration**:
   - Open `.streamlit/secrets.toml`
   - Set: `api_provider = "gemini"`
   - Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key

### Option 2: Groq (Fast Alternative)

1. **Get Groq API Key**:
   - Go to [Groq Console](https://console.groq.com/keys)
   - Sign up/Sign in
   - Create a new API key
   - Copy the API key

2. **Update Configuration**:
   - Open `.streamlit/secrets.toml`
   - Set: `api_provider = "groq"`
   - Replace `YOUR_GROQ_API_KEY_HERE` with your actual API key

### Option 3: Cohere

1. **Get Cohere API Key**:
   - Go to [Cohere Dashboard](https://dashboard.cohere.com/api-keys)
   - Sign up/Sign in
   - Create a new API key
   - Copy the API key

2. **Update Configuration**:
   - Open `.streamlit/secrets.toml`
   - Set: `api_provider = "cohere"`
   - Replace `YOUR_COHERE_API_KEY_HERE` with your actual API key

## 🔧 Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔄 Switching Between APIs

You can easily switch between different APIs by changing the `api_provider` in `.streamlit/secrets.toml`:

```toml
# Use Gemini
api_provider = "gemini"

# Or use Groq for faster responses
api_provider = "groq"

# Or use Cohere as alternative
api_provider = "cohere"
```

## 📊 Free Tier Limits

| API Provider | Free Tier Limits | Best For |
|-------------|------------------|----------|
| **Gemini** | 15 req/min, 1500 req/day | General use, quality |
| **Groq** | High limits, very fast | Speed, real-time |
| **Cohere** | 1000 generations/month | Light usage |

## 🆘 Troubleshooting

### Common Issues:

1. **"API quota exceeded"**:
   - Switch to a different API provider
   - Wait for quota reset
   - Check your rate limits

2. **"Invalid API key"**:
   - Verify the API key is correctly copied
   - Check if the API key has proper permissions
   - Regenerate the API key if needed

3. **"Connection error"**:
   - Check your internet connection
   - Verify the API endpoint is accessible

### Getting Help:

1. Check the API provider's documentation
2. Verify your API key is active
3. Test with a simple API call first

## 🚫 What's No Longer Needed

✅ **Removed Azure Dependencies**:
- ❌ Azure OpenAI API (replaced with free APIs)
- ❌ Azure Form Recognizer (replaced with PyPDF2)  
- ❌ Azure Maps (replaced with OpenStreetMap)

## 🎯 Benefits of Migration

- 💰 **Cost**: Completely free (no more Azure costs)
- 🚀 **Speed**: Groq offers very fast inference  
- 🔄 **Flexibility**: Easy to switch between providers
- 🌍 **Accessibility**: Available worldwide without restrictions
- 📈 **Scalability**: Multiple API options to handle load

## 🔒 Security Notes

- Keep your API keys secret
- Never commit API keys to version control
- Use environment variables in production
- Regularly rotate your API keys

---

**Happy Coding!** 🎉 Your Career Coach app is now running on completely free APIs!
