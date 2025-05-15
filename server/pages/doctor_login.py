import jwt
from flask import jsonify
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set")

"""The doctor's details are in the ENV file to allow for easy changes."""

DOCTOR_USERNAME = os.environ.get('DOCTOR_USERNAME')
DOCTOR_PASSWORD = os.environ.get('DOCTOR_PASSWORD')
DOCTOR_FULL_NAME = os.environ.get('DOCTOR_FULL_NAME', 'Dr. ' + DOCTOR_USERNAME if DOCTOR_USERNAME else '')

if not DOCTOR_USERNAME or not DOCTOR_PASSWORD:
    raise ValueError("DOCTOR_USERNAME and DOCTOR_PASSWORD environment variables must be set")

DOCTORS = {
    DOCTOR_USERNAME: {
        "password": DOCTOR_PASSWORD,  
        "name": DOCTOR_FULL_NAME,
    }
}

def handle_doctor_login(username, password):
    """
    Handle the login for the doctor.
    """
    if username not in DOCTORS:
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401
    
    doctor = DOCTORS[username]
    is_password_valid = False
    
    if username == DOCTOR_USERNAME and password == DOCTOR_PASSWORD:
        is_password_valid = True
    
    if not is_password_valid:
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401
    
    token_payload = {
        'name': doctor["name"],
        'role': 'doctor'
    }
    
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")
    
    return jsonify({
        "success": True,
        "token": token,
        "doctorName": doctor["name"],
        "message": "Login successful"
    })
