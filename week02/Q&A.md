# Q1: 为什么 .env 里定义的 OPENAI_API_KEY，在代码中使用os.getenv('DEEPSEEK_API_KEY')，且打印os.getenv('DEEPSEEK_API_KEY')的值为None，但API依旧能调用成功？

 A1：虽然在代码里显式写了 api_key=os.getenv("DEEPSEEK_API_KEY")，但因为 os.getenv 返回了 None，所以传给 OpenAI() 构造函数的参数实际上是：
···
OpenAI(api_key=None, base_url="https://api.deepseek.com")
···
当传的 api_key=None 时，OpenAI 的 Python SDK 不会直接报错，而是会自动去系统环境变量中查找名为 OPENAI_API_KEY 的变量作为兜底。
也就是说，代码实际生效的密钥是 os.getenv('OPENAI_API_KEY') 的值。