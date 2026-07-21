import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.5
)

# 1. 生成大纲的模板
outline_prompt = ChatPromptTemplate.from_template(
    "请为以下主题生成一份详细的文章大纲（列出 3 个要点）：\n\n主题：{topic}"
)

# 2. 根据大纲写文章的模板
write_prompt = ChatPromptTemplate.from_template(
    "根据以下大纲撰写一篇文章，字数约 200 字：\n\n大纲：\n{outline}"
)

# 3. 润色文章的模板
polish_prompt = ChatPromptTemplate.from_template(
    "请润色以下文章，使其语言更流畅、专业，保留原意：\n\n原文：\n{draft}"
)

# 生成大纲的链
gen_outline = outline_prompt | model

# 写文章的链（带转换）
write_chain = (
    RunnableLambda(lambda output: {"outline": output.content})
    | write_prompt
    | model
)

# 润色的链（带转换）
polish_chain = (
    RunnableLambda(lambda output: {"draft": output.content})
    | polish_prompt
    | model
)

# 完整链路：大纲 → 文章 → 润色
full_chain = gen_outline | write_chain | polish_chain

# 使用 RunnablePassthrough 保留中间结果的链
chain_with_intermediate = (
    RunnablePassthrough.assign(
        # 先生成大纲
        outline=gen_outline
    )
    .assign(
        # 根据大纲写文章，注意 outline 的值是 AIMessage，需提取 content
        draft=RunnableLambda(lambda x: {"outline": x["outline"].content}) | write_prompt | model
    )
    .assign(
        # 根据文章生成润色稿
        final=RunnableLambda(lambda x: {"draft": x["draft"].content}) | polish_prompt | model
    )
    .pick(["topic", "outline", "draft", "final"])   # 保留需要的字段
)

if __name__ == "__main__":
    topic = "人工智能对未来教育的影响"
    print(f"主题：{topic}\n")
    
    # 仅最终润色结果
    final_result = full_chain.invoke({"topic": topic})
    print("=== 润色后文章 ===")
    print(final_result.content)

    print("\n" + "=" * 50 + "\n")

    # 包含中间结果
    all_results = chain_with_intermediate.invoke({"topic": topic})
    print("=== 大纲 ===")
    print(all_results["outline"].content)
    print("\n=== 正文 ===")
    print(all_results["draft"].content)
    print("\n=== 润色稿 ===")
    print(all_results["final"].content)