"use client";

import { useState, useEffect } from "react";
import Chat from './chat/page';
import Authentication from './auth';

type User = {
  id: string;
  name: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);  // Track loading state

  // Fetch the user from localStorage if the page is refreshed
  useEffect(() => {
    const storedUserId = localStorage.getItem("user_id");
    const storedUserName = localStorage.getItem("user_name");

    if (storedUserId && storedUserName) {
      setUser({ id: storedUserId, name: storedUserName });  // Set the user from localStorage
      setIsLoading(false);  // We have the user info, so stop loading
    } else {
      // If no user is found in localStorage, check with the backend
      const fetchUser = async () => {
        try {
          const response = await fetch(`${apiUrl}/users/me`, {
            headers: {
              Authorization: `Basic ${btoa(`${storedUserId}:`)}`,  // Pass user ID in header
            },
          });
          if (response.ok) {
            const userData: User = await response.json();
            setUser(userData);
          }
        } catch (error) {
          console.error("User not authenticated");
        } finally {
          setIsLoading(false);  // Set loading to false after fetching is complete
        }
      };

      fetchUser();  // Fetch user from the backend if needed
    }
  }, []);

  const handleAuthenticated = (userData: User) => {
    setUser(userData);
    localStorage.setItem("user_id", userData.id);  // Save user ID in localStorage
    localStorage.setItem("user_name", userData.name);  // Save username in localStorage
  };

  const handleLogout = () => {
    setUser(null);  // Reset user state to null to show Authentication again
    localStorage.removeItem("user_id");  // Remove user ID from localStorage
    localStorage.removeItem("user_name");  // Remove username from localStorage
  };

  if (isLoading) {
    // Render a loading indicator while waiting for user data
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Authentication onAuthenticated={handleAuthenticated} />;
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="header">
        <h1>Hello, {user.name}!</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>
      <Chat  />

      <style jsx>{`
        .header {
          display: flex;
          align-items: center;  // Ensures the text and button are vertically aligned
          gap: 10px;  // Space between the username and the logout button
        }

        .logout-btn {
          padding: 5px 10px;  // Smaller padding for a smaller button
          font-size: 14px;  // Smaller font size
          background-color: #ff4d4f;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          vertical-align: middle;  // Ensure button aligns with text
        }

        .logout-btn:hover {
          background-color: #d9363e;
        }

        h1 {
          font-family: 'Arial', sans-serif;
          margin: 0;  // Remove default margin to align text properly
        }

        main {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </main>
  );
}
