import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

EXAMPLE INPUT: 
Which is the highest mountain in the world? Mount Everest.

EXAMPLE JSON OUTPUT:
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""

user_prompt = "Which is the longest river in the world? The Nile River."

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)

print(json.loads(response.choices[0].message.content))

# 什么时候该用 system_prompt？

# 当你需要约束模型行为时，建议加上：

# 指定输出格式（如前面的 JSON 输出示例）。
# 固定角色（“你是 Python 技术顾问”、“你是一个严谨的数学老师”）。
# 设定安全规则（“不要回答敏感话题”、“必须用中文回复”）。
# 提供上下文或知识（“你了解以下产品信息：……”）。
# 控制语气和风格（“用风趣幽默的风格回答”）。
# 如果任务很简单（如直接翻译、总结），不写 system 消息也可以，但在 Agent 开发中，几乎都建议加上 system 消息，因为它能大幅提高模型输出的稳定性和一致性。