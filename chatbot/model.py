import re
import torch
import sqlite3
from rapidfuzz import process, fuzz
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import GYMS, TIME_REGEX

# REGEX for Parsing Time


class Database:
    def __init__(self, db_name):
        # Connect to the Database
        self.connection = sqlite3.connect(db_name, check_same_thread=False)

    def execute_query(self, query, params=None):
        """ Execute Specified query """
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()


class SQLGenerator:
    def __init__(self):
        pass
    
    def generate_query(self, intent, gym_name, time, weekend_info):
        """
        Generates query based on the intent and details
        For now our only trained intent is to view capacity of a gym
        """
        # Initialize List to store Specific Conditions
        conditions = []

        # If Intent is to Get Gym Details
        if intent == 0:
            query = "SELECT AVG(capacity) FROM gym_capacity_summary"

            # Add Conditions based on User Input
            if gym_name:
                conditions.append(f"gym_name = ?")
            if time:
                conditions.append(f"time = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        elif intent in [1, 2]:
            query = "SELECT gym_name, AVG(capacity) AS avg_capacity FROM gym_capacity_summary"

             # Add Conditions based on User Input
            if time:
                conditions.append(f"time = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions) + " GROUP BY gym_name"

            # Order by Asc/Desc depending on Intent 1 or 2
            if intent == 1:         
                query += " ORDER BY avg_capacity ASC LIMIT 1"
            else:
                query += " ORDER BY avg_capacity DESC LIMIT 1"

        elif intent == 3:
            query = "SELECT time, AVG(capacity) as avg_capacity FROM gym_capacity_summary"

             # Add Conditions based on User Input
            if gym_name:
                conditions.append(f"gym_name = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions) + " GROUP BY time ORDER BY avg_capacity ASC LIMIT 1"

        return query
    

class ChatBot:
    def __init__(self, model, gyms, database, sql_generator):
        # # Load Pretrained Model
        # self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        # self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        
        # Gym Names for Extraction
        self.gyms = {self.clean_text(gym): gym for gym in gyms}
        self.database = database
        self.sql_generator = sql_generator

    def clean_text(self, text):
        """ Takes in name of gym and returns clean text """
        text = text.lower()
        to_remove = ['gym', 'activesg', '@']
        for word in to_remove:
            text = text.replace(word, '')
        return text.strip()

    def get_intent(self, user_input):
        """ Takes in user_input and outputs likely intent action """
        # Tokenize the User Input
        inputs = self.tokenizer(user_input, return_tensors="pt", padding=True, truncation=True)

        # Predict Intent, based on Highest Probability
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        intent = torch.argmax(logits, dim=-1).item()
        return intent
    
    def get_time(self, user_input):
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
            return None
        
        return f"{hour:02d}:{minute:02d}"
    
    def get_weekend(self, user_input):
        """
        Takes in user_input and outputs whether weekend or weekday
        """
        if any(word in user_input for word in ["weekend", "saturday", "sunday"]):
            return True
        if any(word in user_input for word in ["weekday", "monday", "tuesday", "wednesday", "thursday", "friday"]):
            return False
        return None
    
    def get_gym(self, user_input):
        """
        Use Fuzzymatch to obtain most relevant gym
        """
        cleaned_gym_input = self.clean_text(user_input)

        # Sort Gyms by Length and Check if there is Exact Match
        for key in sorted(self.gyms.keys(), key=len, reverse=True):
            if key in cleaned_gym_input:
                return self.gyms[key]
        
        # Else use Fuzzy Matching
        gym_match, score, _ = process.extractOne(cleaned_gym_input, self.gyms.keys(), scorer=fuzz.partial_ratio)
        return self.gyms[gym_match] if score >= 75 else None
    
    
    def get_response(self, user_input):
        """
        Gets response from chatbot based on user input
        """
        # Get Intent
        intent = 3  # PLACEHOLDER HARD CODE FOR NOW as get_intent is not fully working
        # intent = self.get_intent(user_input)      ADD LATER

        # Get Details
        gym_name = self.get_gym(user_input)
        time = self.get_time(user_input)
        weekend_info = self.get_weekend(user_input)

        # Generate SQL Query and get Results
        query = self.sql_generator.generate_query(intent, gym_name, time, weekend_info)
        print(query)

        # Get Results for Intent 1
        if intent == 0:
            params = [p for p in (gym_name, time, int(weekend_info)
                                  if weekend_info is not None else None) if p is not None]
            avg_capacity =  self.database.execute_query(query, params)

            if avg_capacity is not None:
                parts = ["The average capacity"]
                if gym_name:
                    parts.append(f"of {gym_name} ActiveSG Gym")
                if time:
                    parts.append(f"at {time}")
                if weekend_info is not None:
                    parts.append("on weekends" if weekend_info else "on weekdays")
                return f"{' '.join(parts)} is {avg_capacity:.1f}%"
        
        # Get Results for Intent 2 and Intent 3
        elif intent in [1, 2]:
            params = [p for p in (time, int(weekend_info)
                                  if weekend_info is not None else None) if p is not None]
            gym, avg_capacity =  self.database.execute_query(query, params)

            if gym and avg_capacity is not None:
                if intent == 1:
                    parts = ["The least crowded gym"]
                else:
                    parts = ["The most crowded gym"]
                if time:
                    parts.append(f"at {time}")
                if weekend_info is not None:
                    parts.append("on weekends" if weekend_info else "on weekdays")
                return f"{' '.join(parts)} is {gym} ActiveSG Gym with an average capacity of {avg_capacity:.1f}%"
            
        elif intent == 3:
            params = [p for p in (gym_name, int(weekend_info)
                                  if weekend_info is not None else None) if p is not None]
            best_time, avg_capacity =  self.database.execute_query(query, params)

            if best_time and avg_capacity is not None:
                parts = [f"The best time to visit {gym_name} ActiveSG Gym"]
                if weekend_info is not None:
                    parts.append("on weekends" if weekend_info else "on weekdays")
                return f"{' '.join(parts)} is {best_time} with an average capacity of {avg_capacity:.1f}%"

        # If unable to get results
        return "Sorry, I could not find any information on your request"


database = Database("databases/gym_capacity_summary.db")
sql_generator = SQLGenerator()
chatbot = ChatBot(model=None, gyms=GYMS, database=database, sql_generator=sql_generator)

user_input = "what is the best time to visit tampines activesg gym on weekdays"
user_input = user_input.lower()
response = chatbot.get_response(user_input)
print(response)