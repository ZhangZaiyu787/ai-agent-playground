import os
import math
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 模型
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)

# 工具
@tool
def get_weather(location: str) -> str:
    """输入一个地点，返回这个地点的天气。当用户需要查询某个地点的天气时调用"""
    return f"{location} 当前天气：阴天，7~13°C，北风2级，湿度60%。"

@tool
def calculator(expression: str) -> str:
    """安全的计算器实现，只允许数字、运算符和数学函数。当用户需要计算时调用。"""
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "pow":math.pow,
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
    
@tool
def read_file(file_path: str) -> str:
    """读取指定路径的文件内容。当用户需要查看某个文件的内容时调用。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 {file_path} 不存在"
    except Exception as e:
        return f"读取失败：{str(e)}"

MOCK_DB = {
    "张三": {"age": 28, "city": "北京", "role": "工程师"},
    "李四": {"age": 24, "city": "上海", "role": "设计师"},
}

@tool
def query_user(username: str) -> str:
    """查询用户数据库，获取指定用户的详细信息（年龄、城市、职业）。
    当用户询问某人信息、个人资料时调用。"""
    user = MOCK_DB.get(username)
    if user:
        return f"姓名：{username}，年龄：{user['age']}，城市：{user['city']}，职业：{user['role']}"
    else:
        return f"未找到用户 {username}"
    
tools = [get_weather, calculator, read_file, query_user]

# 记忆模块（MemorySaver）
memory = MemorySaver()  # 内存检查点，可替换为 SqliteSaver 等持久化方案

# 创建agent

agent =  create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个智能助手，可以根据需要调用工具。回答尽量简洁。",
    checkpointer=memory      # 关键：启用多轮对话记忆
)

# 同步调用
def run_agent_invoke(user_input, thread_id: str = "default"):
    print(f"{user_input}")
    result = agent.invoke(
        {"messages":[{"role":"user", "content":user_input}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    #print(f"{result}")
    # 最终回答在最后一条消息里
    final_msg = result["messages"][-1]
    print(f"🤖 Agent: {final_msg.content}")

# 流式输出
def run_agent_stream(user_input, thread_id: str = "default"):
    print(f"{user_input}")
    print("="*50)
    for step in agent.stream(
        {"messages":[{"role":"user", "content":user_input}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="values"
    ):
        result = step["messages"][-1]
        if hasattr(result, "tool_calls") and result.tool_calls:
            for tc in result.tool_calls:
                print(f"🔧 调用工具: {tc['name']}({tc['args']})")
        elif hasattr(result, "content") and result.content:
            role = "🤖 Agent" if result.type == "ai" else "📋 工具返回"
            print(f"{role}: {result.content}")

# 测试
if __name__ == "__main__":
    # 创建测试文件
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("LangGraph 是用于构建有状态 Agent 的框架。")

    print("带记忆的智能助手（输入 ':exit' 退出，':new' 新建会话）")
    current_thread = "user_001"

    while True:
        try:
            user_input = input(f"\n[{current_thread}] 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input == ":exit":
            break
        if user_input == ":new":
            # 新建会话：生成新的 thread_id
            import random
            current_thread = f"user_{random.randint(100, 999)}"
            print(f"已切换到新会话: {current_thread}")
            continue

        # 使用流式模式，方便观察工具调用
        run_agent_stream(user_input, thread_id=current_thread)