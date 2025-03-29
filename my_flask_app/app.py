from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    import os
    os.system('sh /home/ec2-user/my_flask_app/deploy.sh')
    return "Webhook triggered", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
