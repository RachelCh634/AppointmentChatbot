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

user_sessions = {}

def get_user_session(user_id):
    """Get user session data"""
    return user_sessions.get(user_id, {})

def set_user_session(user_id, data):
    """Set user session data"""
    user_sessions[user_id] = data

def clear_user_session(user_id):
    """Clear user session data"""
    if user_id in user_sessions:
        del user_sessions[user_id]

def get_user_id_from_token(token):
    """Extract user ID from token"""
    if not token:
        return "anonymous"
    
    try:
        user_info = jwt.decode(token, secret_key, algorithms=['HS256'])
        return user_info.get('email', 'anonymous')
    except:
        return "anonymous"

def check_cancel_request(text):
    """
    Check if user wants to cancel the current booking process
    """
    cancel_patterns = [
        r'\bcancel\b',
        r'\bstop\b',
        r'\bnever mind\b',
        r'\bforget it\b',
        r'\bביטול\b',
        r'\bתעזוב\b',
        r'\bלא רוצה\b'
    ]
    
    text_lower = text.lower()
    for pattern in cancel_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def is_date_in_past(date_obj):
    """
    Check if the given date is in the past
    """
    today = datetime.now().date()
    return date_obj < today

def is_datetime_in_past(datetime_obj):
    """
    Check if the given datetime is in the past
    """
    jerusalem = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(jerusalem)
    
    # Convert datetime_obj to Jerusalem timezone if it's not already
    if datetime_obj.tzinfo is None:
        datetime_obj = jerusalem.localize(datetime_obj)
    else:
        datetime_obj = datetime_obj.astimezone(jerusalem)
    
    return datetime_obj < now

def parse_appointment_request(text):
    """
    Function to extract date and time from a text message.
    Returns a dictionary with date, time, and validation status.
    """
    text = text.lower()
    
    appointment_details = {
        "datetime": None,
        "date_only": None,
        "time_only": None,
        "valid": False,
        "has_date": False,
        "has_time": False
    }
    
    date_patterns = [
        r'(\d{1,2})[\/\.-](\d{1,2})(?:[\/\.-](\d{2,4}))?',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{1,2})(?:\s+|-)(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)',  # DD Month
        r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)(?:\s+|-)(\d{1,2})',  # Month DD
        r'(today|tomorrow|next day)'  
    ]
    
    weekday_patterns = [
        r'(this|next)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)',
        r'(?:ב|ה)?(יום\s+)?(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)(?:\s+הבא)?'
    ]
    
    time_patterns = [
        r'(\d{1,2})(?::(\d{2}))?\s+(am|pm)',  
        r'(\d{1,2}):(\d{2})',  # HH:MM
        r'at\s+(\d{1,2})(?::(\d{2}))?(?:\s+(am|pm))?'  # at HH or at HH:MM with optional am/pm
    ]

    extracted_date = None
    
    for pattern in weekday_patterns:
        weekday_match = re.search(pattern, text)
        if weekday_match:
            today = datetime.now().date()
            today_weekday = today.weekday()  
            
            matched_weekday = None
            weekday_text = ""
            
            if len(weekday_match.groups()) > 1:
                weekday_text = weekday_match.group(2) if weekday_match.group(2) else ""
            else:
                weekday_text = weekday_match.group(1) if weekday_match.group(1) else ""
            
            english_weekdays = {
                'monday': 0, 'mon': 0,
                'tuesday': 1, 'tue': 1,
                'wednesday': 2, 'wed': 2,
                'thursday': 3, 'thu': 3,
                'friday': 4, 'fri': 4,
                'saturday': 5, 'sat': 5,
                'sunday': 6, 'sun': 6
            }
            
            hebrew_weekdays = {
                'ראשון': 6,  
                'שני': 0,   
                'שלישי': 1,  
                'רביעי': 2,  
                'חמישי': 3,  
                'שישי': 4,  
                'שבת': 5     
            }
            
            if weekday_text and weekday_text.lower() in english_weekdays:
                matched_weekday = english_weekdays[weekday_text.lower()]
            elif weekday_text and weekday_text in hebrew_weekdays:
                matched_weekday = hebrew_weekdays[weekday_text]

            if matched_weekday is not None:
                is_next = False
                if len(weekday_match.groups()) > 1 and weekday_match.group(1) == 'next':
                    is_next = True
                elif 'הבא' in weekday_match.group(0):
                    is_next = True

                if is_next:
                    days_to_add = ((matched_weekday - today_weekday) + 7) % 7
                    if is_day_in_current_hebrew_week(matched_weekday) == False:
                        days_to_add += 7
                else:
                    days_to_add = ((matched_weekday - today_weekday) + 7) % 7
                    if days_to_add == 0:
                        days_to_add = 7

                extracted_date = today + timedelta(days=days_to_add)
                break

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
                    if date_match.group(1) and not date_match.group(1).isdigit():
                        month = _month_to_number(date_match.group(1))
                        day = int(date_match.group(2))
                        year = datetime.now().year
                    elif date_match.group(2) and not date_match.group(2).isdigit():
                        day = int(date_match.group(1))
                        month = _month_to_number(date_match.group(2))
                        year = datetime.now().year
                    else:
                        first_num = int(date_match.group(1))
                        second_num = int(date_match.group(2))
                        
                        if first_num > 12: 
                            day, month = first_num, second_num
                        elif second_num > 12: 
                            month, day = first_num, second_num
                        else:  
                            day, month = first_num, second_num
                        
                        year = int(date_match.group(3)) if date_match.groups()[2] and date_match.group(3) and date_match.group(3).isdigit() else datetime.now().year
                        if year < 100:  
                            year += 2000
                    
                    try:
                        extracted_date = datetime(year, month, day).date()
                    except ValueError:
                        continue
                
                if extracted_date:
                    break
    
    extracted_time = None
    for pattern in time_patterns:
        time_match = re.search(pattern, text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) and time_match.group(2).isdigit() else 0
            
            if len(time_match.groups()) > 2 and time_match.group(3):
                if time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                elif time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                extracted_time = (hour, minute)
                break
    
    appointment_details["has_date"] = extracted_date is not None
    appointment_details["has_time"] = extracted_time is not None
    appointment_details["date_only"] = extracted_date
    appointment_details["time_only"] = extracted_time
    
    if extracted_date and extracted_time:
        hour, minute = extracted_time
        try:
            appointment_datetime = datetime.combine(
                extracted_date, 
                datetime.min.time().replace(hour=hour, minute=minute)
            )
            
            jerusalem = pytz.timezone('Asia/Jerusalem')
            appointment_datetime = jerusalem.localize(appointment_datetime)
            
            appointment_details["datetime"] = appointment_datetime
            appointment_details["valid"] = True
        except ValueError:
            pass
    
    return appointment_details

