import re
from datetime import datetime, timedelta
import jwt
import pytz
from pages.calendar_utils import is_time_available, create_appointment_event
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY environment variable is not set")

def parse_appointment_request(text):
    """
    Simple function to extract date and time from a text message in English.
    Returns a dictionary with date and time if found, or None if not.
    """
    text = text.lower()
    
    appointment_details = {
        "datetime": None,
        "valid": False
    }
    
    date_patterns = [
        r'(\d{1,2})[\/\.-](\d{1,2})(?:[\/\.-](\d{2,4}))?',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{1,2})(?:\s+|-)(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)',  # DD Month
        r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)(?:\s+|-)(\d{1,2})',  # Month DD
        r'(today|tomorrow|next day)'  # Relative dates
    ]
    
    # Weekday patterns (English and Hebrew)
    weekday_patterns = [
        # English weekdays
        r'(this|next)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)',
        # Hebrew weekdays
        r'(?:ב|ה)?(יום\s+)?(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)(?:\s+הבא)?'
    ]
    
    # Time patterns
    time_patterns = [
        r'(\d{1,2}):(\d{2})',  # HH:MM
        r'at\s+(\d{1,2})(?::(\d{2}))?',  # at HH or at HH:MM
        r'(\d{1,2})(?::(\d{2}))?\s+(am|pm)'  # HH:MM am/pm or HH am/pm
    ]
    
    # Extract date
    extracted_date = None
    
    # First try to extract from weekday patterns
    for pattern in weekday_patterns:
        weekday_match = re.search(pattern, text)
        if weekday_match:
            # Get current date
            today = datetime.now().date()
            today_weekday = today.weekday()  # 0 is Monday, 6 is Sunday
            
            # Convert matched weekday to number (0-6)
            matched_weekday = None
            
            # Check if it's English or Hebrew
            weekday_text = weekday_match.group(2) if len(weekday_match.groups()) > 1 else weekday_match.group(1)
            
            # English weekdays
            english_weekdays = {
                'monday': 0, 'mon': 0,
                'tuesday': 1, 'tue': 1,
                'wednesday': 2, 'wed': 2,
                'thursday': 3, 'thu': 3,
                'friday': 4, 'fri': 4,
                'saturday': 5, 'sat': 5,
                'sunday': 6, 'sun': 6
            }
            
            # Hebrew weekdays
            hebrew_weekdays = {
                'ראשון': 6,  # Sunday
                'שני': 0,    # Monday
                'שלישי': 1,  # Tuesday
                'רביעי': 2,  # Wednesday
                'חמישי': 3,  # Thursday
                'שישי': 4,   # Friday
                'שבת': 5     # Saturday
            }
            
            # Try to match with English weekdays
            if weekday_text.lower() in english_weekdays:
                matched_weekday = english_weekdays[weekday_text.lower()]
            # Try to match with Hebrew weekdays
            elif weekday_text in hebrew_weekdays:
                matched_weekday = hebrew_weekdays[weekday_text]
            
            if matched_weekday is not None:
                is_next = (len(weekday_match.groups()) > 1 and weekday_match.group(1) == 'next') or 'הבא' in weekday_match.group(0)
    
                if is_next or matched_weekday <= today_weekday:
        # עבור "הבא" או אם היום כבר עבר השבוע
                    days_to_add = ((matched_weekday - today_weekday) + 7) % 7
                    if days_to_add == 0:
                        days_to_add = 7  # לוודא שזה לא היום עצמו
                else:
                # עבור יום שעוד לא הגיע השבוע ואין "הבא"
                    days_to_add = (matched_weekday - today_weekday) % 7

                extracted_date = today + timedelta(days=days_to_add)
                break

    # If no weekday found, try other date patterns
    if not extracted_date:
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                if 'today' in date_match.groups():
                    extracted_date = datetime.now().date()
                elif 'tomorrow' in date_match.groups():
                    extracted_date = (datetime.now() + timedelta(days=1)).date()
                elif 'next day' in date_match.groups():
                    extracted_date = (datetime.now() + timedelta(days=1)).date()
                elif len(date_match.groups()) >= 2:
                    # Check if first group is a month name
                    if date_match.group(1) and not date_match.group(1).isdigit():
                        month = _month_to_number(date_match.group(1))
                        day = int(date_match.group(2))
                        year = datetime.now().year
                    # Otherwise assume numeric format
                    else:
                        first_num = int(date_match.group(1))
                        second_num = int(date_match.group(2))
                        
                        # Try to determine if MM/DD or DD/MM format
                        # For simplicity, assume numbers > 12 are days, otherwise use American format (MM/DD)
                        if first_num > 12:  # Must be DD/MM
                            day, month = first_num, second_num
                        elif second_num > 12:  # Must be MM/DD
                            month, day = first_num, second_num
                        else:  # Ambiguous, default to MM/DD
                            month, day = first_num, second_num
                        
                        year = int(date_match.group(3)) if date_match.groups()[2] and date_match.group(3).isdigit() else datetime.now().year
                        if year < 100:  # Handle 2-digit years
                            year += 2000
                    
                    # Validate date
                    try:
                        extracted_date = datetime(year, month, day).date()
                    except ValueError:
                        continue
                
                if extracted_date:
                    break
    
    # Extract time
    extracted_time = None
    for pattern in time_patterns:
        time_match = re.search(pattern, text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) and time_match.group(2).isdigit() else 0
            
            # Adjust hours for AM/PM if specified
            if len(time_match.groups()) > 2 and time_match.group(3):
                if time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                elif time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
            
            # Validate time
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                extracted_time = (hour, minute)
                break
    
    # Combine date and time if both are found
    if extracted_date and extracted_time:
        hour, minute = extracted_time
        try:
            # Create datetime object
            appointment_datetime = datetime.combine(
                extracted_date, 
                datetime.min.time().replace(hour=hour, minute=minute)
            )
            
            # Localize to Jerusalem timezone as used in calendar_utils.py
            jerusalem = pytz.timezone('Asia/Jerusalem')
            appointment_datetime = jerusalem.localize(appointment_datetime)
            
            appointment_details["datetime"] = appointment_datetime
            appointment_details["valid"] = True
        except ValueError:
            pass
    
    return appointment_details

