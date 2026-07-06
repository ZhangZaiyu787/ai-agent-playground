import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com/beta",
)

response = client.completions.create(
    model="deepseek-v4-flash",
    prompt="def fib(a):",
    suffix="    return fib(a-1) + fib(a-2)",
    max_tokens=128
)
print(response.choices[0].text)

## client.completions.create 和 client.chat.completions.create 的主要区别

# 这两种调用方式分别对应 OpenAI API 的两类不同接口：**Completions API** 和 **Chat Completions API**。它们在输入格式、使用场景和底层模型行为上有本质区别。
# ---
# ## 对比表

# | 对比维度 | `client.completions.create` | `client.chat.completions.create` |
# |----------|----------------------------|----------------------------------|
# | **接口类型** | 文本补全 (Completions) | 聊天补全 (Chat Completions) |
# | **输入格式** | 单个 `prompt` 字符串（可选 `suffix`） | 消息列表 `messages`，每条消息有 `role` 和 `content` |
# | **角色概念** | 无角色，只是续写文本 | 有 `system`, `user`, `assistant`, `tool` 等角色区分 |
# | **典型用途** | 代码填充、文本续写、FIM（中间填充） | 对话、指令执行、工具调用、多轮交互 |
# | **是否支持对话历史** | 不支持，只能传一个 prompt | 支持，通过 `messages` 列表传递完整对话上下文 |
# | **是否支持函数调用/工具** | 不支持 | 支持 `tools` 参数和 `tool_calls` 响应 |
# | **是否支持停止符** | 支持 `stop` 参数 | 支持 `stop` 参数 |
# | **返回字段** | `response.choices[0].text` | `response.choices[0].message.content` |
# | **适用模型** | 传统 GPT-3 系列、代码模型（如 Codex、DeepSeek FIM） | GPT-3.5、GPT-4、DeepSeek 等所有现代聊天模型 |

# ---

# ## 核心区别

# ### 1. 输入结构不同
# - **Completions**：只需一个 `prompt` 字符串，模型会续写后续内容。
#   ```python
#   response = client.completions.create(
#       model="deepseek-v4-flash",
#       prompt="def fib(a):",
#       suffix="    return fib(a-1) + fib(a-2)",
#   )
#   ```
# - **Chat Completions**：需要结构化的消息列表，每条消息有 `role`。
#   ```python
#   response = client.chat.completions.create(
#       model="deepseek-chat",
#       messages=[{"role": "user", "content": "写一个斐波那契函数"}]
#   )
#   ```

# ### 2. 功能范围不同
# - **Completions** 是底层 API，只能做“文本续写”，**不支持**函数调用、对话记忆、角色设定等高级功能。
# - **Chat Completions** 是高层 API，专门为现代聊天模型设计，支持**多轮对话、工具调用、推理链**等，是开发 AI Agent 的主要接口。

# ### 3. 特殊能力：代码填充 (FIM)
# 你问的这段代码是 **Fill-in-the-Middle** 的特殊用法：
# ```python
# client.completions.create(
#     prompt="def fib(a):",
#     suffix="    return fib(a-1) + fib(a-2)",
# )
# ```
# - `prompt` 是代码的前缀，`suffix` 是代码的后缀。
# - 模型需要生成**中间缺失的部分**。
# - **这种填充能力在 `chat.completions` 中目前通常不支持**，因为聊天模型的设计目标不是“补全中间的代码”，而是“根据指令生成整个回复”。
