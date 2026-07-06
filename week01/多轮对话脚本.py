import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

message = [{"role":"system", "content":"你是一个私人助手"}]

while True:
    user_input = input("User: ")
    if user_input.lower() == 'exit':
        break

    message.append({"role":"user", "content":user_input})

    response = client.chat.completions.create(
        model = "deepseek-v4-flash",
        messages = message
    )

    print(f"{response.choices[0].message.content}\n")

    message.append(response.choices[0].message)
