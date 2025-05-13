import requests
import jwt
from flask import jsonify
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set")


def handle_google_login(google_token):
    try:
        print(f"Received token: {google_token}")

        if not google_token:
            return jsonify({'error': 'Google token is required'}), 400

        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {google_token}'}
        )
        
        if response.status_code != 200:
            print(f'Google API error: Status {response.status_code}, Response: {response.text}')
            return jsonify({'error': 'Failed to authenticate with Google'}), 401

        if response.text.strip():
            try:
                google_user_info = response.json()
                print(f"Parsed user info: {google_user_info}")
            except ValueError as e:
                print(f'Error parsing JSON: {e}')
                return jsonify({'error': 'Invalid JSON response from Google'}), 500
        else:
            print("Empty response from Google")
            return jsonify({'error': 'Empty response from Google'}), 500

        payload = {
            'email': google_user_info['email'],
            'name': google_user_info.get('given_name', '') or google_user_info['name'],
            'role': 'user'
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        print("User login success. Returning token and username.")
        return jsonify({
            'token': token,
            'userName': payload['name'],
        })

    except Exception as e:
        print(f'Google login error (main except): {e}')
        return jsonify({'error': 'Server error'}), 500
