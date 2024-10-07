"use client"

import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaPen } from "react-icons/fa";  // Import Font Awesome Pen Icon

// Define a type for Thread
interface Thread {
  id: number;
  title: string;
  created_at: string;
}

// Define a type for Message with optional response_to_id
interface Message {
  id: number;
  message: string;
  timestamp: string;
  response_to_id?: number;  // Optional field
}

export default function Chat() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);  // Reference for the input field
  const messagesEndRef = useRef<HTMLDivElement>(null);  // Reference for scrolling

  // Fetch threads on page load
  const fetchThreads = async () => {
    try {
      const response = await axios.get("/api/threads");
      setThreads(response.data);
    } catch (error) {
      console.error("Error fetching threads:", error);
    }
  };

  useEffect(() => {
    fetchThreads();  // Fetch threads when component mounts
  }, []);

  // Fetch messages when a thread is selected
  const fetchMessages = async (threadId: number) => {
    try {
      const response = await axios.get(`/api/threads/${threadId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };


  // Handle message send
  const handleSendMessage = async () => {
    if (newMessage.trim() === "") return;
    try {
      const response = await axios.post(`/api/send_message`, {
        message: newMessage,
        thread_id: selectedThread ? selectedThread.id : null,  // Send null when creating a new thread
      });

      // Clear input
      setNewMessage("");

      // If creating a new thread (i.e., thread_id is null), refetch threads
      if (!selectedThread) {
        await fetchThreads();  // Refetch threads

        // Automatically select and highlight the new thread
        const newThread = response.data.thread;  // Assuming backend returns the new thread in response
        setSelectedThread(newThread);
        fetchMessages(newThread.id);  // Fetch messages for the newly created thread
      } else {
        // If it's an existing thread, just update the messages
        setMessages([...messages, response.data.user_message, response.data.chatbot_response]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  // Handle key press in input (Enter key sends the message)
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();  // Prevent form submission or new line
      handleSendMessage();
    }
  };

  // Handle new thread creation (blank message list)
  const createNewThread = () => {
    setSelectedThread(null);  // Set thread to null to indicate a new thread
    setMessages([]);  // Clear the message list
    inputRef.current?.focus();  // Focus on the input field
  };

  return (
    <div className="container">
      <div className="chat-container">
        {/* Thread List */}
        <div className="thread-list">
          <div className="header">
            <h2>Threads</h2>
            <FaPen 
              style={{ cursor: "pointer", fontSize: "20px", color: "#336699" }} 
              onClick={createNewThread} 
              title="Start a new thread" 
            />
          </div>
          <ul>
            {threads.map((thread) => (
              <li
                key={thread.id}
                onClick={() => {
                  setSelectedThread(thread);
                  fetchMessages(thread.id);
                }}
                style={{
                  cursor: "pointer",
                  backgroundColor: selectedThread?.id === thread.id ? "#336699" : "white",  // Brighter blue for selected thread
                  color: selectedThread?.id === thread.id ? "white" : "black",  // Text color based on selection
                  padding: "15px",
                  border: "1px solid #ddd",
                  borderRadius: "5px",
                  marginBottom: "10px",
                  fontWeight: selectedThread?.id === thread.id ? "bold" : "normal",  // Bold for selected thread
                }}
              >
                {thread.title}
              </li>
            ))}
          </ul>
        </div>

        {/* Chat Window */}
        <div className="chat-window">
          <div className="messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.response_to_id ? "chatbot" : "user"}`}
                style={{
                  textAlign: message.response_to_id ? "left" : "right",  // Chatbot on left, user on right
                  backgroundColor: message.response_to_id ? "#f0f0f0" : "#336699",  // Chatbot light, user brighter blue
                  color: message.response_to_id ? "black" : "white",  // Ensure text visibility
                  padding: "15px",
                  borderRadius: "10px",
                  margin: "10px 0",
                  maxWidth: "60%",
                  alignSelf: message.response_to_id ? "flex-start" : "flex-end",  // Align based on message type
                }}
              >
                {message.message}
              </div>
            ))}
            <div ref={messagesEndRef} />  {/* Reference to scroll to the bottom */}
          </div>
          <div className="message-input">
            <input
              ref={inputRef}  // Reference for the input field
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={handleKeyDown}  // Attach keydown handler to input
              placeholder="Type your message..."
              style={{
                flex: 1,
                padding: "15px",
                border: "1px solid #ddd",
                borderRadius: "5px",
                backgroundColor: "white",
                color: "black",
                fontSize: "16px",
              }}
            />
            <button
              onClick={handleSendMessage}
              style={{
                padding: "15px 20px",
                marginLeft: "10px",
                border: "none",
                backgroundColor: "#336699",  // Use the same blue for buttons
                color: "white",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .container {
          width: 90%;
          margin: 0 auto;
          padding: 20px;
        }
        .chat-container {
          display: flex;
          justify-content: space-between;
        }
        .thread-list {
          width: 25%;
          padding-right: 10px;
        }
        .thread-list ul {
          list-style-type: none;
          padding: 0;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .chat-window {
          width: 70%;
          border: 1px solid #ddd;
          padding: 10px;
          border-radius: 5px;
          display: flex;
          flex-direction: column;
        }
        .messages {
          height: 400px;
          overflow-y: scroll;
          border-bottom: 1px solid #ddd;
          padding-bottom: 10px;
          display: flex;
          flex-direction: column;
        }
        .message-input {
          display: flex;
          margin-top: 10px;
        }

        @media (max-width: 768px) {
          .chat-container {
            flex-direction: column;
          }
          .thread-list {
            width: 100%;
            margin-bottom: 20px;
          }
          .chat-window {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}
