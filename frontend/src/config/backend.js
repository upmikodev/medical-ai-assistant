// config/backend.js

const BACKEND_URL = "http://localhost:8000";

export async function runChatLocal(prompt) {
  try {
    const res = await fetch(`${BACKEND_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: prompt }),
    });

    const data = await res.json();
    return data.response || data.error;
  } catch (err) {
    return `Error conectando al backend: ${err.message}`;
  }
}
