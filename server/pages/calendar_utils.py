from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pytz

SERVICE_ACCOUNT_FILE = 'credentials.json'
CALENDAR_ID = '86d7e091f847634b5f8532e3542dc427b914b7473d4e46cce98a7ee4be877236@group.calendar.google.com'
SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

def is_time_available(start_time: datetime, duration_minutes=30) -> bool:
    if start_time.tzinfo is None:
        jerusalem = pytz.timezone('Asia/Jerusalem')
        start_time = jerusalem.localize(start_time).astimezone(timezone.utc)
    else:
        start_time = start_time.astimezone(timezone.utc)
    end_time = start_time + timedelta(minutes=duration_minutes)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return len(events_result.get('items', [])) == 0


def create_appointment_event(start_time: datetime, user_name, duration_minutes=30):
    end_time = start_time + timedelta(minutes=duration_minutes-1)
    event = {
        'summary': f'Appointment for {user_name}',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Jerusalem'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Jerusalem'},
    }
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event

