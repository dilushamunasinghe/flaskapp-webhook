from flask import Flask, render_template, request, jsonify
import os
import logging
import subprocess

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Path configurations
APP_DIRECTORY = '/home/ubuntu/flaskapp-webhook/my_flask_app'
DEPLOY_SCRIPT = os.path.join(APP_DIRECTORY, 'deploy.sh')
VENV_PATH = os.path.join(APP_DIRECTORY, 'venv')
TARGET_BRANCH = 'main'

@app.route('/')
def home():
    """Serve the index.html file."""
    logging.info("Serving the home page (index.html).")
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook events from GitLab."""
    try:
        payload = request.json
        logging.info(f"Webhook payload received: {payload}")

        # Extract the ref field to determine the branch
        ref = payload.get('ref')
        logging.info(f"Branch reference in payload: {ref}")

        if ref and ref == f'refs/heads/{TARGET_BRANCH}':
            logging.info(f"Webhook triggered by changes to branch: {TARGET_BRANCH}.")

            # Activate the virtual environment and run the deployment script
            if os.path.exists(DEPLOY_SCRIPT):
                logging.info(f"Found deployment script at: {DEPLOY_SCRIPT}. Executing...")
                exit_code = subprocess.call(f"source {VENV_PATH}/bin/activate && sh {DEPLOY_SCRIPT}", shell=True, executable="/bin/bash")
                if exit_code == 0:
                    logging.info("Deployment script executed successfully.")
                    return jsonify({"message": f"Deployment initiated for branch: {TARGET_BRANCH}."}), 200
                else:
                    logging.error("Deployment script failed during execution.")
                    return jsonify({"message": "Deployment script failed during execution."}), 500
            else:
                logging.error(f"Deployment script not found at: {DEPLOY_SCRIPT}.")
                return jsonify({"message": "Deployment script not found."}), 500
        else:
            logging.warning(f"Webhook triggered but not targeting the '{TARGET_BRANCH}' branch. Ref received: {ref}.")
            return jsonify({"message": f"Not targeting the '{TARGET_BRANCH}' branch."}), 400

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"message": f"An error occurred while processing the webhook: {e}."}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
