from flask import Flask, request, jsonify
from flask_cors import CORS
from pages.appointment_processor import handle_appointment_request
from pages.google_login import handle_google_login
import uuid

app = Flask(__name__)

CORS(app)  

conversation_history = {}  

@app.route('/appointment', methods=['POST', 'OPTIONS'])
def appointment():
    
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.json
    text = data.get('text', '')
    session_id = data.get('session_id', '')
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({"role": "user", "content": text})
    
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    result = handle_appointment_request(text, token, conversation_history[session_id])
    conversation_history[session_id].append({"role": "assistant", "content": result["message"]})
    response = jsonify({
        "message": result["message"],
        "status": result["status"],
        "session_id": session_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')


    return response
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

