import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

ZERO_MESSAGE = "你是一个数学家"
FEW_SHOT_MEAASGE = '''你是一个数学家,请按照示例的格式回答问题。

示例1：
问题： 一个班有 30 个学生，男生比女生多 4 人，男生有多少人？
答案： 男生有 17 人。

示例2：
问题： 小明买了 5 本书，每本 8 元，他付了 50 元，找回多少元？
答案： 找回 10 元。

现在回答下面的问题，只给出答案。'''
COT_MEAASGE = '你是一个数学家。回答问题时请逐步推理，先列出已知条件，再分步骤计算，最后给出答案.'

messages = [{"role" : "system", "content" : ZERO_MESSAGE}]

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

while True:

    user_input = input()

    if user_input == 'exit!':
        break

    messages.append({"role" : "user", "content" : user_input})

    response = client.chat.completions.create(
        messages=messages,
        model="deepseek-v4-flash",
        temperature=1,
        max_tokens=1024
    )

    print(f"{response.choices[0].message.content}")

    messages.append(response.choices[0].message)