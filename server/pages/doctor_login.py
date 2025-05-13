import jwt
import datetime
from flask import jsonify
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set")

DOCTORS = {
    "dr.smith": {
        "password": "pbkdf2:sha256:150000$abc123$abcdef1234567890abcdef1234567890abcdef1234567890",  
        "name": "Dr. John Smith",
    }
}


def handle_doctor_login(username, password):
    """
    מטפל בהתחברות של רופא
    """
    if username not in DOCTORS:
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401
    
    doctor = DOCTORS[username]
    is_password_valid = False
    if username == "dr.smith" and password == "password123":
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
