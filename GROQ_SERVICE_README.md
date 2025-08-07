# Groq LLM Service

A Python service for interacting with Groq's language models API.

## Setup

1. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_api_key_here
```

2. Install dependencies:
```bash
pip install python-dotenv requests psycopg2-binary
```

## Files

- `groq_service.py` - Main service class for Groq API interactions
- `groq_example.py` - Example usage of the service
- `analyze_posts.py` - Analyze database posts using Groq

## Usage

### Basic Usage
```python
from groq_service import GroqService

# Initialize service
groq = GroqService()

# Get a simple completion
response = groq.get_completion("Explain quantum computing in simple terms")
print(response)
```

### Analyze Database Posts
```bash
python analyze_posts.py
```

This will:
1. Fetch posts from the database that haven't been analyzed
2. Use Groq to analyze each post for:
   - Summary
   - Category classification
   - Sentiment analysis
   - Key themes/keywords
3. Save results to `post_analysis_results.json`

## Available Models

- `llama3-8b-8192` (default)
- `llama3-70b-8192`
- `mixtral-8x7b-32768`
- `gemma-7b-it`
- `gemma2-9b-it`

## Features

- Simple completion interface
- Chat completion with conversation history
- Text analysis (summary, sentiment, categories)
- Environment variable configuration
- Error handling and retry logic
- JSON response parsing