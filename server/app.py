from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from pages.appointment_processor import handle_appointment_request
from pages.google_login import handle_google_login
from pages.doctor_login import handle_doctor_login
from pages.calendar_utils import get_upcoming_appointments
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set")

app = Flask(__name__)

CORS(app)  

@app.route('/appointment', methods=['POST', 'OPTIONS'])
def appointment():
    """
    Navigates to the function for handling requests and messages from the user.
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.json
    text = data.get('text', '')    
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    result = handle_appointment_request(text, token)
    response = jsonify({
        "message": result["message"],
        "status": result["status"],
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/doctor-login', methods=['POST', 'OPTIONS'])
def doctor_login():
    """
    Navigates to the doctor login function
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400

    return handle_doctor_login(username, password)


@app.route('/google-login', methods=['POST'])
def google_login():
    """
    Navigates to the google login function
    """
    data = request.json
    print("Received data:", data) 
    google_token = data.get('googleToken')

    if not google_token:
        return jsonify({'error': 'Missing Google token'}), 400

    return handle_google_login(google_token)


@app.route('/upcoming-appointments', methods=['GET', 'OPTIONS'])
def get_upcoming_appointments_api():
    """
    Navigates to the view all upcoming events function and verifies that the user is a doctor
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response
    
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    if not token:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        if payload.get('role') != 'doctor':
            return jsonify({'error': 'Access denied. Doctor privileges required'}), 403
        days = request.args.get('days', default=30, type=int)
        appointments = get_upcoming_appointments(days)
        
        return jsonify({
            'appointments': appointments,
            'count': len(appointments),
            'doctorName': payload.get('name')
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired. Please log in again'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token. Please log in again'}), 401


if __name__ == '__main__':
    app.run(debug=True)

