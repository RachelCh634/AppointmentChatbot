from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pytz
import re
import os
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = 'credentials.json'
CALENDAR_ID = os.environ.get('CALENDAR_ID', '')
SCOPES = ['https://www.googleapis.com/auth/calendar']

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
except Exception as e:
    print(f"Error initializing Google Calendar service: {e}")
    service = None

def is_calendar_available():
    """
    Check if the Google Calendar service is available and properly configured.
    """
    if not service:
        return False
    if not CALENDAR_ID:
        return False
    
    try:
        service.calendarList().get(calendarId=CALENDAR_ID).execute()
        return True
    except HttpError as e:
        print(f"Calendar access error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error checking calendar availability: {e}")
        return False

def is_time_available(start_time: datetime, duration_minutes=30) -> bool:
    """
    Check if the given time slot is available.
    """
    if not service or not CALENDAR_ID:
        print("Calendar service not available. Cannot check time availability.")
        return False
        
    try:
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
    except HttpError as e:
        print(f"Google Calendar API error when checking availability: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error when checking time availability: {e}")
        return False


def create_appointment_event(start_time: datetime, user_name, user_email, duration_minutes=30):
    """
    Create a meeting event on the clinic calendar 
    """
    if not service or not CALENDAR_ID:
        print("Calendar service not available. Cannot create appointment.")
        return None
        
    try:
        print(f"Creating appointment event for {user_name} at {start_time}")
        end_time = start_time + timedelta(minutes=duration_minutes-1)
        event = {
            'summary': f'Appointment for {user_name}',
            'description': f'Contact Information:\nName: {user_name}' + 
                          (f'\nEmail: {user_email}' if user_email else ''),
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Jerusalem'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Jerusalem'},
        }
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return created_event
    except HttpError as e:
        print(f"Google Calendar API error when creating appointment: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error when creating appointment: {e}")
        return None


def get_upcoming_appointments(days=30):
    """
    Fetch upcoming appointments from the clinic calendar.
    """
    if not service or not CALENDAR_ID:
        print("Calendar service not available. Cannot fetch appointments.")
        return []
        
    try:
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days)).isoformat()

        print(f"Fetching appointments from {time_min} to {time_max}")

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            print('No upcoming appointments found.')
            return []

        appointments = []
     
        for event in events:
            summary = event.get('summary', '')
            if 'Appointment for' not in summary:
                continue

            description = event.get('description', '')
            name_match = re.search(r'Name: (.+?)(?:\n|$)', description)
            email_match = re.search(r'Email: (.+?)(?:\n|$)', description)

            appointment = {
                'summary': summary,
                'start': event['start'].get('dateTime'),
                'end': event['end'].get('dateTime'),
                'user_name': name_match.group(1).strip() if name_match else None,
                'user_email': email_match.group(1).strip() if email_match else None,
            }

            appointments.append(appointment)
            print(appointments)
        return appointments

    except HttpError as e:
        print(f"Google Calendar API error when fetching appointments: {e}")
        return []
    except Exception as e:
        print(f"Error fetching appointments from Google Calendar: {e}")
        return []
