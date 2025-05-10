import requests
import secrets
import jwt
import json
import os
from flask import jsonify

secret_key = 'sdf8sdfhsd8fh328fhsd'
users_file = 'users.json'

def load_users():
    if not os.path.exists(users_file):
        return []
    with open(users_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def find_user_by_email(email, users):
    for user in users:
        if user['email'] == email:
            return user
    return None

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

        users = load_users()

        user = find_user_by_email(google_user_info['email'], users)
        if user:
            print(f"Existing user found: {user['email']}")
        else:
            print("No user found. Creating new user...")
            user = {
                'id': secrets.token_hex(8),
                'email': google_user_info['email'],
                'fullName': google_user_info['name'],
                'displayName': google_user_info.get('given_name', ''),
                'phoneNumber': '',
                'city': 'לא צוין',
                'isSeller': False,
                'password': secrets.token_hex(16)
            }
            users.append(user)
            print("Saving new user...")
            save_users(users)

        payload = {'id': user['id'], 'email': user['email']}
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        print("User login success. Returning token and username.")
        return jsonify({
            'token': token,
            'userName': user['displayName'] or user['fullName']})


    except Exception as e:
        print(f'Google login error (main except): {e}')
        return jsonify({'error': 'Server error'}), 500
