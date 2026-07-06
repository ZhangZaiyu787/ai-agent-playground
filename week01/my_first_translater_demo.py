import os
from time import strftime
from urllib import response
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMT = "你是一个翻译助手，输入中文请给出英文翻译，输入英文请给出中文翻译，输入其他请直接给出中文翻译，不需要其他额外的输出"

def translate(user_input, historys):
    messages = [{"role" : "system", "content" : SYSTEM_PROMT}]

    for h in historys[-5:]:
        messages.append({"role" : "user", "content" : "h[origin]"})
        messages.append({"role" : "assistant", "content" : "h[translate]"})
    messages.append({"role" : "user", "content" : user_input})
   # messages.append({"role": "user", "content": text})


    max_retry = 3
    for attemp in range(1, max_retry + 1):
        try:
            response = client.chat.completions.create(
                model = "deepseek-v4-flash",
                messages=messages,
                temperature=0.3,   # 低温度使翻译更稳定
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [错误] 第 {attempt} 次尝试失败: {e}")
            if attemp == max_retry:
                print("  [重试耗尽] 翻译失败，请检查网络或 API Key。")
                return None

def main():
    print("=" * 50)
    print("欢迎使用翻译助手")
    print("输入'history!'查看历史记录")
    print("输入'exit!'退出")
    print("=" * 50)

    historys = []

    while True:
        try:
            user_input = input("请输入需要翻译的文字\n").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input == "exit!":
            print("再见！")
            break

        if user_input == "history!":
            if not historys:
                print("没有历史记录")
            else:
                print('---- 翻译历史 ----')
                for i, h in enumerate(historys, 1):
                    print(f"{i}. {h['time']} {h['origin']} -> {h['translate']}")
                print('-----------------')
            continue
        
        translated = translate(user_input, historys)

        if translated:
            print('翻译结果为：', translated)
            historys.append({"time" : datetime.now().strftime("%H:%M:%S"),
                            "origin" : user_input,
                            "translate" : translated})


if __name__ == "__main__":
    main()