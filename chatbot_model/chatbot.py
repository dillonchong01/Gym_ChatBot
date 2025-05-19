import onnxruntime as ort
from tokenizers import Tokenizer
from config import TOKENIZER_PATH, MODEL_PATH
from chatbot_model.helper_functions import get_gym, get_time, get_weekend

class ChatBot:
    def __init__(self, database, sql_generator):
        # Load Pretrained Model
        self.tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
        self.session = ort.InferenceSession(MODEL_PATH)
        
        # Gym Names for Extraction
        self.database = database
        self.sql_generator = sql_generator

        # Context History
        self.context = {}

    def get_intent(self, user_input):
        """ Takes in user_input and outputs likely intent action """
        # Encode Input using Tokenizer
        encoding = self.tokenizer.encode(user_input)
        input_ids = [encoding.ids]
        attention_mask = [[1] * len(encoding.ids)]

        # Prepare ONNX-compatible Inputs
        input_names = [inp.name for inp in self.session.get_inputs()]
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = [[0] * len(encoding.ids)]

        # Predict Intent
        logits = self.session.run(["logits"], inputs)[0]
        return int(max(enumerate(logits[0]), key=lambda x: x[1])[0])
    
    
    def get_response(self, user_input):
        """
        Parses user input to update/reset context. SQL query is then generated to
        access the database and return human response
        """
        # Clean User Input
        user_input = user_input.lower()

        # Get Details
        new_gym_name = get_gym(user_input)
        new_time = get_time(user_input)
        if new_time == "Invalid Time":          # If Time is invalid (not between 7am-10pm), raise error
            self.context.pop("Time", None)
            return "ActiveSG gyms are only open between 7am to 10pm."
        new_weekend_info = get_weekend(user_input)

        # If New Query (More than 5 words), Clear Context
        if len(user_input.split()) > 5:
            self.context.clear()        
            self.context["Intent"] = self.get_intent(user_input)

        # Add Parameters to Context
        if new_gym_name:
            self.context["Gym"] = new_gym_name
        if new_time:
            self.context["Time"] = new_time
        if new_weekend_info is not None:
            self.context["Weekend"] = new_weekend_info

        intent = self.context["Intent"]
        gym_name = self.context.get("Gym")
        time = self.context.get("Time")
        weekend_info = self.context.get("Weekend")

        # Generate SQL Query and get Results
        query = self.sql_generator.generate_query(intent, gym_name, time, weekend_info)

        # Get Results for Intent 1
        if intent == 0:
            params = [p for p in (gym_name, time, int(weekend_info)
                                  if weekend_info is not None else None) if p is not None]
            avg_capacity = self.database.execute_query(query, params)[0]

            if avg_capacity is not None:
                parts = ["The average capacity"]
                if gym_name:
                    parts.append(f"of {gym_name} ActiveSG Gym")
                else:
                    parts.append("across all ActiveSG Gyms")
                if time:
                    parts.append(f"at {time}")
                if weekend_info is not None:
                    parts.append("on weekends" if weekend_info else "on weekdays")
                return f"{' '.join(parts)} is {avg_capacity:.1f}%"
        
        # Get Results for Intent 2 and Intent 3
        elif intent in [1, 2]:
            params = [p for p in (time, int(weekend_info)
                                  if weekend_info is not None else None) if p is not None]
            gym, avg_capacity = self.database.execute_query(query, params)

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
            best_time, avg_capacity = self.database.execute_query(query, params)

            if best_time and avg_capacity is not None:
                parts = [f"The best time to visit {gym_name} ActiveSG Gym"]
                if weekend_info is not None:
                    parts.append("on weekends" if weekend_info else "on weekdays")
                return f"{' '.join(parts)} is {best_time} with an average capacity of {avg_capacity:.1f}%"

        # If unable to get results
        return "Sorry, I could not find any information on your request"