from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv
from pages.datetime_utils import extract_datetime

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=api_key)

def fix_malformed_response(client, original_response, api_model="gpt-4-turbo"):
    correction_prompt = f"""
The following response does not follow the required format. Please rewrite it using one of the following exact formats only:

1. DATETIME: YYYY-MM-DD HH:MM | Message
2. DATE_ONLY: YYYY-MM-DD | Message
3. TIME_ONLY: HH:MM | Message
4. GREETING | Message

Here is the response you gave:
{original_response}

Respond only in one of the formats above. Do not explain, just fix it.
"""

    try:
        correction = client.chat.completions.create(
            model=api_model,
            messages=[
                {"role": "system", "content": "You are a strict format enforcer."},
                {"role": "user", "content": correction_prompt}
            ],
            temperature=0,
            max_tokens=200
        )

        return correction.choices[0].message.content.strip()

    except Exception as e:
        print("Correction failed:", e)
        return None

def get_response_from_openai(text, conversation_history=None):
    try:
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        today_day = today.strftime("%A")
        
        print(f"Current date: {today_str}, Day: {today_day}")
        
        messages = [
            {"role": "system", "content": f"""
You are a friendly medical clinic appointment assistant for a clinic in Israel.
❗ Always start your response with the tag DATETIME: or DATE_ONLY:, TIME_ONLY:, or GREETING. Never skip the tag, even if the message is very short.

The clinic working hours are:

- Sunday: OPEN from 08:00 to 19:00
- Monday: OPEN from 08:00 to 19:00
- Tuesday: OPEN from 08:00 to 19:00
- Wednesday: OPEN from 08:00 to 19:00
- Thursday: OPEN from 08:00 to 19:00
- Friday: OPEN from 08:00 to 12:00
- Saturday: CLOSED
The clinic is closed on Saturdays.
Assume the clinic is in Israel. In Israel, Sunday is the first working day of the week, and Saturday is the only weekend day.

Today's date is: {today_str} ({today_day})
Current time is: {today.strftime('%H:%M')}

Your primary goal is to help users schedule appointments. Maintain a natural conversation flow.

IMPORTANT: Only extract a date and time if the user explicitly mentions them. If the user asks for an appointment but doesn't specify a date or time, ask them when they would like to schedule.

Format your response as:
DATETIME: YYYY-MM-DD HH:MM | Your friendly response to the user

If the user doesn't specify a time but does specify a date:
DATE_ONLY: YYYY-MM-DD | What time?

If the user doesn't specify a date but does specify a time:
TIME_ONLY: HH:MM | What date?

If you can't extract a date/time or the user is just greeting:
GREETING | Your friendly response to the user

❗ Always start your response with the tag DATETIME: or DATE_ONLY:, TIME_ONLY:, or GREETING. Never skip the tag, even if the message is very short.
❗ Always start your response with the tag DATETIME: or DATE_ONLY:, TIME_ONLY:, or GREETING. Never skip the tag, even if the message is very short.
❗ Always start your response with the tag DATETIME: or DATE_ONLY:, TIME_ONLY:, or GREETING. Never skip the tag, even if the message is very short.

"""}
        ]

        if conversation_history:
            messages.extend(conversation_history[-10:])
        else:
            messages.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        ai_response = response.choices[0].message.content.strip()
        print(f"OpenAI response: {ai_response}")

        if not any(tag in ai_response for tag in ["DATETIME:", "DATE_ONLY:", "TIME_ONLY:", "GREETING"]):
            corrected = fix_malformed_response(client, ai_response)
            if corrected:
                print(f"Corrected response: {corrected}")
                ai_response = corrected

        if "DATETIME:" in ai_response:
            parts = ai_response.split("|", 1)
            if len(parts) == 2:
                datetime_part = parts[0].replace("DATETIME:", "").strip()
                message_part = parts[1].strip()
                try:
                    dt_obj = datetime.strptime(datetime_part, "%Y-%m-%d %H:%M")
                    return {
                        "type": "datetime",
                        "datetime": dt_obj,
                        "message": message_part
                    }
                except ValueError:
                    return {"type": "error", "message": "I couldn't understand the date format. Please try again."}

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
                    return {"type": "error", "message": "I couldn't understand the date format. Please try again."}

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
                    return {"type": "error", "message": "I couldn't understand the time format. Please try again."}

        elif "GREETING" in ai_response:
            if "|" in ai_response:
                message_part = ai_response.split("|", 1)[1].strip()
            else:
                message_part = ai_response.replace("GREETING", "").replace(":", "").strip()
            return {"type": "greeting", "message": message_part}

        dt = extract_datetime(ai_response)
        if dt:
            return {
                "type": "datetime",
                "datetime": dt,
                "message": ai_response
            }

        return {"type": "unknown", "message": ai_response}

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"type": "error", "message": "Sorry, I encountered an error. Please try again."}
