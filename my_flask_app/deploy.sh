#!/bin/bash

# Navigate to the app directory
cd /home/ubuntu/flaskapp-webhook/my_flask_app || exit

# Activate the virtual environment
source venv/bin/activate

# Pull the latest changes from the repository
git pull origin main

# # Install any new dependencies
# pip install -r requirements.txt

# Restart the Gunicorn service
sudo systemctl restart my_flask_app