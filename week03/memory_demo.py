import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


load_dotenv()

# 1. 初始化模型
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3
)

# 2. 提示模板（带历史插槽）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的私人助手，请记住用户说过的话。"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# 3. 基础链
chain = prompt | model

# 4. 会话存储
store = {}

def get_session_history(session_id: str):
    """获取或创建指定会话的历史记录"""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 5. 带记忆的链
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# ===== 交互式命令行 =====
print("=" * 50)
print("带记忆的聊天机器人")
print("命令：")
print("  :history  - 查看当前会话历史")
print("  :clear    - 清空当前会话记忆")
print("  :switch <id> - 切换到指定会话")
print("  :exit     - 退出")
print("=" * 50)

session_id = "default"

while True:
    try:
        user_input = input("\n你: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n再见！")
        break

    if not user_input:
        continue

    # 处理命令
    if user_input.startswith(":"):
        cmd = user_input[1:].lower().split()
        if cmd[0] == "exit":
            print("再见！")
            break
        elif cmd[0] == "history":
            msgs = store.get(session_id)
            if not msgs or not msgs.messages:
                print("（无历史记录）")
            else:
                for msg in msgs.messages:
                    role = "用户" if msg.__class__.__name__ == "HumanMessage" else "助手"
                    print(f"{role}: {msg.content}")
            continue
        elif cmd[0] == "clear":
            if session_id in store:
                store[session_id].clear()
                print("记忆已清空。")
            else:
                print("没有可清空的记忆。")
            continue
        elif cmd[0] == "switch" and len(cmd) > 1:
            session_id = cmd[1]
            print(f"已切换到会话 {session_id}")
            continue
        else:
            print("未知命令，可用 :history / :clear / :switch <id> / :exit")
            continue

    # 正常对话
    try:
        response = chain_with_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"助手: {response.content}")
    except Exception as e:
        print(f"出错: {e}")