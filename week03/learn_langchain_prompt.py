import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate #文本补全模型
from langchain_core.prompts import ChatPromptTemplate #对话模型
from langchain_core.prompts import MessagesPlaceholder #动态注入历史
from langchain_deepseek import ChatDeepSeek 


# 初始化模型
client = ChatDeepSeek(
    model="deepseek-chat",
    temperature=1,
    api_key=os.getenv("DEEPSEEK_API_KEY")  # 不写就从环境变量 DEEPSEEK\_API\_KEY 读
)

# 构造消息列表
messages = [
    SystemMessage(content="你是一个专业的 Python 开发工程师，回答简洁准确。"),
    HumanMessage(content="用一句话解释什么是面向对象编程")
]

# 调用模型
response = client.invoke(messages)

print(type(response))  # <class 'langchain_core.messages.ai.AIMessage'>
print(response.content)  # 回答文本

# result=client.invoke(["什么是向量数据库？"])
# print(result.content)

# 定义模版
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{source_lang}到{target_lang}的翻译器，只输出译文。"),
    ("user", "{input}")
])


# 3. 用 LCEL 拼接链：模板 → 模型
# LCEL 的 | 操作符是数据从左流向右：
# template 处理用户输入 → 生成 Prompt → 传给 llm 调用 API → 返回结果。
# 所以顺序是 template | client
chain = template | client
 
result = chain.invoke({
    "source_lang":"英文",
    "target_lang": "中文",
    "input": "hello world"
})
print("英译中:", result.content)

history_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，请记住用户的姓名。"),
    MessagesPlaceholder("history"),   # 动态插入历史消息
    ("user", "{input}")
])

chain = history_template | client

# 第一轮
history = []
res1 = chain.invoke({"history": history, "input": "我叫小明"})
print("Bot:", res1.content)
history.append(HumanMessage("我叫小明"))
history.append(res1)  # res1 是 AIMessage

# 第二轮
res2 = chain.invoke({"history": history, "input": "我叫什么名字？"})
print("Bot:", res2.content)

### ChatModel 核心属性

# `.invoke(messages)`：同步调用，返回一个 `AIMessage` 对象
# `.stream(messages)`：流式输出
# `.ainvoke(messages)`：异步调用

# 返回的 `AIMessage` 对象：
# `.content`：回答的文本内容
# `.tool_calls`：如果有工具调用，在这里