def _month_to_number(month_name):
    """
    Convert month name to number
    """
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
    return months.get(month_name.lower(), 1)  

def check_greeting_or_thanks(text):
    """
    Check if the message is a greeting or thank you message and return appropriate response.
    """
    text_lower = text.lower()
    
    thank_you_patterns = [
        r'\bthank(?:s| you)\b',
        r'\bthanks\b',
        r'\bty\b',
        r'\bthx\b',
        r'\bappreciate\b',
        r'\bgrateful\b',
        r'\bתודה\b',
        r'\bתודה רבה\b',
        r'\bתודה לך\b',
        r'\bאני מודה לך\b'
    ]
    
    good_day_patterns = [
        r'\bgood day\b',
        r'\bhave a nice day\b',
        r'\bhave a good one\b',
        r'\bnice day\b',
        r'\bיום טוב\b',
        r'\bיום נעים\b',
        r'\bיום מוצלח\b',
        r'\bהמשך יום נעים\b',
        r'\bהמשך יום טוב\b',
        r'\bשיהיה לך יום\b'
    ]
    
    greeting_patterns = [
        r'\bhello\b',
        r'\bhi\b',
        r'\bhey\b',
        r'\bgood morning\b',
        r'\bgood afternoon\b',
        r'\bgood evening\b',
        r'\bשלום\b',
        r'\bהיי\b',
        r'\bבוקר טוב\b',
        r'\bצהריים טובים\b',
        r'\bערב טוב\b',
        r'\bלילה טוב\b',
        r'\bמה שלומך\b',
        r'\bמה נשמע\b'
    ]
    
    for pattern in thank_you_patterns:
        if re.search(pattern, text_lower):
            return "Have fun! I was happy to help, have a nice day."
    
    for pattern in good_day_patterns:
        if re.search(pattern, text_lower):
            return "Thank you! Have a wonderful day too!"
    
    for pattern in greeting_patterns:
        if re.search(pattern, text_lower):
            return "Hello! How can I help you schedule an appointment today?"
    
    return None

