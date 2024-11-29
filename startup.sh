#!/bin/bash

# Create required directories in /data if they don't already exist
mkdir /data/analyses
mkdir /data/uploads

# Ensure proper permissions
chmod -R 644 /data

# Create empty JSON files if they don't exist
touch /data/users.json
touch /data/properties.json
touch /data/transactions.json
touch /data/categories.json
touch /data/reimbursements.json

# Initialize empty JSON arrays in files if they're empty
for file in /data/*.json; do
    if [ ! -s "$file" ]; then
        echo "[]" > "$file"
    fi
done

echo "Directory structure initialized successfully"
echo "Contents of /data:"
ls -la /data

# Start the application

export PATH=$PATH:/usr/local/python3/bin && pip install gunicorn && gunicorn app:app