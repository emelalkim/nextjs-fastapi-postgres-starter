from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from seed import seed_user_if_needed
from sqlalchemy.ext.asyncio import AsyncSession
from db_engine import engine
from models import User, Message, Thread
from datetime import datetime
from sqlalchemy.orm import selectinload
from typing import Optional
import random

seed_user_if_needed()

app = FastAPI()


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

@app.get("/users/me")
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)

# API call to get threads of the current user
@app.get("/users/me/threads")
async def get_my_threads():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Fetching the current user (assuming only one user for simplicity)
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            # Fetching threads that belong to the user
            thread_result = await session.execute(select(Thread).filter_by(user_id=user.id))
            threads = thread_result.scalars().all()

            if not threads:
                raise HTTPException(status_code=404, detail="No threads found for this user")

            # Returning the list of threads using a ThreadRead schema (assuming it exists)
            return [ThreadRead(id=thread.id, title=thread.title, created_at=thread.created_at) for thread in threads]


@app.get("/users/me/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: int):
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Fetch the thread to ensure it exists
            thread_result = await session.execute(select(Thread).filter_by(id=thread_id))
            thread = thread_result.scalars().first()

            if thread is None:
                raise HTTPException(status_code=404, detail="Thread not found")

            # Fetch all messages associated with the thread
            message_result = await session.execute(
                select(Message).filter_by(thread_id=thread_id)
            )
            messages = message_result.scalars().all()

            if not messages:
                raise HTTPException(status_code=404, detail="No messages found in this thread")

            # Returning the list of messages using the MessageRead schema
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
async def send_message(request: SendMessageRequest):
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Fetch the current user (assuming only one user for simplicity)
            user_result = await session.execute(select(User))
            user = user_result.scalars().first()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            # If thread_id is provided, fetch the thread; otherwise, create a new thread
            if request.thread_id:
                # Fetch the thread
                thread_result = await session.execute(select(Thread).filter_by(id=request.thread_id))
                thread = thread_result.scalars().first()

                if thread is None:
                    raise HTTPException(status_code=404, detail="Thread not found")
            else:
                # Create a new thread with the message as the title
                thread = Thread(
                    title=request.message[:50],  # Use the first 50 characters of the message as the title
                    user_id=user.id,
                    created_at=datetime.utcnow()
                )
                session.add(thread)
                await session.flush()  # This flushes to get the thread ID for the message

            # Add the user message
            user_message = Message(
                message=request.message,
                user_id=user.id,
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
                user_id=user.id, 
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
