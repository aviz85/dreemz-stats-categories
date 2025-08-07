#!/bin/bash

# Load environment variables
export DB_NAME=dreemz_prod
export DB_USERNAME=aviz_prod_ro
export DB_PASSWORD='$g~cE$PulHFXNEWwED3{'
export DB_HOST=dreemz-prod.c6qnrs7z5bfu.us-east-2.rds.amazonaws.com
export DB_PORT=5432

# Connect to PostgreSQL
PGGSSENCMODE=disable PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME" -d "$DB_NAME"