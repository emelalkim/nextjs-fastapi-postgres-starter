from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

   # Relationships
    messages = relationship("Message", back_populates="user")
    threads = relationship("Thread", back_populates="user")  # User can create many threads

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}"

class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))  # Foreign key linking to the Thread table
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    response_to_id: Mapped[int] = mapped_column(ForeignKey("message.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="messages")
    thread = relationship("Thread", back_populates="messages")  # Message belongs to a thread
    response_to = relationship("Message", remote_side=[id], back_populates="responses")
    responses = relationship("Message", back_populates="response_to", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, message={self.message!r}, user_id={self.user_id!r}, thread_id={self.thread_id!r}, timestamp={self.timestamp!r}, response_to_id={self.response_to_id!r})"

class Thread(Base):
    __tablename__ = "thread"

    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key auto-increment
    title: Mapped[str] = mapped_column(String(100))  # Optional: A title for the thread
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # Timestamp for thread creation
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))  # Foreign key linking the thread to the user who created it

    # Relationship to the messages and user
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")
    user = relationship("User", back_populates="threads")  # Relationship to get the user who created the thread

    def __repr__(self) -> str:
        return f"Thread(id={self.id!r}, title={self.title!r}, created_at={self.created_at!r}, user_id={self.user_id!r})"

