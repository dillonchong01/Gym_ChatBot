from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from model.chatbot import ChatBot
from model.sql_database import Database, SQLGenerator

app = FastAPI()

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Initialize Chatbot
database = Database("databases/gym_capacity_summary.db")
sql_generator = SQLGenerator()
chatbot = ChatBot(intent_model=None, database=database, sql_generator=sql_generator)

@app.get("/", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=JSONResponse)
def chat_response(message: str = Form(...)):
    bot_reply = chatbot.get_response(message)
    return {"reply": bot_reply}

app.mount("/static", StaticFiles(directory="static"), name="static")