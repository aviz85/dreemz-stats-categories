# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dream analytics dashboard that analyzes and visualizes dream data from a SQLite database. The system consists of:

- **Flask Backend** (`app.py`): Serves REST APIs for dream analytics with HTTP Basic Authentication
- **React Frontend** (`frontend/`): Material-UI dashboard with multiple analysis views
- **SQLite Database** (`dreams_complete.db`): Contains dream records with categories and metadata
- **FAISS Integration**: Vector similarity search for finding similar dreams

## Development Setup

### Backend
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
echo "ADMIN_USERNAME=admin" > .env
echo "ADMIN_PASSWORD=changeme123" >> .env

# Run development server
python3 app.py
```

### Frontend
```bash
cd frontend
npm install
npm start  # Development server on port 3000
npm run build  # Production build
```

## Key Architecture Components

### Authentication System
- HTTP Basic Authentication on all API endpoints using Flask-HTTPAuth
- Credentials stored in `.env` file and hashed with Werkzeug
- Frontend handles auth via localStorage and axios interceptors in `frontend/src/utils/api.js`

### Database Schema
Dreams table contains:
- `category_1`, `category_2`, `category_3`: Dream categories (dreams can have 1-3 categories)
- `age_at_dream`: Dreamer's age (some records have NULL values)
- `normalized_title`: Processed dream title for analysis

### API Categories Analysis
The `/api/categories-analysis` endpoint supports:
- `include_all=true/false`: Count all categories (1,2,3) vs just category_1
- Age filtering with `min_age` and `max_age` parameters
- When `include_all=true`, uses UNION ALL to count category instances across all three category fields

### FAISS Similarity Search
- Requires `dreams_faiss_index.faiss` and `dreams_faiss_mapping.json` files
- Index maps dream embeddings to database IDs for similarity matching
- System gracefully handles missing FAISS files

### Frontend Components
- `CategoriesAnalysis.js`: Main analytics view with age filtering and category inclusion toggle
- `SimilaritySearch.js`: FAISS-powered dream similarity search
- `LiveDashboard.js`: Real-time statistics dashboard
- `UniqueDreams.js`: Analysis of unique dream patterns

## Data Insights
- Total dreams: ~115,624
- When including all categories (1,2,3): ~321,958 category instances
- Age filter default: 13-60 years (excludes ~4k dreams with NULL or extreme ages)
- 30 unique dream categories in the dataset

## Deployment Notes
- Uses gunicorn for production WSGI serving
- Designed for Contabo VPS deployment with nginx reverse proxy
- Database and FAISS files are gitignored due to size (see .gitignore)
- Virtual environment (.venv) is used for dependency isolation