def _month_to_number(month_name):
    """Convert month name to number"""
    months = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    return months.get(month_name.lower(), 1)  # Default: January

def check_greeting_or_thanks(text):
    """
    Check if the message is a greeting or thank you message and return appropriate response
    
    Args:
        text (str): The user's message
        
    Returns:
        str or None: Response message if it's a greeting or thank you, None otherwise
    """
    # Convert to lowercase for easier matching
    text_lower = text.lower()
    
    # Thank you patterns
    thank_you_patterns = [
        r'\bthank(?:s| you)\b',
        r'\bthanks\b',
        r'\bty\b',
        r'\bthx\b',
        r'\bappreciate\b',
        r'\bgrateful\b',
        # Hebrew thank you patterns
        r'\bתודה\b',
        r'\bתודה רבה\b',
        r'\bתודה לך\b',
        r'\bאני מודה לך\b'
    ]
    
    # Good day/nice day patterns
    good_day_patterns = [
        r'\bgood day\b',
        r'\bhave a nice day\b',
        r'\bhave a good one\b',
        r'\bnice day\b',
        # Hebrew good day patterns
        r'\bיום טוב\b',
        r'\bיום נעים\b',
        r'\bיום מוצלח\b',
        r'\bהמשך יום נעים\b',
        r'\bהמשך יום טוב\b',
        r'\bשיהיה לך יום\b'
    ]
    
    # General greeting patterns
    greeting_patterns = [
        r'\bhello\b',
        r'\bhi\b',
        r'\bhey\b',
        r'\bgood morning\b',
        r'\bgood afternoon\b',
        r'\bgood evening\b',
        # Hebrew greeting patterns
        r'\bשלום\b',
        r'\bהיי\b',
        r'\bבוקר טוב\b',
        r'\bצהריים טובים\b',
        r'\bערב טוב\b',
        r'\bלילה טוב\b',
        r'\bמה שלומך\b',
        r'\bמה נשמע\b'
    ]
    
    # Check for thank you patterns
    for pattern in thank_you_patterns:
        if re.search(pattern, text_lower):
            return "Please! I was happy to help, have a nice day."
    
    # Check for good day patterns
    for pattern in good_day_patterns:
        if re.search(pattern, text_lower):
            return "Thank you! Have a wonderful day too!"
    
    # Check for greeting patterns
    for pattern in greeting_patterns:
        if re.search(pattern, text_lower):
            return "Hello! How can I help you schedule an appointment today?"
    
    # If no patterns match, return None
    return None

