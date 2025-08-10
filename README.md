# Dream Analytics Dashboard

PostgreSQL-powered dashboard for analyzing dream data with categories and unique dream analysis.

## Features

- **Categories Analysis**: View dream statistics by category and subcategory
- **Unique Dreams Analysis**: Explore normalized dream titles with filtering
- **Age-based Filtering**: Filter analysis by age ranges
- **Responsive UI**: React-based dashboard with Material-UI

## Deployment on Render

1. Connect this repository to Render
2. Add PostgreSQL add-on to your service  
3. Set environment variables (DATABASE_URL is auto-configured)
4. Run migration script to import data: `python migrate_to_postgres.py`

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set database URL
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run migration (first time only)
python migrate_to_postgres.py

# Start server
python app.py
```

## Tech Stack

- **Backend**: Flask + PostgreSQL
- **Frontend**: React + Material-UI  
- **Database**: PostgreSQL (115k+ dreams, 36k+ unique titles)
- **Deployment**: Render.com