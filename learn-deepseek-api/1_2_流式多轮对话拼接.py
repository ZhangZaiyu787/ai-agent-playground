import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
# Turn 1
print("========== 第一轮：9.11 vs 9.8 ==========")
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    stream=True,  # 开启流式
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
        reasoning_content += chunk.choices[0].delta.reasoning_content
    elif chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
        content += chunk.choices[0].delta.content

print("\n\n✅ 第一轮完成\n")

# Turn 2
# The reasoning_content will be ignored by the API
print("========== 第二轮：strawberry 中有几个 R ==========")
messages.append({"role": "assistant", "reasoning_content": reasoning_content, "content": content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    stream=True,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

reasoning_content2 = ""
content2 = ""

for chunk in response:
    delta = chunk.choices[0].delta
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        print(delta.reasoning_content, end="", flush=True)
        reasoning_content2 += delta.reasoning_content
    elif delta.content:
        print(delta.content, end="", flush=True)
        content2 += delta.content

print("\n\n✅ 第二轮完成")
# ...

# 流式与非流式的区别：
# 
# 非流式：脚本等待 3-5 秒，然后一次性打印所有文本。适合后台批处理，获取完整结果
# 流式：文字一个个出现，推理过程实时可见。适合前端交互、Agent 实时反馈，让用户感知模型正在“思考”
# 
# #