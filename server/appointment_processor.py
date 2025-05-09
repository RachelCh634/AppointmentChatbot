import parsedatetime
import datetime
import re
from calendar_utils import is_time_available, create_appointment_event

def extract_datetime(text):
    time_pattern = r'at\s+(\d{1,2})(?:[:.]?(\d{2}))?(?:\s*(am|pm))?'
    time_match = re.search(time_pattern, text, re.IGNORECASE)
    
    cal = parsedatetime.Calendar()
    result = cal.parse(text)
    
    if result[1]:
        dt_struct = list(result[0])
        
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3).lower() if time_match.group(3) else None
            
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
                
            if not am_pm and hour < 12 and hour >= 8:
                pass
            elif not am_pm and hour < 8:
                hour += 12
                
            dt_struct[3] = hour  
            dt_struct[4] = minute  
            
        return tuple(dt_struct)
    else:
        return None

def is_within_operating_hours(dt):
    appointment_datetime = datetime.datetime(*dt[:6])
    
    day_of_week = (appointment_datetime.weekday() + 1) % 7
    hour = appointment_datetime.hour
    
    if day_of_week == 6:
        return False
    
    if day_of_week == 5:
        return 8 <= hour < 12
    
    return 8 <= hour < 19

def get_operating_hours_message():
    return ("Clinic operating hours:\n"
            "Sunday to Thursday: 8:00 AM - 7:00 PM\n"
            "Friday: 8:00 AM - 12:00 PM\n"
            "Saturday: Closed")

def handle_appointment_request(text):
    dt = extract_datetime(text)
    if dt:
        if is_within_operating_hours(dt):
            dt_obj = datetime.datetime(*dt[:6])
            formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')

            if is_time_available(dt_obj):
                create_appointment_event(dt_obj)
                return {"status": "success", "message": f"Appointment booked at {formatted_date}"}
            else:
                return {
                    "status": "error",
                    "message": f"The requested time ({formatted_date}) is already taken. Please choose another time."
                }

        else:
            formatted_date = datetime.datetime(*dt[:6]).strftime('%Y-%m-%d %H:%M')
            return {
                "status": "error",
                "message": f"The requested time ({formatted_date}) is outside clinic operating hours.\n\n{get_operating_hours_message()}"
            }
    else:
        return {"status": "error", "message": "Couldn't understand the date from the message"}