def is_date_on_saturday(date_obj):
    """
    Check if the given date falls on Saturday (weekday 5 in Python)
    """
    return date_obj.weekday() == 5

def handle_appointment_request(text, token):
    """
    Handling a new appointment request with support for partial input (date only or time only).
    """
    greeting_response = check_greeting_or_thanks(text)
    if greeting_response:
        return {
            "message": greeting_response,
            "status": "success"
        }
    
    user_id = get_user_id_from_token(token)
    user_session = get_user_session(user_id)
    
    # Check if user wants to cancel
    if check_cancel_request(text):
        clear_user_session(user_id)
        return {
            "message": "Appointment booking cancelled. How else can I help you?",
            "status": "success"
        }
    
    appointment_details = parse_appointment_request(text)
    
    user_name = "Anonymous"
    user_email = None
    
    if token:
        try:
            user_info = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_email = user_info.get('email')    
            user_name = user_info.get('name', 'Guest')
        except Exception as e:
            pass

    # Check if user is in the middle of appointment booking process
    if 'pending_date' in user_session:
        # User previously provided date, now checking for time
        if appointment_details["has_time"]:
            # Combine saved date with new time
            saved_date = user_session['pending_date']
            hour, minute = appointment_details["time_only"]
            
            try:
                appointment_datetime = datetime.combine(
                    saved_date, 
                    datetime.min.time().replace(hour=hour, minute=minute)
                )
                
                jerusalem = pytz.timezone('Asia/Jerusalem')
                appointment_datetime = jerusalem.localize(appointment_datetime)
                
                # Check if the datetime is in the past
                if is_datetime_in_past(appointment_datetime):
                    return {
                        "message": f"The requested time {appointment_datetime.strftime('%Y-%m-%d %H:%M')} is in the past. Please choose a different time for {saved_date.strftime('%B %d, %Y')}.",
                        "status": "waiting_for_time"
                    }
                
                # Process the complete appointment
                result = process_complete_appointment(appointment_datetime, user_name, user_email)
                
                # If appointment failed due to time issues, keep the date in session
                if result["status"] == "error" and ("not available" in result["message"] or "outside of clinic hours" in result["message"] or "must start at" in result["message"]):
                    return {
                        "message": f"{result['message']} Please choose a different time for {saved_date.strftime('%B %d, %Y')}.",
                        "status": "waiting_for_time"
                    }
                
                clear_user_session(user_id)
                return result
                
            except ValueError:
                return {
                    "message": f"Invalid time format. Please try again with a valid time for {saved_date.strftime('%B %d, %Y')}.",
                    "status": "waiting_for_time"
                }
        else:
            return {
                "message": f"Please provide a time for your appointment on {user_session['pending_date'].strftime('%B %d, %Y')}. For example: '2:30 PM' or '14:30'",
                "status": "waiting_for_time"
            }
    
    elif 'pending_time' in user_session:
        if appointment_details["has_date"]:
            new_date = appointment_details["date_only"]
            if is_date_in_past(new_date):
                return {
                    "message": f"The date {new_date.strftime('%B %d, %Y')} is in the past. Please choose a future date.",
                    "status": "waiting_for_date"
                }
            
            if is_date_on_saturday(new_date):
                return {
                    "message": f"Sorry, the clinic is closed on Saturday ({new_date.strftime('%B %d, %Y')}). Please choose a different date. The clinic is open Sunday–Thursday 08:00–19:00 and Friday 08:00–12:00.",
                    "status": "waiting_for_date"
                }
            
            saved_time = user_session['pending_time']
            hour, minute = saved_time
            
            try:
                appointment_datetime = datetime.combine(
                    new_date, 
                    datetime.min.time().replace(hour=hour, minute=minute)
                )
                
                jerusalem = pytz.timezone('Asia/Jerusalem')
                appointment_datetime = jerusalem.localize(appointment_datetime)
                
                if is_datetime_in_past(appointment_datetime):
                    return {
                        "message": f"The requested time {appointment_datetime.strftime('%Y-%m-%d %H:%M')} is in the past. Please choose a future date and time.",
                        "status": "error"
                    }
                
                result = process_complete_appointment(appointment_datetime, user_name, user_email)
                
                # If appointment failed due to time issues, keep the time in session
                if result["status"] == "error" and ("not available" in result["message"] or "outside of clinic hours" in result["message"]):
                    hour, minute = saved_time
                    time_str = f"{hour:02d}:{minute:02d}"
                    return {
                        "message": f"{result['message']} Please choose a different date for your appointment at {time_str}.",
                        "status": "waiting_for_date"
                    }
                
                clear_user_session(user_id)
                return result
                
            except ValueError:
                return {
                    "message": "Invalid date format. Please try again with a valid date.",
                    "status": "waiting_for_date"
                }
        else:
            hour, minute = user_session['pending_time']
            time_str = f"{hour:02d}:{minute:02d}"
            return {
                "message": f"Please provide a date for your appointment at {time_str}. For example: 'June 8' or 'next Monday'",
                "status": "waiting_for_date"
            }
    
    if appointment_details["valid"]:
        appointment_datetime = appointment_details["datetime"]
        
        if is_datetime_in_past(appointment_datetime):
            return {
                "message": f"The requested time {appointment_datetime.strftime('%Y-%m-%d %H:%M')} is in the past. Please choose a future date and time.",
                "status": "error"
            }
        
        return process_complete_appointment(appointment_datetime, user_name, user_email)
        
    elif appointment_details["has_date"] and not appointment_details["has_time"]:
        selected_date = appointment_details["date_only"]
        
        if is_date_in_past(selected_date):
            return {
                "message": f"The date {selected_date.strftime('%B %d, %Y')} is in the past. Please choose a future date.",
                "status": "error"
            }
        
        if is_date_on_saturday(selected_date):
            return {
                "message": f"Sorry, the clinic is closed on Saturday ({selected_date.strftime('%B %d, %Y')}). Please choose a different date. The clinic is open Sunday–Thursday 08:00–19:00 and Friday 08:00–12:00.",
                "status": "error"
            }
        
        set_user_session(user_id, {'pending_date': selected_date})
        
        return {
            "message": f"Great! I have your date as {selected_date.strftime('%B %d, %Y')}. What time would you like your appointment? Please provide a time like '2:30 PM' or '14:30'.",
            "status": "waiting_for_time"
        }
        
    elif appointment_details["has_time"] and not appointment_details["has_date"]:
        hour, minute = appointment_details["time_only"]
        time_str = f"{hour:02d}:{minute:02d}"
        set_user_session(user_id, {'pending_time': appointment_details["time_only"]})
        
        return {
            "message": f"I have your time as {time_str}. What date would you like your appointment? Please provide a date like 'June 8' or 'next Monday' (note: the clinic is closed on Saturdays).",
            "status": "waiting_for_date"
        }
    
    else:
        return {
            "message": "I couldn't understand the appointment details. Please provide a date and time, for example: 'June 8 at 2:30 PM' or just start with a date like 'next Monday'.",
            "status": "error"
        }

