from flask import Flask, request, jsonify
from flask_cors import CORS
from appointment_processor import handle_appointment_request
from users import handle_google_login
app = Flask(__name__)

CORS(app)  

@app.route('/appointment', methods=['POST'])
def appointment():
    data = request.get_json() 
    text = data.get('text') 
    result = handle_appointment_request(text)
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

