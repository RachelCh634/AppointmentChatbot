from flask import Flask, request, jsonify
from flask_cors import CORS
from pages.appointment_processor import handle_appointment_request
from pages.google_login import handle_google_login
app = Flask(__name__)

CORS(app)  

@app.route('/appointment', methods=['POST'])
def appointment():
    data = request.get_json() 
    text = data.get('text') 
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1] 
    result = handle_appointment_request(text, token)
    return jsonify(result)

@app.route('/google-login', methods=['POST'])
def google_login():
    data = request.json
    print("Received data:", data) 
    google_token = data.get('googleToken')

    if not google_token:
        return jsonify({'error': 'Missing Google token'}), 400

    return handle_google_login(google_token)


if __name__ == '__main__':
    app.run(debug=True)

