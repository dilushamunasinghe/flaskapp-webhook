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
    """Handle webhook events from GitHub."""
    try:
        payload = request.json
        logging.info(f"Webhook payload received: {payload}")

        # Extract the ref field to determine the branch
        ref = payload.get('ref')
        logging.info(f"Branch reference in payload: {ref}")

        if ref == f'refs/heads/{TARGET_BRANCH}':
            logging.info(f"Webhook triggered by changes to the branch: {TARGET_BRANCH}.")

            # Check for deployment script existence
            if os.path.isfile(DEPLOY_SCRIPT):
                logging.info(f"Executing deployment script at {DEPLOY_SCRIPT}...")

                # Execute deployment script and log output
                process = subprocess.Popen(
                    f"source {VENV_PATH}/bin/activate && sh {DEPLOY_SCRIPT}",
                    shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    logging.info(f"Deployment completed successfully:\n{stdout.decode().strip()}")
                    return jsonify({"message": "Deployment completed successfully!"}), 200
                else:
                    logging.error(f"Error during deployment:\n{stderr.decode().strip()}")
                    return jsonify({"error": "Deployment script failed.", "details": stderr.decode().strip()}), 500
            else:
                logging.error(f"Deployment script not found at: {DEPLOY_SCRIPT}")
                return jsonify({"error": "Deployment script missing."}), 404
        else:
            logging.warning(f"Webhook triggered but targeting branch: {ref}, not '{TARGET_BRANCH}'.")
            return jsonify({"message": f"Not targeting the '{TARGET_BRANCH}' branch."}), 400

    except Exception as e:
        logging.error(f"Exception occurred while handling the webhook: {e}")
        return jsonify({"error": "An error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting the Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
