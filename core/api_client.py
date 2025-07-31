import time


class OpenAIStub:
    """OpenAI客户端的占位类，当未安装openai库时使用"""

    def __init__(self, *args, **kwargs):
        pass

    class Chat:
        @staticmethod
        def completions_create(*args, **kwargs):
            class DummyResponse:
                @staticmethod
                def choices():
                    class DummyChoice:
                        message = type('', (), {'content': '演示模式下的响应'})()

                    return [DummyChoice()]

            return DummyResponse()


# 尝试导入真实的OpenAI客户端
try:
    from openai import OpenAI
except ImportError:
    OpenAI = OpenAIStub


# log_ai_system/core/api_client.py
class DeepSeekAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"  # 符合官方base_url
        )

    def completions_create(self, model, prompt, max_tokens=5000, temperature=0.3, retry=3):
        attempt = 0
        while attempt < retry:
            try:
                return self.client.chat.completions.create(
                    model=model,
                    messages=[  # 严格匹配官方messages格式
                        {"role": "system", "content": "你是专业的信息安全日志分析专家，生成可执行Python代码，只返回代码不解释。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False,
                    timeout=120
                )
            except Exception as e:
                attempt += 1
                print(f"API调用出错 (尝试 {attempt}/{retry}): {str(e)}")
                if attempt < retry:
                    time.sleep(2)
        raise Exception(f"API调用失败，已达到最大重试次数 ({retry}次)")
