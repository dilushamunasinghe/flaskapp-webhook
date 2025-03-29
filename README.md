# Flask app with GitHub Webhook

## Instructions

Create an EC2 Ubuntu and login in

`'ssh -i your-key.pem ec2-user@your-ec2-public-ip
`

### install dependencies

```bash
sudo apt update 
sudo apt install python3 python3-pip -y
pip install flask gunicorn
```

### Clone repository

#### Step 1: Generate an SSH Key
Open a terminal on your local machine.

Run the following command to generate a new SSH key:

bash
`ssh-keygen -t ed25519 -C "your_email@example.com"`

Replace "your_email@example.com" with the email address associated with your GitHub account.

If your system doesn't support the ed25519 algorithm, use:

bash
`ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`

When prompted to "Enter a file in which to save the key," press Enter to accept the default location (~/.ssh/id_ed25519).

Optionally, set a passphrase for added security (or press Enter to skip).

#### Step 2: Add the SSH Key to the SSH Agent
Start the SSH agent:

bash
`eval "$(ssh-agent -s)"`

Add your SSH private key to the agent:

bash
`ssh-add ~/.ssh/id_ed25519`

#### Step 3: Add the SSH Key to Your GitHub Account
Copy the public key to your clipboard:

bash
`cat ~/.ssh/id_ed25519.pub`

Highlight and copy the output.

Go to your GitHub account:

Navigate to Settings > SSH and GPG keys.

Click New SSH key.

Paste the public key into the "Key" field and give it a title (e.g., "My Laptop Key").

Click Add SSH key.

Run the following command to test your connection:

```bash
ssh -T git@github.com
```

#### Step 4: Clone the Repository
Go to the GitHub repository you want to download.

Click the green Code button and select SSH.

Copy the SSH URL (e.g., git@github.com:username/repo.git).

Clone the repository using the SSH URL:

bash
`git clone git@github.com:username/repo.git`

## Deploy Flask app  

1. Activate Virtual Environment
Make sure you're in the correct directory:

`cd flaskapp-webhook/my_flask_app`
1. Activate the virtual environment:

`source venv/bin/activate`

2. Test Gunicorn
Run the Flask application to ensure it works:

```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

Access your app temporarily at http://your-ec2-public-ip:5000. If everything looks good, move on to hosting.

3. Configure Nginx
Ensure your Nginx configuration file (`/etc/nginx/sites-available/my_flask_app`) points to your app's location:

```nginx
server {
    listen 80;
    server_name your-ec2-public-ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
} 
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/my_flask_app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
4. Add a GitHub Webhook
If you haven't already, configure the webhook in your GitHub repository:

Go to Settings > Webhooks.

Add http://your-ec2-public-ip/webhook as the payload URL.

Ensure your app.py has the /webhook route to trigger a deployment script.

5. Deployment Script
Create and test your deploy.sh script to pull changes from GitHub and restart the app:

```bash
#!/bin/bash
cd /home/ec2-user/flaskapp-webhook/my_flask_app
git pull origin main
source venv/bin/activate
sudo systemctl restart my_flask_app
```
Make it executable:

```bash
chmod +x deploy.sh
```
### Create an app service

Step 1: Update the Service File
Open your service file:

```bash
sudo nano /etc/systemd/system/my_flask_app.service
```
Replace ec2-user with ubuntu in the [Service] section:

```ini
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flaskapp-webhook/my_flask_app
Environment="PATH=/home/ubuntu/flaskapp-webhook/my_flask_app/venv/bin"
ExecStart=/home/ubuntu/flaskapp-webhook/my_flask_app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Step 2: Reload the Systemd Daemon
After modifying the service file, reload the systemd daemon to apply the changes:

```bash
sudo systemctl daemon-reload
```
Step 3: Start and Enable the Service
Start the service:


```bash
sudo systemctl start my_flask_app
```
Enable the service to run on boot:

```bash
sudo systemctl enable my_flask_app
```
Step 4: Verify the Service
Check the status of the service:

```bash
sudo systemctl status my_flask_app
```
If everything is configured correctly, the service should be running without errors, and your Flask app should be accessible.


## Troubleshoot

### Check app service logs

```
sudo journalctl -u my_flask_app
```

Check Active Processes on Port 5000
Identify the process occupying port 5000:

```bash
sudo netstat -tuln | grep 5000
```
Alternatively, use lsof:

```bash
sudo lsof -i:5000
```
This command will display the process ID (PID) of the application using port 5000.

Kill the Process
Once you've identified the PID, terminate the process:

```bash
sudo kill -9 <PID>
```
Replace <PID> with the actual process ID from the previous step.

Restart Your Service
Now that port 5000 is free, restart your Gunicorn service:

```bash
sudo systemctl restart my_flask_app
```
Verify Port Usage
Confirm that the correct process is running on port 5000:

```bash
sudo netstat -tuln | grep 5000
```
It should now show your Gunicorn app.

### Check Server Accessibility
Ensure your EC2 instance allows incoming HTTP traffic:

Go to the AWS Management Console.

Check the Security Group for your EC2 instance.

Ensure there’s a rule allowing inbound traffic on port 80 (HTTP).

Test the `/webhook` endpoint manually:

Use curl to send a POST request to your webhook:

```bash
curl -X POST http://your-ec2-public-ip/webhook -d '{"test": "data"}' -H "Content-Type: application/json"
```

Check if the Flask app logs the request.