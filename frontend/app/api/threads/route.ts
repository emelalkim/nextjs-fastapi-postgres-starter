
import axios from "axios";

export async function GET(request: Request) {
  try {
    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/users/me/threads`);
    return new Response(JSON.stringify(response.data), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to fetch threads" }), { status: 500 });
  }
}
