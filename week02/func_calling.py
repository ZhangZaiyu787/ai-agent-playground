from http import client
import os
from urllib import response
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

messages = [{"role" : "system", "content" : "你是一个天气助手"}]

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

def get_weather_mock(location):
    return "Cloudy 7~13°C"


while True:
    user_input = input()

    if user_input == "exit!":
        break

    messages.append({"role" : "user", "content" : user_input})

    response = client.chat.completions.create(
        model = "deepseek-v4-flash",
        messages=messages,
        tools=tools
    )

    assistant_msg = response.choices[0].message
    messages.append(response.choices[0].message)

    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            if tool_call.function.name == "get_weather":
                args = json.loads(tool_call.function.arguments)
                location = args.get("location")
                result = get_weather_mock(location)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        # 再次调用模型生成最终回复
        final_response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages
        )
        print(f"Assistant: {final_response.choices[0].message.content}")
        messages.append(final_response.choices[0].message)
    else:
        print(f"Assistant: {assistant_msg.content}")
        break
