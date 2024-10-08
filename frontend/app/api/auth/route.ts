import axios from "axios";

export async function POST(request: Request) {
const body = await request.json();
try {
    const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth`, body);
    return new Response(JSON.stringify(response.data), { status: 200 });
} catch (error) {
    console.log(error)
    return new Response(JSON.stringify({ error: "Failed to authenticate" }), { status: 500 });
}
}
  
