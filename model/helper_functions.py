from functools import lru_cache
from rapidfuzz import process, fuzz
from config import TIME_REGEX, GYMS

def clean_text(text):
    """ Takes in name of gym and returns clean text """
    text = text.lower()
    for word in ['gym', 'activesg', '@']:
        text = text.replace(word, '')
    return text.strip()

def get_time(user_input):
    """
    Takes in user_input and outputs a likely timing
    """
    # Check for Time Inputs
    time_input = TIME_REGEX.search(user_input)
    if not time_input:
        return None

    # Conversion
    if time_input.group('h24') is not None:
        hour, minute = int(time_input.group('h24')), int(time_input.group('m24'))
    elif time_input.group('h24nc') is not None:
        s = time_input.group('h24nc')
        hour, minute = int(s[:2]), int(s[2:])
    else:
        hour = int(time_input.group('h12'))
        minute = int(time_input.group('m12') or 0)
        period = time_input.group('period').lower()
        if period == 'pm' and hour != 12:
            hour += 12
        if period == 'am' and hour == 12:
            hour = 0

    # Round to Nearest 30minutes
    if minute < 15:
        minute = 0
    elif minute < 45:
        minute = 30
    else:
        minute = 0
        hour += 1
    
    # Only allow values between 7am to 10pm
    if hour < 7 or hour > 22 or (hour == 22 and minute > 0):
        return "Invalid Time"
    
    return f"{hour:02d}:{minute:02d}"

def get_weekend(user_input):
    """
    Takes in user_input and outputs whether weekend or weekday
    """
    if any(word in user_input for word in ["weekend", "saturday", "sunday"]):
        return True
    if any(word in user_input for word in ["weekday", "monday", "tuesday", "wednesday", "thursday", "friday"]):
        return False
    return None

@lru_cache(maxsize=128)
def get_gym(user_input):
    """
    Use Fuzzymatch to obtain most relevant gym
    """
    user_input = clean_text(user_input)
    gym_map = {clean_text(gym): gym for gym in GYMS}
    # Sort Gyms by Length and Check if there is Exact Match
    for key in sorted(gym_map.keys(), key=len, reverse=True):
        if key in user_input:
            return gym_map[key]
    
    # Else use Fuzzy Matching
    match, score, _ = process.extractOne(user_input, gym_map.keys(), scorer=fuzz.partial_ratio)
    return gym_map[match] if score >= 75 else None