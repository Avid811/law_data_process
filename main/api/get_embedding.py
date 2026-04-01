import os
from openai import OpenAI
from typing import List, Optional


def get_embedding(text: str,
                  model: str = "text-embedding-v3",
                  dimensions: int = 1024,
                  encoding_format: str = "float") -> List[float]:
    """
    获取文本的嵌入向量

    Args:
        text: 要生成嵌入向量的文本内容
        model: 使用的模型名称，默认为"text-embedding-v3"
        dimensions: 向量维度，默认为1024
        encoding_format: 编码格式，默认为"float"

    Returns:
        文本的嵌入向量列表

    Raises:
        ValueError: 当API密钥未设置或文本为空时
        Exception: 当API调用失败时
    """
    # 检查输入参数
    if not text or not text.strip():
        raise ValueError("文本内容不能为空")

    # 获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未设置OPENAI_API_KEY环境变量")

    # 创建客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    try:
        # 生成嵌入向量
        completion = client.embeddings.create(
            model=model or 'text-embedding-v3',
            input=text,
            dimensions=1024
        )

        # 返回嵌入向量
        return completion.data[0].embedding

    except Exception as e:
        raise Exception(f"生成嵌入向量失败: {str(e)}")

print(get_embedding('nihao'))
