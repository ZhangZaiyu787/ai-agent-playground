import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent          # 新版导入
from langchain.tools import tool

load_dotenv()

# 模型
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)

# 工具
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

tools = [read_file, query_user]

# 创建 ReAct Agent（新版 API 名称变了，本质没变）
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个智能助手，可以根据需要调用工具。回答尽量简洁。"
)

# 流式观察 ReAct 循环
def run_agent(user_input: str):
    print(f"\n用户: {user_input}")
    print("=" * 50)
    for step in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="values"
    ):
        # 每次迭代的 step 是一个完整的 {"messages": [...]} 字典。
        msg = step["messages"][-1] # step["messages"][-1] 取出消息列表中的最后一条，也就是此次迭代中刚产生的新消息。
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"🔧 调用工具: {tc['name']}({tc['args']})")
        elif hasattr(msg, "content") and msg.content:
            role = "🤖 Agent" if msg.type == "ai" else "📋 工具返回"
            print(f"{role}: {msg.content}")

# 也可以使用 invoke 形式，来获取更简洁直观的输出
def run_agent_invoke(user_input: str):
    print(f"\n用户: {user_input}")
    print("=" * 50)
    # 一次性调用，返回最终完整状态
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )
    # 最终回答在最后一条消息里
    final_msg = result["messages"][-1]
    print(f"🤖 Agent: {final_msg.content}")

# 测试
if __name__ == "__main__":
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("LangGraph 是用于构建有状态 Agent 的框架。")

    run_agent("请帮我查一下张三的信息")
    run_agent("读取文件 test.txt 的内容")

    run_agent_invoke("帮我查一下李四的信息")

## run_agent 函数详解：

# agent.stream(...)：这是 LangGraph Agent 的流式调用方法，它返回一个生成器，每产出一次状态就 yield 一次。
# 参数 1：初始状态
# {"messages": [{"role": "user", "content": user_input}]}
# LangGraph Agent 的状态是一个字典，这里我们传入了初始的 messages 列表，其中只包含用户刚刚发送的问题。Agent 内部的图会从这个状态开始执行。
# 参数 2：stream_mode="values"
# 指定流模式为 "values"，意思是每次 yield 出的都是完整的当前状态（即整个 {"messages": [...]} 字典），而不是只返回增量。这样我们可以直接访问最新的消息列表，方便打印。