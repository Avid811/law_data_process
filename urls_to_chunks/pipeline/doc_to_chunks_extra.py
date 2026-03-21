import json
import config
from urls_to_chunks.pipeline.format_single_doc import parse_law_to_chunks
from urls_to_chunks.pipeline.get_single_doc import fetch_page_with_cookies


def filter_chunks_by_keywords(keywords, input_file=None, chunks=None):
    """
    根据关键词筛选chunks并重新编号

    Args:
        keywords: 关键词数组，如["网络", "算法"]
        input_file: 已保存的chunks文件路径（可选）
        chunks: 已解析的chunks列表（可选）

    Returns:
        筛选后的chunks列表
    """
    # 如果直接提供chunks参数，使用它
    if chunks is not None:
        all_chunks = chunks
    # 否则从文件读取
    elif input_file is not None:
        all_chunks = []
        with open(input_file, "r", encoding="utf-8") as file:
            for line in file:
                chunk = json.loads(line.strip())
                all_chunks.append(chunk)
    else:
        raise ValueError("必须提供input_file或chunks参数")

    # 筛选包含任意关键词的chunks
    filtered_chunks = []
    for chunk in all_chunks:
        content = chunk.get("content", "")

        # 检查是否包含任意关键词
        for keyword in keywords:
            if keyword in content:
                filtered_chunks.append(chunk)
                break  # 已匹配到一个关键词，无需检查其他关键词

    # 重新编号
    for idx, chunk in enumerate(filtered_chunks):
        chunk["chunkId"] = str(idx)  # 重新编号，从0开始

    return filtered_chunks


def save_filtered_chunks(filtered_chunks, output_file, law_name=None):
    """
    保存筛选后的chunks

    Args:
        filtered_chunks: 筛选后的chunks列表
        output_file: 输出文件路径
        law_name: 法律名称（可选，用于生成文件名）
    """
    with open(output_file, "w", encoding="utf-8") as file:
        for chunk in filtered_chunks:
            # 将字典转换为JSON字符串
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"已保存 {len(filtered_chunks)} 个筛选后的chunks到: {output_file}")


def main():
    """主函数，用于测试"""
    # 目标URL
    url = "https://www.pkulaw.com/chl/1dd3a2fb498ecb3ebdfb.html?keyword=中华人民共和国数据安全法&way=listView"

    # Cookie字符串
    cookie_str = config.COOKIE_STR

    # 指定chromedriver路径
    chromedriver_path = r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe'

    # 关键词数组
    keywords = ["网络", "算法"]  # 替换为您的关键词

    # 1. 获取页面内容
    print("开始获取页面内容...")
    html_content = fetch_page_with_cookies(
        target_url=url,
        cookie_str=cookie_str,
        chromedriver_path=chromedriver_path,
        headless=False
    )

    # 2. 解析为chunks
    print("解析页面内容为chunks...")
    chunks = parse_law_to_chunks(html_content)

    # 3. 保存原始chunks（可选）
    original_file = "《中华人民共和国数据安全法》_original_chunks.txt"
    with open(original_file, "w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"已保存 {len(chunks)} 个原始chunks到: {original_file}")

    # 4. 筛选chunks
    print(f"使用关键词 {keywords} 进行筛选...")
    filtered_chunks = filter_chunks_by_keywords(keywords, chunks=chunks)

    # 5. 保存筛选结果
    keyword_str = "_".join(keywords)
    output_file = f"《中华人民共和国数据安全法》_filtered_{keyword_str}_chunks.txt"
    save_filtered_chunks(filtered_chunks, output_file)