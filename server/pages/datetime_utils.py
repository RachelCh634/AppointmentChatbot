import datetime
import re
import parsedatetime

def extract_datetime(text):
    cal = parsedatetime.Calendar()
    result = cal.parse(text)
    
    if result[1]: 
        time_pattern = r'at\s+(\d{1,2})(?:[:.]?(\d{2}))?(?:\s*(am|pm))?'
        time_match = re.search(time_pattern, text, re.IGNORECASE)
        
        dt_struct = list(result[0])
        
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3).lower() if time_match.group(3) else None
            
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
            
            if not am_pm:
                if hour < 8 and hour > 0:
                    hour += 12
            
            dt_struct[3] = hour
            dt_struct[4] = minute
        
        dt = datetime.datetime(*dt_struct[:6])
        
        now = datetime.datetime.now()
        
        if dt.date() == now.date() and dt.time() < now.time():
            print(f"Time {dt.time()} has already passed today. Adjusting...")
            next_hour = now.hour + 1
            if next_hour < 19:
                dt = dt.replace(hour=next_hour, minute=0)
                print(f"Adjusted to today at {dt.time()}")
            else:
                dt = dt + datetime.timedelta(days=1)
                dt = dt.replace(hour=9, minute=0) 
                print(f"Adjusted to tomorrow at {dt.time()}")
        
        elif dt < now:
            print(f"Date {dt.date()} has already passed. Adjusting...")
            if (now.date() - dt.date()).days < 7:
                dt += datetime.timedelta(days=7)
                print(f"Adjusted to next week: {dt.date()}")
            else:
                future_text = f"next {text}"
                future_result = cal.parse(future_text)
                if future_result[1]:
                    future_dt = datetime.datetime(*future_result[0][:6])
                    if future_dt > now:
                        dt = future_dt
                        print(f"Re-interpreted as future date: {dt.date()}")
        
        clinic_hours = get_clinic_hours(dt)
        if not clinic_hours['is_open']:
            print(f"Selected time is outside clinic hours: {clinic_hours['message']}")
            if dt.weekday() == 5:  
                days_to_add = 1
                dt = dt + datetime.timedelta(days=days_to_add)
                dt = dt.replace(hour=9, minute=0)
                print(f"Adjusted to Sunday at 9:00 AM: {dt}")
        elif dt.hour < 8 or (dt.hour >= 19 and dt.weekday() != 4) or (dt.hour >= 12 and dt.weekday() == 4):
            if dt.hour < 8:
                dt = dt.replace(hour=9, minute=0)
                print(f"Adjusted to opening hours: {dt}")
            else:
                dt = dt + datetime.timedelta(days=1)
                dt = dt.replace(hour=9, minute=0)
                print(f"Adjusted to next day opening hours: {dt}")
                
                if dt.weekday() == 5:  # שבת
                    dt = dt + datetime.timedelta(days=1)
                    print(f"Adjusted again because of Saturday: {dt}")
        
        return dt
    else:
        common_expressions = {
            "tomorrow": datetime.datetime.now() + datetime.timedelta(days=1),
            "today": datetime.datetime.now(),
            "next week": datetime.datetime.now() + datetime.timedelta(days=7),
            "next month": datetime.datetime.now() + datetime.timedelta(days=30),
        }
        
        for expr, date_value in common_expressions.items():
            if expr in text.lower():
                dt = date_value.replace(hour=9, minute=0) 
                
                time_pattern = r'at\s+(\d{1,2})(?:[:.]?(\d{2}))?(?:\s*(am|pm))?'
                time_match = re.search(time_pattern, text, re.IGNORECASE)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    am_pm = time_match.group(3).lower() if time_match.group(3) else None
                    
                    if am_pm == 'pm' and hour < 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    if not am_pm and hour < 8 and hour > 0:
                        hour += 12
                    
                    dt = dt.replace(hour=hour, minute=minute)
                
                return dt
        return None

    
def get_clinic_hours(dt):
    if isinstance(dt, datetime.datetime):
        day_of_week = dt.weekday() 
        day_name = dt.strftime('%A')
    else:
        dt_obj = datetime.datetime(*dt[:6])
        day_of_week = dt_obj.weekday()
        day_name = dt_obj.strftime('%A')
    
    if day_name == 'Saturday':
        return {
            'is_open': False,
            'day': day_name,
            'hours': 'Closed',
            'message': 'The clinic is closed on Saturdays.'
        }
    elif day_name == 'Friday':
        return {
            'is_open': True,
            'day': day_name,
            'hours': '8:00 AM - 12:00 PM',
            'message': 'The clinic is open on Fridays from 8:00 AM to 12:00 PM.'
        }
    else:
        return {
            'is_open': True,
            'day': day_name,
            'hours': '8:00 AM - 7:00 PM',
            'message': f'The clinic is open on {day_name} from 8:00 AM to 7:00 PM.'
        }



