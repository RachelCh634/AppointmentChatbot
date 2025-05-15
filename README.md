## 🩺 Appointment Chatbot with Google Calendar Integration

### 🚀 Project Overview
This project is a web-based chatbot that allows users to schedule doctor appointments.

#### 🎯 Objectives
- Let users schedule doctor appointments via a natural chat conversation.
- Check availability based on clinic working days and hours.
- Prevent double-bookings using Google Calendar API.
- Automatically create confirmed appointments in the doctor’s calendar.
- Provide doctors with an admin interface to view their upcoming appointments.

---
#### 🗂️ Folder Structure
```markdown
project-root/
├── server/
│   ├── app.py
│   ├── requirements.txt
│   ├── credentials.json
│   ├── .env
│   └── pages/
├── client/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── components/
└── README.md
```
### 🧩 System Architecture

#### 📱 Frontend (React)
- Google login via OAuth 2.0.
- Nice and easy UI for intuitive interactions.
- Chat booking - Users can chat with the bot to schedule appointments.
- Doctor dashboard showing all future confirmed appointments.

#### 🖥️ Backend (Python)
- Message parsing: Understanding user messages, extracting date/time, detecting intent.
- Natural language date/time parsing using libraries like parsedatetime or dateparser.
- Google Calendar sync: Check availability, avoid conflicts.
- Appointment creation: Automatically book available time slots in Google Calendar.
- Error handling: Friendly responses to unclear or invalid requests.

## 🔧 Setup & Run Instructions

### 1. Server Setup

#### Requirements:
- Python 3.8+

#### Install dependencies:

```bash
cd server
pip install -r requirements.txt
```

#### 🔐 Google Calendar API Credentials
To connect with Google Calendar, you must provide a service account key file named credentials.json.

#### Steps to set it up:
- Go to Google Cloud Console.
- Create a Service Account (under "IAM & Admin" → "Service Accounts").
- Grant it the "Editor" role (or specific Calendar permissions).
- Create and download a JSON key – save it as credentials.json inside the server/ folder.
- Share your Google Calendar with the service account's email (found in the JSON file), with "Make changes to events" permission.

#### ⚠️ Do not upload credentials.json to GitHub! Make sure it's listed in .gitignore.

#### Run the server:

Run server:
```bash
python app.py
```
Default server address: http://localhost:5000

### 2. React Client Setup

Requirements:
Node.js 14+

Install and run:

```bash
cd client
npm install
npm start
```

Client will run on http://localhost:3000.

### 🧪 Test Scenarios
- ✅ Booking a valid appointment.
- ❌ Attempting to book outside business hours or on weekends.
- 🔁 Detecting and blocking overlapping appointments.
- 💬 Chatting with phrases like: “Can I book an appointment for tomorrow at 9am?”
- 👨‍⚕️ Viewing scheduled appointments in the doctor’s dashboard.

### 📌 Notes
For unsupported messages, the bot responds with helpful clarification prompts.








