import json

from Tools.scripts.verify_ensurepip_wheels import print_notice

import config
from urls_to_chunks.pipeline.format_single_doc import parse_law_to_chunks
from urls_to_chunks.pipeline.get_single_doc import fetch_page_with_cookies


def main():
    """串联爬取法条+格式化chunks的主流程"""
    # 目标URL
    url = "https://www.pkulaw.com/protocol/790df01963a8406c804742100c2ad401bdfb.html?keyword=%E4%BA%92%E8%81%94%E7%BD%91%E8%B7%9F%E5%B8%96%E8%AF%84%E8%AE%BA%E6%9C%8D%E5%8A%A1%E7%AE%A1%E7%90%86%E8%A7%84%E5%AE%9A&way=listView"





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

    print(html_content)
    chunks = parse_law_to_chunks(html_content)

    with open("../../part_chunks_source/《互联网跟帖评论服务管理规定》_chunks.txt", "w", encoding="utf-8") as file:
        for chunk in chunks:
            # 将字典转换为JSON字符串
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()