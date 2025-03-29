#!/bin/bash

# Navigate to app directory
cd /home/ubuntu/flaskapp-webhook/my_flask_app || exit

# Activate the virtual environment
source venv/bin/activate

# Pull latest changes
git pull origin main

# Restart Gunicorn
sudo systemctl restart gunicorn
