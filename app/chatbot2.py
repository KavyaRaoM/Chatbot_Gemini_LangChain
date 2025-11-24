
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.db import messages_col
from datetime import datetime
import os
from app.db import save_message, get_last_messages
from app.core.config import GEMINI_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def chat_with_student(student_uuid, user_message):
    """
    Chat with student - retrieves last 10 messages for context and answers current question
    Takes student_uuid, user_message and returns AI response as a string
    
    """
    # Save the student's current message
    save_message(student_uuid, "student", user_message)
    
    # Retrieve last 10 messages for context (includes the one we just saved)
    last_messages = get_last_messages(student_uuid, limit=10)
    
    # Build conversation history for LangChain
    conversation = []
    for msg in last_messages:
        if msg["sender"] == "student":
            conversation.append(HumanMessage(content=msg["message"]))
        elif msg["sender"] == "ai":
            conversation.append(AIMessage(content=msg["message"]))
    
    # System prompt - defines AI behavior
    SYSTEM_PROMPT = """You are a helpful AI chatbot. Be friendly and educational. 
Answer questions clearly and help users learn effectively."""
    
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(conversation)
    
    # Get AI response from Gemini
    response = llm.invoke(messages)
    ai_response = response.content
    
    # Save AI response to database
    save_message(student_uuid, "ai", ai_response)
    
    return ai_response