from bs4 import BeautifulSoup
import re
import json


def parse_law_to_chunks(html_content):
    """
    解析法律页面 HTML，按“条”为粒度进行 Chunk 切分，提取元数据并构造结构化数据。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # ==========================================
    # 1. 提取元信息 (必须在清理隐藏节点之前提取)
    # ==========================================
    metadata = {
        "source": "",
        "takeEffect": "",
        "lawType": "",
        "whoMake": "",
        "status": ""
    }

    # 提取 Source
    title_input = soup.find('input', id='ArticleTitle')
    if title_input and title_input.get('value'):
        metadata["source"] = title_input.get('value').strip()
    else:
        # Fallback 方案：找标题
        title_node = soup.find('h1') or soup.find(class_=re.compile(r'title|art-title'))
        metadata["source"] = title_node.get_text(strip=True) if title_node else ""

    # 辅助函数：根据 strong 标签的文本提取相邻的内容
    def get_meta_value(keyword):
        strong_tag = soup.find('strong', string=re.compile(keyword))
        if strong_tag:
            # 情况1：目标值在相邻的 span 标签的 title 属性里（如：制定机关、时效性）
            next_span = strong_tag.find_next_sibling('span')
            if next_span and next_span.get('title'):
                return next_span.get('title').strip()

            # 情况2：目标值直接跟在 strong 标签所在的父节点文本里（如：施行日期）
            parent_text = strong_tag.parent.get_text(strip=True)
            # 剔除掉 label 自身，剩下的就是值
            val = parent_text.replace(strong_tag.get_text(strip=True), '').strip()
            return val
        return ""

    metadata["takeEffect"] = get_meta_value("施行日期")
    metadata["whoMake"] = get_meta_value("制定机关")
    metadata["status"] = get_meta_value("时效性")
    metadata["lawType"] = get_meta_value("法规类别")

    # ==========================================
    # 2. 清理 DOM 树（剔除干扰节点）
    # ==========================================
    noise_classes = ['TiaoYinV2', 'c-icon', 'fbWindow-btn', 'fb-dropdown', 'TyFblx']
    for noise in noise_classes:
        for el in soup.find_all(class_=noise):
            el.decompose()

    for hidden_input in soup.find_all('input', type='hidden'):
        hidden_input.decompose()

    # ==========================================
    # 3. 遍历 DOM，按“条”进行 Chunk 切分
    # ==========================================
    chunks = []
    chunk_index = 0

    # 状态记录器
    current_chapter = ""
    current_section = ""
    current_article_num = ""
    current_article_content = []  # 缓存当前法条的多段文字（款、项）

    # 内部辅助函数：去除“第一章 ”、“第二节 ”等前缀
    def clean_hierarchy_text(text):
        if not text:
            return ""
        # 匹配 第x章、第x节、第x编 后面跟着的内容
        # 这里同时也处理掉可能存在的全角/半角空格
        cleaned = re.sub(r'^第[一二三四五六七八九十百千]+[章节编]\s*', '', text)
        return cleaned.strip()

    # 内部函数：打包生成一个 Chunk
    def flush_article():
        nonlocal chunk_index, current_article_num, current_article_content
        if current_article_num and current_article_content:
            # 1. 处理层级路径
            path_parts = [metadata["source"]]

            clean_chap = clean_hierarchy_text(current_chapter)
            if clean_chap:
                path_parts.append(clean_chap)

            clean_sect = clean_hierarchy_text(current_section)
            if clean_sect:
                path_parts.append(clean_sect)

            # 2. 拼接前缀：用“——”连接各级目录
            prefix = "——".join(path_parts)

            # 3. 拼接正文：前缀与正文之间用“"——"”连接
            full_text = "\n".join(current_article_content)
            content_str = f"{prefix}——{full_text}"

            chunk = {
                "content": content_str,
                "metadata": {
                    "source": metadata["source"],
                    "takeEffect": metadata["takeEffect"],
                    "lawType": metadata["lawType"],
                    "whoMake": metadata["whoMake"],
                    "chapter": current_chapter,  # metadata里建议保留原始信息，方便后续检索
                    "section": current_section,
                    "articleNumber": current_article_num,
                    "status": metadata["status"]
                },
                "chunkId": str(chunk_index),
                "embedding": "[0.1, 0.2, ...]"
            }
            chunks.append(chunk)
            chunk_index += 1

        current_article_content = []


    # 获取所有可能包含内容的节点集合
    content_nodes = soup.find_all(class_=re.compile(r'navbian|navzhang|navjie|kuan-content|xiang-content'))

    for node in content_nodes:
        text = node.get_text(strip=True).replace('\u3000', ' ')
        if not text:
            continue

        cls = node.get('class', [])

        # 匹配【章】
        if any('navzhang' in c for c in cls) or re.match(r'^第[一二三四五六七八九十百千]+章', text):
            current_chapter = text
            current_section = ""  # 换章时，清空节的状态

        # 匹配【节】
        elif any('navjie' in c for c in cls) or re.match(r'^第[一二三四五六七八九十百千]+节', text):
            current_section = text

        # 匹配【款】（条文的第一段，或后续段落）
        elif 'kuan-content' in cls:
            # 检查这是否是一个新的“法条”开头（如：第十三条xxx）
            match = re.match(r'^(第[一二三四五六七八九十百千]+条)(.*)', text)
            if match:
                # 遇到新的法条，先把上一条存入 chunks
                flush_article()
                # 记录新法条的编号
                current_article_num = match.group(1)
                # 把原文塞进缓存
                current_article_content.append(text)
            else:
                # 如果没有“第x条”开头，说明它是当前法条的第二款、第三款，直接追加
                current_article_content.append(text)

        # 匹配【项】（如：(一)、(二) 等条件）
        elif 'xiang-content' in cls:
            current_article_content.append(f"    {text}")

    # 循环结束后，不要忘了把最后一条数据给 flush 出来
    flush_article()

    return chunks

