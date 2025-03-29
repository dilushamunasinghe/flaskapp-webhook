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
            # Log the request payload
            logging.info(f"Webhook triggered: {request.json}")

            # Optional: Validate the request payload (customize according to your needs)
            if 'ref' in request.json and 'main' in request.json['ref']:
                # Trigger the deployment script
                os.system('sh /home/ubuntu/flaskapp-webhook/my_flask_app/deploy.sh')
                return jsonify({"message": "Deployment initiated successfully"}), 200
            else:
                logging.warning("Webhook triggered but not targeting master branch.")
                return jsonify({"message": "Not targeting master branch"}), 400
        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    return jsonify({"message": "Invalid request method"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
