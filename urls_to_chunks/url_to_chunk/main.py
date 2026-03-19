import json

import config
from urls_to_chunks.url_to_chunk.format_single_doc import parse_law_to_chunks
from urls_to_chunks.url_to_chunk.get_single_doc import fetch_page_with_cookies


def main():
    """主函数，用于测试"""
    # 目标URL
    url = "https://www.pkulaw.com/chl/d653ed619d0961c0bdfb.html?keyword=%E7%BD%91%E7%BB%9C%E4%BF%A1%E6%81%AF%E4%BF%9D%E6%8A%A4%E6%B3%95&way=listView"

    # Cookie字符串
    cookie_str = config.COOKIE_STR

    # 指定chromedriver路径
    chromedriver_path = r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe'

    # 调用封装的函数获取页面内容
    print("开始获取页面内容...")
    html_content = fetch_page_with_cookies(
        target_url=url,
        cookie_str=cookie_str,
        chromedriver_path=chromedriver_path,
        headless=False# 设置为False可以显示浏览器窗口，便于调试
    )

    chunks = parse_law_to_chunks(html_content)

    with open("chunks.txt", "w", encoding="utf-8") as file:
        for chunk in chunks:
            # 将字典转换为JSON字符串
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()