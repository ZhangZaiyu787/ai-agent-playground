import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 系统提示词：定义翻译助手的行为
SYSTEM_PROMPT = """你是一个专业的翻译助手。请严格遵循以下规则：
1. 如果用户输入中文，将其翻译成英文。
2. 如果用户输入英文，将其翻译成中文。
3. 如果输入为其他语言，先检测语言，再翻译成中文。
4. 仅输出翻译结果，不要添加额外解释、问候或标点修饰，除非用户明确要求。
5. 保持专业术语的准确性，语气与原文一致。
"""

def translate(text, history):
    """调用 API 进行翻译，带重试机制"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 将最近 5 轮历史加入上下文（避免 token 过长）
    for h in history[-5:]:
        messages.append({"role": "user", "content": h["original"]})
        messages.append({"role": "assistant", "content": h["translated"]})
    messages.append({"role": "user", "content": text})

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                temperature=0.3,   # 低温度使翻译更稳定
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [错误] 第 {attempt} 次尝试失败: {e}")
            if attempt == max_retries:
                print("  [重试耗尽] 翻译失败，请检查网络或 API Key。")
                return None

def main():
    print("=" * 50)
    print("欢迎使用命令行翻译助手")
    print("输入 'history' 查看历史 | 输入 'exit' 退出")
    print("=" * 50)

    history = []  # 每条记录: {original, translated, time}

    while True:
        try:
            user_input = input("\n请输入要翻译的文本: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("再见！")
            break

        if user_input.lower() == "history":
            if not history:
                print("暂无翻译记录。")
            else:
                print("\n--- 翻译历史 ---")
                for i, h in enumerate(history, 1):
                    print(f"{i}. [{h['time']}] {h['original']} -> {h['translated']}")
                print("----------------\n")
            continue

        # 执行翻译
        translated = translate(user_input, history)
        if translated:
            print(f"翻译结果: {translated}")
            history.append({
                "original": user_input,
                "translated": translated,
                "time": datetime.now().strftime("%H:%M:%S")
            })

if __name__ == "__main__":
    main()