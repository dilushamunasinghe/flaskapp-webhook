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
    try:
        payload = request.json
        logging.info(f"Webhook payload received: {payload}")
        ref = payload.get('ref')
        logging.info(f"Branch reference in payload: {ref}")

        if ref and ref == 'refs/heads/main':
            logging.info(f"Webhook triggered for main branch.")

            deploy_script = '/home/ubuntu/flaskapp-webhook/my_flask_app/deploy.sh'
            process = subprocess.Popen(
                ['bash', deploy_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                logging.info(f"Deployment script executed successfully.\nOutput: {stdout.decode().strip()}")
                return jsonify({"message": "Deployment completed successfully"}), 200
            else:
                logging.error(f"Deployment script failed.\nError: {stderr.decode().strip()}")
                return jsonify({"message": "Deployment script failed", "error": stderr.decode().strip()}), 500
        else:
            logging.warning(f"Webhook triggered but not targeting the 'main' branch. Ref received: {ref}")
            return jsonify({"message": "Not targeting the 'main' branch"}), 400

    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return jsonify({"message": f"Internal server error: {e}"}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)