from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=api_key)

def get_response_from_openai(text, conversation_history=None):
    try:
        messages = [
    {"role": "system", "content": """
    You are a friendly medical clinic appointment assistant.

    IMPORTANT: You MUST format your responses exactly as instructed below. This is critical for the system to work properly.

    Format ALL your responses using one of these exact formats:
    1. DATETIME: YYYY-MM-DD HH:MM | Your message
    2. DATE_ONLY: YYYY-MM-DD | Your message
    3. TIME_ONLY: HH:MM | Your message
    4. GREETING | Your message

    Examples of correct formatting:
    DATETIME: 2025-05-16 09:30 | Your appointment is scheduled for Friday at 9:30 AM.
    DATE_ONLY: 2025-05-16 | What time would you like to schedule on Friday?
    TIME_ONLY: 09:30 | What date would you like to schedule at 9:30 AM?
    GREETING | Hello! How can I help you schedule an appointment today?

    Operating hours:
    Sunday to Thursday: 8:00 AM - 7:00 PM
    Friday: 8:00 AM - 12:00 PM
    Saturday: Closed

    Today's date is: """ + datetime.now().strftime("%Y-%m-%d") + """
    """}
        ]

        if conversation_history:
            recent_history = conversation_history[-10:]
            messages.extend(recent_history)
        else:
            messages.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )

        ai_response = response.choices[0].message.content
        print(f"OpenAI response: {ai_response}")

        if "DATETIME:" in ai_response:
            parts = ai_response.split("|", 1)
            if len(parts) == 2:
                datetime_part = parts[0].replace("DATETIME:", "").strip()
                message_part = parts[1].strip()
                
                try:
                    # בדיקה אם יש גם תאריך וגם שעה
                    if " " in datetime_part and ":" in datetime_part:
                        dt_obj = datetime.strptime(datetime_part, "%Y-%m-%d %H:%M")
                        return {
                            "type": "datetime",
                            "datetime": dt_obj,
                            "message": message_part
                        }
                    # אם יש רק תאריך ללא שעה
                    elif "-" in datetime_part and ":" not in datetime_part:
                        date_obj = datetime.strptime(datetime_part, "%Y-%m-%d").date()
                        return {
                            "type": "date_only",
                            "date": date_obj,
                            "message": message_part
                        }
                    else:
                        return {
                            "type": "error",
                            "message": "I couldn't understand the date format. Please provide a complete date and time."
                        }
                except ValueError:
                    return {
                        "type": "error",
                        "message": "I couldn't understand the date format. Please try again."
                    }
            else:
                return {
                    "type": "error",
                    "message": "I couldn't parse the response format. Please try again."
                }
                
        elif "DATE_ONLY:" in ai_response:
            parts = ai_response.split("|", 1)
            if len(parts) == 2:
                date_part = parts[0].replace("DATE_ONLY:", "").strip()
                message_part = parts[1].strip()
                
                try:
                    date_obj = datetime.strptime(date_part, "%Y-%m-%d").date()
                    return {
                        "type": "date_only",
                        "date": date_obj,
                        "message": message_part
                    }
                except ValueError:
                    return {
                        "type": "error",
                        "message": "I couldn't understand the date format. Please try again."
                    }
            else:
                return {
                    "type": "error",
                    "message": "I couldn't parse the response format. Please try again."
                }
                
        elif "TIME_ONLY:" in ai_response:
            parts = ai_response.split("|", 1)
            if len(parts) == 2:
                time_part = parts[0].replace("TIME_ONLY:", "").strip()
                message_part = parts[1].strip()
                
                try:
                    time_obj = datetime.strptime(time_part, "%H:%M").time()
                    return {
                        "type": "time_only",
                        "time": time_obj,
                        "message": message_part
                    }
                except ValueError:
                    return {
                        "type": "error",
                        "message": "I couldn't understand the time format. Please try again."
                    }
            else:
                return {
                    "type": "error",
                    "message": "I couldn't parse the response format. Please try again."
                }
                
        elif "GREETING" in ai_response:
            if "|" in ai_response:
                message_part = ai_response.split("|", 1)[1].strip()
            else:
                if "GREETING:" in ai_response:
                    message_part = ai_response.replace("GREETING:", "").strip()
                else:
                    message_part = ai_response.replace("GREETING", "").strip()
                    
            return {
                "type": "greeting",
                "message": message_part
            }
        else:
            return {
                "type": "unknown",
                "message": ai_response
            }
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {
            "type": "error",
            "message": "Sorry, I encountered an error. Please try again."
        }
