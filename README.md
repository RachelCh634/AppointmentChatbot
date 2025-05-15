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

##### Steps to set it up:
- Go to Google Cloud Console.
- Create a Service Account (under "IAM & Admin" → "Service Accounts").
- Grant it the "Editor" role (or specific Calendar permissions).
- Create and download a JSON key – save it as credentials.json inside the server/ folder.
- Share your Google Calendar with the service account's email (found in the JSON file), with "Make changes to events" permission.

##### ⚠️ Do not upload credentials.json to GitHub! Make sure it's listed in .gitignore.

#### 🔐 .env File – Required Environment Variables
The application requires a .env file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key_here
DOCTOR_USERNAME=your_username_here
DOCTOR_PASSWORD=your_password_here
DOCTOR_FULL_NAME=your_full_name_here
CALENDAR_ID=your_calendar_id@group.calendar.google.com
```
##### Description:
- SECRET_KEY – A secret string used by the server for internal encryption. Required.
- DOCTOR_USERNAME – The doctor's login username.
- DOCTOR_PASSWORD – The doctor's login password.
- DOCTOR_FULL_NAME – The doctor's full name.
- CALENDAR_ID – The ID of the Google Calendar where appointments will be created.
##### 🛡️ Important: Never share your .env file. Make sure it's listed in your .gitignore

#### 📅 Google Calendar Setup
To allow the app to create events in your Google Calendar:
- Open Google Calendar.
- On the left, hover over the desired calendar → click ⋮ → Settings and sharing.
- Scroll to the Calendar ID section under Integrate calendar and copy it.
- Paste it into your .env file as the value for CALENDAR_ID.

#### 👥 Share the Calendar with Your Service Account
In the same calendar settings page, scroll to Share with specific people.
- Click Add people.
- In your credentials.json file, locate the "client_email" field: ``` "client_email": "your-service-account@your-project.iam.gserviceaccount.com" ``` 
- Paste that email address into the sharing field.
- Grant it permission to Make changes to events.

#### Run the server:
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








