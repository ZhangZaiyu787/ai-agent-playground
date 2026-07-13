import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ================= 工具定义 =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather of a location.",
            "parameters": {
                "type": "object",
                "properties": { 
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform a mathematical calculation. Supports +, -, *, /, ** (power), sqrt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g. '3*4+2' or 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# ================= 工具实现 =================
import math

def get_weather_mock(location):
    """模拟天气查询"""
    return f"Cloudy 7~13°C (mocked for {location})"

def calculator_real(expression):
    """安全的计算器实现，只允许数字、运算符和数学函数"""
    # 安全白名单：只允许数字、运算符、空格、小数点、括号和 math 中的函数
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "pow": math.pow,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
    }
    try:
        # 用 eval 但限制可访问的名称，提高安全性
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"

# 工具名到函数的映射
TOOL_MAP = {
    "get_weather": get_weather_mock,
    "calculator": calculator_real
}


# ================= 对话初始化 =================
messages = [
    {"role": "system", "content": "你是一个智能助手，可以查询天气和执行数学计算。请根据用户的问题选择适当的工具。"}
]

print("智能助手已启动。输入 'exit!' 退出。")

while True:
    user_input = input("User: ").strip()
    if user_input.lower() == "exit!":
        break

    messages.append({"role": "user", "content": user_input})

    # 第一轮调用：可能触发工具调用
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=tools
    )

    assistant_msg = response.choices[0].message
    messages.append(assistant_msg)

    # 处理工具调用
    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            # 根据工具名分发
            if func_name in TOOL_MAP:
                # 提取参数（不同工具的参数字段不同）
                if func_name == "get_weather":
                    result = TOOL_MAP[func_name](args.get("location"))
                elif func_name == "calculator":
                    result = TOOL_MAP[func_name](args.get("expression"))
                else:
                    result = "未知工具"
            else:
                result = f"工具 {func_name} 未实现"

            # 将工具结果返回给模型
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # 再次调用模型，让它基于工具结果生成最终答案
        final_response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages
        )
        final_msg = final_response.choices[0].message
        print(f"Assistant: {final_msg.content}")
        messages.append(final_msg)
    else:
        # 没有工具调用，直接输出文本回复
        print(f"Assistant: {assistant_msg.content}")