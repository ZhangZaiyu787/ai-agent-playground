import instructor
import os
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
print(f"{os.getenv('DEEPSEEK_API_KEY')}")
print(os.environ.get('DEEPSEEK_API_KEY')) 
client = instructor.from_openai(OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"),
    mode=instructor.Mode.TOOLS,   # 推荐：用 Function Calling 方式实现结构化输出
    
)

class UserInfo(BaseModel):
    name: str = Field(description="用户姓名")
    age: int = Field(ge=0, le=120, description="年龄，0-120 之间")

# 直接得到 Pydantic 对象，而不是字符串
user = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "张三今年 28 岁"}],
    response_model=UserInfo,
    max_retries=3                 # 重试最多 3 次（默认 1 次）
)
print(user.name)  # 张三
print(user.age)   # 28