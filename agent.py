from openai import OpenAI
import requests
import os

# 🔹 1. Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tavily_client = None
if os.getenv("TAVILY_API_KEY"):
    from tavily import TavilyClient
    tavily_client = TavilyClient()

messages = [
    {"role": "system", "content": "You are a smart AI assistant that can use tools when needed."}
]

# 🔹 2. Tool: Web Search
def web_search(query):
    if tavily_client:
        response = tavily_client.search(query=query, max_results=5, search_depth="basic")
        results = response.get("results", [])
        if results:
            return "\n\n".join(r.get("content", "") for r in results)
        return "No results found"

    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url).json()

    return response.get("AbstractText", "No results found")


# 🔹 3. Tool Definition (for LLM)
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for latest information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]


# 🔹 4. Agent Logic
def ask_agent(user_input):
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    msg = response.choices[0].message

    # ✅ If tool is called
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = eval(tool_call.function.arguments)

        # Call tool
        result = web_search(args["query"])

        # VERY IMPORTANT: append assistant message first
        messages.append(msg)

        # Then append tool response
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

        # Call LLM AGAIN with tool result
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        msg = response.choices[0].message

    reply = msg.content

    messages.append({
        "role": "assistant",
        "content": reply
    })

    return reply



# 🔹 5. Run Loop (CLI)
if __name__ == "__main__":
    print("🤖 AI Assistant (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        answer = ask_agent(user_input)
        print("AI:", answer)