import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

reasoning_content = response.choices[0].message.reasoning_content
content = response.choices[0].message.content

print("=" * 50)
print("【Turn 1 - Reasoning】")
print(response.choices[0].message.reasoning_content)
print("\n【Turn 1 - Answer】")
print(response.choices[0].message.content)

# Turn 2
# The reasoning_content will be ignored by the API
messages.append(response.choices[0].message)
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)


print("\n" + "=" * 50)
print("【Turn 2 - Reasoning】")
print(response.choices[0].message.reasoning_content)
print("\n【Turn 2 - Answer】")
print(response.choices[0].message.content)
# ...