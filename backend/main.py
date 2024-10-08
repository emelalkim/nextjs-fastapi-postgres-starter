from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, func
from seed import seed_user_if_needed
from sqlalchemy.ext.asyncio import AsyncSession
from db_engine import engine
from models import User, Message, Thread
from datetime import datetime
from sqlalchemy.orm import selectinload
from typing import Optional
import random
import base64
from fastapi.middleware.cors import CORSMiddleware

seed_user_if_needed()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # This allows the Authorization header to be sent
)

class UserRead(BaseModel):
    id: int
    name: str

class ThreadRead(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageRead(BaseModel):
    id: int
    message: str
    timestamp: datetime
    response_to_id: Optional[int] = None  # Can be None if the message is not a reply
    user_id: int  # User ID of the person who sent the message

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    message: str
    thread_id: Optional[int] = None  # Optional thread_id for the message

class AuthRequest(BaseModel):
    name: str

# Helper function to extract user_id from Authorization header
def get_user_from_auth(request: Request):
    # Retrieve the Authorization header directly from the request
    auth_header = request.headers.get("authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # Assuming Basic Authentication: 'Authorization: Basic base64encodedcredentials'
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        user_id = decoded_credentials.split(":")[0]  # Extract the user ID from 'user_id:'
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Auth route to authenticate or create a new user
@app.post("/auth")
async def authenticate_user(auth: AuthRequest):
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Try to find user by name (case-insensitive)
            result = await session.execute(select(User).filter(func.lower(User.name) == func.lower(auth.name)))
            user = result.scalars().first()
            if not user:
                # If user not found, create a new user
                user = User(name=auth.name)
                session.add(user)
                await session.flush()  # Flush to get the user ID
                user_data = {
                    "id": user.id,
                    "name": user.name,
                }
                await session.commit()
            else:
                user_data = {
                    "id": user.id,
                    "name": user.name,
                }

            return user_data

# Get current authenticated user
@app.get("/users/me")
async def get_my_user(request: Request):
    user_id = get_user_from_auth(request)  # Get user ID from the Authorization header
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalars().first()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)

# API call to get threads of the current user
@app.get("/threads")
async def get_my_threads(request: Request):
    user_id = get_user_from_auth(request)  # Get user ID from the Authorization header
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Fetching threads that belong to the user
            thread_result = await session.execute(select(Thread).filter_by(user_id=user_id))
            threads = thread_result.scalars().all()

            if not threads:
                return [ThreadRead(id=thread.id, title=thread.title, created_at=thread.created_at) for thread in threads]

            return [ThreadRead(id=thread.id, title=thread.title, created_at=thread.created_at) for thread in threads]

@app.get("/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: int, request: Request):
    user_id = get_user_from_auth(request)  # Get user ID from the Authorization header
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Fetch the thread to ensure it exists and belongs to the user
            thread_result = await session.execute(select(Thread).filter_by(id=thread_id, user_id=user_id))
            thread = thread_result.scalars().first()

            if thread is None:
                raise HTTPException(status_code=404, detail="Thread not found")

            # Fetch all messages associated with the thread
            message_result = await session.execute(select(Message).filter_by(thread_id=thread_id))
            messages = message_result.scalars().all()

            if not messages:
                raise HTTPException(status_code=404, detail="No messages found in this thread")

            return [
                MessageRead(
                    id=message.id,
                    message=message.message,
                    timestamp=message.timestamp,
                    response_to_id=message.response_to_id,
                    user_id=message.user_id
                )
                for message in messages
            ]

# Sample list of random responses the chatbot can send
chatbot_responses = [
    "That's interesting! You said: {message}",
    "I see what you mean by: {message}",
    "Let me think about: {message}",
    "I appreciate your thoughts on: {message}"
]

@app.post("/send_message")
async def send_message(request: SendMessageRequest, req: Request):
    user_id = get_user_from_auth(req)  # Get user ID from the Authorization header
    async with AsyncSession(engine) as session:
        async with session.begin():
            # If thread_id is provided, fetch the thread; otherwise, create a new thread
            if request.thread_id:
                thread_result = await session.execute(select(Thread).filter_by(id=request.thread_id, user_id=user_id))
                thread = thread_result.scalars().first()

                if thread is None:
                    raise HTTPException(status_code=404, detail="Thread not found")
            else:
                # Create a new thread with the message as the title
                thread = Thread(
                    title=request.message[:50],  # Use the first 50 characters of the message as the title
                    user_id=user_id,
                    created_at=datetime.utcnow()
                )
                session.add(thread)
                await session.flush()  # This flushes to get the thread ID for the message

            # Add the user message
            user_message = Message(
                message=request.message,
                user_id=user_id,
                thread_id=thread.id,
                timestamp=datetime.utcnow(),
            )
            session.add(user_message)
            await session.flush()  # Flush to get the message ID for response_to reference

            # Generate a random chatbot response
            response_text = random.choice(chatbot_responses).format(message=request.message)

            # Add the chatbot's response message
            chatbot_message = Message(
                message=response_text,
                user_id=user_id, 
                thread_id=thread.id,
                timestamp=datetime.utcnow(),
                response_to_id=user_message.id
            )
            session.add(chatbot_message)

            thread_data = {
                "id": thread.id,
                "title": thread.title,
                "created_at": thread.created_at
            }
            user_message_data = {
                "id": user_message.id,
                "message": user_message.message,
                "timestamp": user_message.timestamp
            }
            chatbot_message_data = {
                "id": chatbot_message.id,
                "message": chatbot_message.message,
                "response_to_id": chatbot_message.response_to_id,
                "timestamp": chatbot_message.timestamp
            }

        # Commit the new thread and both messages to the database
        await session.commit()

    # Return the response
    return {
        "thread": thread_data,
        "user_message": user_message_data,
        "chatbot_response": chatbot_message_data
    }
