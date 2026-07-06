import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com/beta",
)

messages = [
    {"role": "user", "content": "Please write quick sort code"},
    {"role": "assistant", "content": "```python\n", "prefix": True} #这种模式相当于在说：“模型，这是你还没说完的话，请从 ```python\n 后面接着写下去。
]
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    stop=["```"],
)
print(response.choices[0].message.content)

# 这种技术有什么用？

# 代码补全/内联生成：在 IDE 或 AI 编程助手中，可以给定已输入的代码片段，让模型续写。
# 精确控制格式：避免每次都要解析 Markdown 代码块，或者让模型输出多余的说明文字。
# Agent 开发：当你需要模型生成特定格式的中间结果（比如 JSON 片段、SQL 语句）时，可以用前缀引导输出开头，再用 stop 限定结尾，确保格式完全可控。