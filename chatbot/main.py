from model import ChatBot
from sql_database import Database, SQLGenerator
from config import GYMS


database = Database("databases/gym_capacity_summary.db")
sql_generator = SQLGenerator()
chatbot = ChatBot(intent_model=None, gyms=GYMS, database=database, sql_generator=sql_generator)

user_input = "what is the best time to visit tampines activesg gym on weekdays"
user_input = chatbot.clean_text(user_input)
response = chatbot.get_response(user_input)
print(response)