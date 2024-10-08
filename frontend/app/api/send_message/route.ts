
import axios from "axios";

export async function POST(request: Request) {
  const body = await request.json();
  // Extract the Authorization header from the incoming request
  const authHeader = request.headers.get("authorization");
  try {
    const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/send_message`, body, {
      headers: {
        'Authorization': authHeader  // Pass the Authorization header
      }
    });
    return new Response(JSON.stringify(response.data), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to send message" }), { status: 500 });
  }
}
