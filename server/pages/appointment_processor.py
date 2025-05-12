import parsedatetime
import datetime
import re
import jwt
from pages.calendar_utils import is_time_available, create_appointment_event
from pages.google_login import secret_key
from pages.openai_utils import get_response_from_openai
from pages.datetime_utils import extract_datetime 

def is_within_operating_hours(dt):
    if isinstance(dt, datetime.datetime):
        appointment_datetime = dt
    else:
        appointment_datetime = datetime.datetime(*dt[:6])
        day_name = appointment_datetime.strftime('%A')
        hour = appointment_datetime.hour

    print(f"Checking operating hours for: {day_name}, {hour}:00")

    day_of_week = appointment_datetime.weekday()
    if day_of_week == 6: 
        day_of_week = 0
    else:
        day_of_week += 1
    
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

def handle_appointment_request(text, token=None, conversation_history=None):    
    try:
        openai_result = get_response_from_openai(text, conversation_history)      
        print("OpenAI result:", openai_result)  
        
        if openai_result["type"] == "datetime":
            dt_obj = openai_result["datetime"]
            if isinstance(dt_obj, tuple):
                dt_obj = datetime.datetime(*dt_obj[:6])
            
            now = datetime.datetime.now()
            if dt_obj < now:
                return {
                    "status": "error",
                    "message": f"I'm sorry, but the requested time ({dt_obj.strftime('%A, %B %d at %I:%M %p')}) has already passed. Please choose a future time."
                }
            
            day_name = dt_obj.strftime('%A')
            if day_name == 'Sunday':
                is_sunday_open = 8 <= dt_obj.hour < 19
                if not is_sunday_open:
                    return {
                        "status": "error",
                        "message": f"I'm sorry, but the requested time on Sunday ({dt_obj.strftime('%I:%M %p')}) is outside our operating hours. Our hours on Sunday are 8:00 AM - 7:00 PM. Would you like to choose a different time?"
                    }
            
            if is_within_operating_hours((dt_obj.year, dt_obj.month, dt_obj.day, dt_obj.hour, dt_obj.minute, 0)):
                formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')
                user_name = "Anonymous"
                if token:
                    try:
                        user_info = jwt.decode(token, secret_key, algorithms=['HS256'])
                        user_email = user_info.get('email')
                        user_name = user_info.get('name', user_email) 
                    except Exception as e:
                        print(f"Error decoding token: {e}")
                
                if is_time_available(dt_obj):
                    print(f"Time is available, creating appointment...")
                    appointment_created = create_appointment_event(dt_obj, user_name=user_name)
                    if appointment_created:
                        print(f"Appointment successfully created")
                    return {
                        "status": "success", 
                        "message": openai_result["message"]
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"I'm sorry, but the time slot ({formatted_date}) is already taken. Would you like to try a different time?"
                    }
            else:
                formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')
                return {
                    "status": "error",
                    "message": f"I'm sorry, but the requested time ({dt_obj.strftime('%A, %B %d at %I:%M %p')}) is outside our operating hours. Our hours are Sunday-Thursday 8:00 AM - 7:00 PM and Friday 8:00 AM - 12:00 PM. Would you like to choose a different time?"
                }
        
        elif openai_result["type"] == "date_only" or openai_result["type"] == "time_only" or openai_result["type"] == "greeting" or openai_result["type"] == "unknown":
            return {
                "status": openai_result["type"],
                "message": openai_result["message"]
            }
        
        else:
            return {
                "status": "unknown",
                "message": openai_result["message"]
            }
            
    except Exception as e:
        print(f"Error in OpenAI processing: {e}")
        
        dt = extract_datetime(text)
        if not dt:
            return {
                "status": "missing_info",
                "message": "I couldn't understand when you want to book an appointment. Please specify a date and time, for example: 'tomorrow at 2pm' or 'next Monday at 10:30'."
            }
        
        if isinstance(dt, tuple):
            dt_obj = datetime.datetime(*dt[:6])
        else:
            dt_obj = dt
        
        now = datetime.datetime.now()
        if dt_obj < now and dt_obj.weekday() == 0:  
            dt_obj += datetime.timedelta(days=7)

        if dt_obj < now:
            return {
                "status": "error",
                "message": f"I'm sorry, but the requested time ({dt_obj.strftime('%A, %B %d at %I:%M %p')}) has already passed. Please choose a future time."
            }
        
        day_name = dt_obj.strftime('%A')
        if day_name == 'Sunday':
            is_sunday_open = 8 <= dt_obj.hour < 19
            if not is_sunday_open:
                return {
                    "status": "error",
                    "message": f"I'm sorry, but the requested time on Sunday ({dt_obj.strftime('%I:%M %p')}) is outside our operating hours. Our hours on Sunday are 8:00 AM - 7:00 PM. Would you like to choose a different time?"
                }
        
        if is_within_operating_hours((dt_obj.year, dt_obj.month, dt_obj.day, dt_obj.hour, dt_obj.minute, 0)):
            formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')
            print(f"Extracted datetime: {dt_obj}")
            print(f"Formatted date: {formatted_date}")
            
            user_name = "Anonymous"
            if token:
                try:
                    user_info = jwt.decode(token, secret_key, algorithms=['HS256'])
                    user_id = user_info.get('id')
                    user_email = user_info.get('email')
                    user_name = user_info.get('name', user_email) 
                except Exception as e:
                    print(f"Error decoding token: {e}")
            
            if is_time_available(dt_obj):
                create_appointment_event(dt_obj, user_name=user_name)
                return {
                    "status": "success", 
                    "message": f"Great! Your appointment is confirmed for {dt_obj.strftime('%A, %B %d at %I:%M %p')}. We look forward to seeing you!"
                }
            else:
                return {
                    "status": "error",
                    "message": f"I'm sorry, but the time slot ({formatted_date}) is already taken. Would you like to try a different time?"
                }
        else:
            formatted_date = dt_obj.strftime('%Y-%m-%d %H:%M')
            return {
                "status": "error",
                "message": f"I'm sorry, but the requested time ({dt_obj.strftime('%A, %B %d at %I:%M %p')}) is outside our operating hours. Our hours are Sunday-Thursday 8:00 AM - 7:00 PM and Friday 8:00 AM - 12:00 PM. Would you like to choose a different time?"
            }
