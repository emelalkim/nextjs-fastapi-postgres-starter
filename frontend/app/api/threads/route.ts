
import axios from "axios";

export async function GET(request: Request) {
  try {
    // Extract the Authorization header from the incoming request
    const authHeader = request.headers.get("authorization");
    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/threads`, {
      headers: {
        'Authorization': authHeader  // Pass the Authorization header
      }
    });
    return new Response(JSON.stringify(response.data), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to fetch threads" }), { status: 500 });
  }
}
