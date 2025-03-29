#!/bin/bash

# Navigate to the app directory
cd /home/ubuntu/flaskapp-webhook/my_flask_app

# Pull the latest changes from the repository
git pull origin main

# Activate the virtual environment
source venv/bin/activate

# # Install any new dependencies
# pip install -r requirements.txt

# Restart the Gunicorn service
sudo systemctl restart my_flask_app