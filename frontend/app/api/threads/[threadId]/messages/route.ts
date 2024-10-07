
import axios from "axios";

interface Params {
  threadId: string;
}

export async function GET(request: Request, { params }: { params: Params }) {
  const { threadId } = params;
  try {
    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/users/me/threads/${threadId}/messages`);
    return new Response(JSON.stringify(response.data), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to fetch messages" }), { status: 500 });
  }
}
