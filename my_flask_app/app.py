from flask import Flask, render_template, request, jsonify
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            # Log the full payload for debugging purposes
            logging.info(f"Webhook payload received: {request.json}")

            # Define the target branch (flexible for changes in the future)
            target_branch = 'main'

            # Validate the branch reference in the payload
            if 'ref' in request.json and f'refs/heads/{target_branch}' in request.json['ref']:
                # Log the branch triggering the webhook
                logging.info(f"Webhook triggered by changes to branch: {target_branch}")

                # Trigger the deployment script
                os.system('sh /home/ubuntu/flaskapp-webhook/my_flask_app/deploy.sh')
                return jsonify({"message": f"Deployment initiated for {target_branch} branch"}), 200
            else:
                logging.warning(f"Webhook triggered but not targeting the '{target_branch}' branch.")
                return jsonify({"message": f"Not targeting the '{target_branch}' branch"}), 400
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
            return jsonify({"message": f"An error occurred while processing the webhook: {str(e)}"}), 500
    else:
        logging.warning("Received a request with an unsupported method.")
        return jsonify({"message": "Invalid request method. Only POST is supported."}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
