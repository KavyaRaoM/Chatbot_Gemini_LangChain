from pymongo import MongoClient
from datetime import datetime
from app.core.config import MONGO_URI

# client = MongoClient("mongodb+srv://New_User1:GbNb4SBWENtBe9eI@cluster0.p5yznsz.mongodb.net/chatbot")
client = MongoClient(MONGO_URI) 
db = client["chatbot"]

students_col = db["students"]
messages_col = db["messages"]


def create_student(uuid, name):
    if not students_col.find_one({"uuid": uuid}):
        students_col.insert_one({
            "uuid": uuid,
            "name": name,
            "created_at": datetime.utcnow()
        })


def save_message(student_uuid, sender, message):
    messages_col.insert_one({
        "student_uuid": student_uuid,
        "sender": sender,
        "message": message,
        "timestamp": datetime.utcnow()
    })


def get_last_messages(student_uuid, limit=10):
    msgs = list(messages_col.find({"student_uuid": student_uuid})
                .sort("timestamp", -1)
                .limit(limit))
    return list(reversed(msgs))


