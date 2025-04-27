#!/bin/bash

# Exit on error
set -o errexit

# Create required directories
mkdir -p /opt/render/project/src/data/analyses
mkdir -p /opt/render/project/src/data/uploads

# Create empty JSON files if they don't exist
mkdir -p /opt/render/project/src/data
touch /opt/render/project/src/data/users.json
touch /opt/render/project/src/data/properties.json
touch /opt/render/project/src/data/transactions.json
touch /opt/render/project/src/data/categories.json
touch /opt/render/project/src/data/reimbursements.json

# Initialize empty JSON arrays in files if they're empty
for file in /opt/render/project/src/data/*.json; do
    if [ ! -s "$file" ]; then
        echo "[]" > "$file"
    fi
done

echo "Directory structure initialized successfully"
echo "Contents of /opt/render/project/src/data:"
ls -la /opt/render/project/src/data

# Install Python dependencies
pip install -r requirements.txt

# Start gunicorn
gunicorn --bind 0.0.0.0:$PORT wsgi:app