def handle_appointment_request(text, token):
    """
    Handle a new appointment request
    
    Args:
        text (str): The user's message
        token (str): Authentication token (if any)
        conversation_history (list): History of the conversation
    
    Returns:
        dict: Response with message and status
    """
    # Check if the message is a greeting or thank you
    greeting_response = check_greeting_or_thanks(text)
    if greeting_response:
        return {
            "message": greeting_response,
            "status": "success"
        }
    
    # Parse the message using our function instead of OpenAI
    appointment_details = parse_appointment_request(text)
    
    user_name = "Anonymous"
    if token:
        try:
            user_info = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_email = user_info.get('email')    
            user_name = user_info.get('name', 'Guest')
        except Exception as e:
            pass

    if not appointment_details["valid"]:
        return {
            "message": "I couldn't understand the appointment details. Please provide a clear date and time.",
            "status": "error"
        }
    
    # Get the datetime object
    appointment_datetime = appointment_details["datetime"]
    
    if not is_within_clinic_hours(appointment_datetime):
        return {
            "message": f"The requested time {appointment_datetime.strftime('%Y-%m-%d %H:%M')} is outside of clinic hours. The clinic is open Sunday–Thursday 08:00–19:00 and Friday 08:00–12:00.",
            "status": "error"
        }
    
    is_valid_time, time_error_message = is_valid_appointment_time(appointment_datetime)
    if not is_valid_time:
        return {
            "message": time_error_message,
            "status": "error"
        }
    # Check if the time is available using your existing function
    is_available = is_time_available(appointment_datetime)
    
    if not is_available:
        return {
            "message": f"The appointment on {appointment_datetime.strftime('%Y-%m-%d')} at {appointment_datetime.strftime('%H:%M')} is not available. Please choose another time.",
            "status": "error"
        }
    
    # Book the appointment using your existing function
    try:
        event = create_appointment_event(appointment_datetime, user_name, user_email)
        
        return {
            "message": f"Appointment scheduled for {appointment_datetime.strftime('%Y-%m-%d')} at {appointment_datetime.strftime('%H:%M')}.",
            "status": "success",
            "event_id": event.get('id')
        }
    except Exception as e:
        return {
            "message": f"An error occurred while booking the appointment: {str(e)}",
            "status": "error"
        }


def is_within_clinic_hours(dt):
    """
    בדיקה האם המועד המבוקש הוא בזמן פתיחת המרפאה.
    קלט: dt - אובייקט datetime (עם timezone)
    פלט: True אם בתוך שעות פעילות, אחרת False
    """
    if not dt:
        return False

    # המרפאה פועלת ב־Asia/Jerusalem timezone
    jerusalem = pytz.timezone('Asia/Jerusalem')
    local_dt = dt.astimezone(jerusalem)

    weekday = local_dt.weekday()  # 0=Monday, ..., 6=Sunday
    hour = local_dt.hour
    minute = local_dt.minute

    if weekday in [6, 0, 1, 2, 3]:  # ימים ראשון עד חמישי (Sunday=6, Monday=0, ..., Thursday=3)
        return 8 <= hour < 19 or (hour == 19 and minute == 0)
    elif weekday == 4:  # שישי (Friday)
        return 8 <= hour < 12 or (hour == 12 and minute == 0)
    else:
        return False  # שבת (Saturday=5)


def is_valid_appointment_time(appointment_datetime):
    minute = appointment_datetime.minute
    if minute not in [0, 30]:
        return False, "Appointments must start at the hour (XX:00) or half hour (XX:30). Please choose a valid time."
    return True, ""



