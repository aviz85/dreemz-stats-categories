#!/bin/bash
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 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" \
  -d '{
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "user", "content": "Translate to English: להיות יוטיובר"}],
    "max_tokens": 50
  }'