import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import math


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tools = [
    {
        "type":"function",
        "function":{
            "name":"get_weather",
            "description":"you can input a location, and i will return the weather in location",
            "parameters":{
                "type":"object",
                "properties":{ #用来定义工具函数每个参数的名称、类型和含义，让模型知道该传递哪些字段以及它们代表什么。
                    "location":{
                        "type":"string",
                        "description":"the location where you want to konw weather"
                    }
                },
                "required":["location"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"calculator",
            "description":"you can input a number, will return a result",
            "parameters":{
                "type":"object",
                "properties":{
                    "expression":{
                        "type":"string",
                        "description":"the expression which you input"
                    }
                },
                "required":["expression"]
            }
        }
        
    }
]

def get_weather_mock(location):
    return f"{location} 当前天气：阴天，7~13°C，北风2级，湿度60%。"

def calculator_mock(expression):
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
    "calculator": calculator_mock
}

messages = [{"role":"system","content":"你是一个私人助手，支持查询天气和计算器功能"}]

while True:
    user_input = input()
    if user_input=="exit!":
        break

    messages.append({"role":"user",
                     "content":user_input})
    
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=tools
    )

    assistant_msg = response.choices[0].message
    messages.append(assistant_msg)

    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            func_name=tool_call.function.name
            args=json.loads(tool_call.function.arguments)
            print(f"{func_name}, {args}, {tool_call.id}")
            if func_name in TOOL_MAP:
                if func_name=="get_weather":
                    result = TOOL_MAP[func_name](args.get("location"))
                elif func_name=="calculator":
                    result = TOOL_MAP[func_name](args.get("expression"))
                else:
                    result="unknow tools"
            else:
                result = f"工具 {func_name} 未实现"

            messages.append({"role":"tool","tool_call_id": tool_call.id,"content":result})

    
        final_response=client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages
        )

        result_msg=final_response.choices[0].message
        print(f"Assistant {result_msg.content}")
        messages.append(result_msg)
    else:
        # 没有工具调用，直接输出文本回复
        print(f"Assistant: {assistant_msg.content}")

