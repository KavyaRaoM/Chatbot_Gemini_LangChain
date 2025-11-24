from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from app.chatbot2 import chat_with_student
from app.db import create_student, save_message, get_last_messages



app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Show the chat page initially with no UUID or messages"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat", response_class=HTMLResponse)
def chat(
    request: Request,
    name: str = Form(...),
    student_uuid: str = Form(None),
    message: str = Form(...)
):
    """
    Handle chat messages:
    1. Create student if new user
    2. Get AI response using bot.py (which handles saving messages and context)
    3. Fetch conversation history
    4. Return updated chat page
    """
    # First-time user - generate UUID and create student
    if not student_uuid:
        student_uuid = str(uuid4())
        create_student(student_uuid, name or "Guest")
        print(f"✅ New student created: {name} ({student_uuid})")
    
    # Get AI response from bot.py
    # Note: chat_with_student already saves both user message and AI response
    # It uses last 3 messages for context
    ai_response = chat_with_student(student_uuid, message)
    
    print(f"Student UUID: {student_uuid}")
    print(f"User: {message}")
    print(f"AI: {ai_response[:100]}...")  # Print first 100 chars
    
    # Fetch last 10 messages to show in UI (same as what model uses)
    conversation_history = get_last_messages(student_uuid, limit=10)
    
   
    print(f"🔍 Total messages in DB for this user: {len(conversation_history)}")
    print(f"🔍 Messages: {[msg['message'][:30] for msg in conversation_history]}")
    
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "student_uuid": student_uuid,
            "conversation_history": conversation_history,
            "name": name
        }
    )
