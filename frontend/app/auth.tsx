"use client";

import { useState } from "react";
import axios from "axios";

interface Props {
  onAuthenticated: (user: { id: string; name: string }) => void;
}

export default function Authentication({ onAuthenticated }: Props) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleAuth = async () => {
    if (name.trim() === "") {
      setError("Please enter a valid name.");
      return;
    }

    try {
      const response = await axios.post("/api/auth", { name });
      if (response.status === 200) {
        const data = response.data;
        onAuthenticated(data); // Pass the authenticated user data to the parent component
        localStorage.setItem("user_id", data.id); // Store user_id for future requests
        localStorage.setItem("user_name", data.name);
        setError("");  // Clear any previous error
      }
    } catch (err) {
      setError("Authentication failed. Please try again.");
    }
  };

  // Handle "Enter" key press in the input field
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleAuth();  // Trigger authentication when Enter is pressed
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={handleKeyDown}  // Attach Enter key press handler
        placeholder="Enter your name"
        className="auth-input"
      />
      <button onClick={handleAuth} className="auth-button">Submit</button>

      {error && <p className="error-message">{error}</p>}

      <style jsx>{`
        .auth-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          background-color: #1c1c1c;  // Dark background
          color: white;  // White text color
        }

        .auth-input {
          margin-top: 20px;
          padding: 15px;
          font-size: 16px;
          width: 100%;
          max-width: 300px;
          background-color: #333;  // Dark input background
          border: 1px solid #555;  // Darker border
          color: white;  // White text color inside input
          border-radius: 5px;
        }

        .auth-button {
          margin-top: 20px;
          padding: 10px 20px;
          background-color: #336699;  // Matching blue color
          color: white;
          border: none;
          cursor: pointer;
          font-size: 16px;
          border-radius: 5px;
        }

        .auth-button:hover {
          background-color: #28527a;  // Slightly darker on hover
        }

        .error-message {
          color: #ff4d4f;
          margin-top: 10px;
        }

        h2 {
          font-family: 'Arial', sans-serif;
          font-size: 24px;
          margin-bottom: 20px;
          color: white;  // White color for the heading
        }
      `}</style>
    </div>
  );
}