def process_complete_appointment(appointment_datetime, user_name, user_email):
    """Process a complete appointment request with both date and time"""
    
    if is_datetime_in_past(appointment_datetime):
        return {
            "message": f"The requested time {appointment_datetime.strftime('%Y-%m-%d %H:%M')} is in the past. Please choose a future date and time.",
            "status": "error"
        }
    
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
    
    is_available = is_time_available(appointment_datetime)
    
    if not is_available:
        return {
            "message": f"The appointment on {appointment_datetime.strftime('%Y-%m-%d')} at {appointment_datetime.strftime('%H:%M')} is not available. Please choose another time.",
            "status": "error"
        }
    
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
    Check if the given datetime is within clinic hours.
    """
    if not dt:
        return False

    jerusalem = pytz.timezone('Asia/Jerusalem')
    local_dt = dt.astimezone(jerusalem)

    weekday = local_dt.weekday() 
    hour = local_dt.hour
    minute = local_dt.minute

    if weekday in [6, 0, 1, 2, 3]:  
        return 8 <= hour < 19 or (hour == 19 and minute == 0)
    elif weekday == 4: 
        return 8 <= hour < 12 or (hour == 12 and minute == 0)
    else:
        return False 

def is_valid_appointment_time(appointment_datetime):
    """
    Check if the appointment time is valid.
    """
    minute = appointment_datetime.minute
    if minute not in [0, 30]:
        return False, "Appointments must start at the hour (XX:00) or half hour (XX:30). Please choose a valid time."
    return True, ""

def is_day_in_current_hebrew_week(target_weekday):
    """
    Check if the target day was already in the current Hebrew week. 
    """
    today = datetime.now()
    today_weekday = today.weekday()  
    today_hebrew_weekday = (today_weekday + 1) % 7
    target_hebrew_weekday = (target_weekday + 1) % 7    
    return target_hebrew_weekday <= today_hebrew_weekday
