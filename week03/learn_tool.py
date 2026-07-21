import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.tools import tool

# 开启调试模式，会打印 Agent 每一步的推理和工具调用细节
import langchain
#langchain.debug = True

load_dotenv()

# ---------- 1. 初始化模型 ----------
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)

# ---------- 2. 定义自定义工具 ----------

# 工具一：读取本地文件
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

# 模拟数据库
MOCK_DB = {
    "张三": {"age": 28, "city": "北京", "role": "工程师"},
    "李四": {"age": 24, "city": "上海", "role": "设计师"},
}

# 工具二：查询用户信息
@tool
def query_user(username: str) -> str:
    """查询用户数据库，获取指定用户的详细信息（年龄、城市、职业）。
    当用户询问某人信息、个人资料时调用。"""
    user = MOCK_DB.get(username)
    if user:
        return f"姓名：{username}，年龄：{user['age']}，城市：{user['city']}，职业：{user['role']}"
    else:
        return f"未找到用户 {username}"

# ---------- 3. 创建 Agent ----------
tools = [read_file, query_user]

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个智能助手，可以根据需要调用工具。回答尽量简洁。"
)

# ---------- 4. 测试 ----------
def test_agent():
    # 先准备一个测试文件
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("这是测试文件内容，用于验证读取工具。")

    # 场景一：查询用户（应调用 query_user）
    print("\n===== 测试1：查询用户 =====")
    res1 = agent.invoke({
        "messages": [{"role": "user", "content": "请帮我查一下张三的信息"}]
    })
    print("Agent 最终回答：", res1["messages"][-1].content)

    # 场景二：读取文件（应调用 read_file）
    print("\n===== 测试2：读取文件 =====")
    res2 = agent.invoke({
        "messages": [{"role": "user", "content": "读取文件 test.txt 的内容"}]
    })
    print("Agent 最终回答：", res2["messages"][-1].content)

    # 场景三：普通对话（不应调用任何工具）
    print("\n===== 测试3：普通对话 =====")
    res3 = agent.invoke({
        "messages": [{"role": "user", "content": "你好，今天天气不错"}]
    })
    print("Agent 最终回答：", res3["messages"][-1].content)

if __name__ == "__main__":
    test_agent()