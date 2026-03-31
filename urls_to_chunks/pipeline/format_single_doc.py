from bs4 import BeautifulSoup, NavigableString
import re
import json
from collections import defaultdict


def parse_law_to_chunks(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # ==========================================
    # 1. 提取元信息 (保持原逻辑)
    # ==========================================
    metadata = {
        "source": "", "takeEffect": "", "lawType": "", "whoMake": "", "status": ""
    }
    title_input = soup.find('input', id='ArticleTitle')
    if title_input and title_input.get('value'):
        metadata["source"] = title_input.get('value').strip()
    else:
        title_node = soup.find('h1') or soup.find(class_=re.compile(r'title|art-title'))
        metadata["source"] = title_node.get_text(strip=True) if title_node else "法律文档"

    def get_meta_value(keyword):
        tag = soup.find('strong', string=re.compile(keyword))
        if tag:
            next_span = tag.find_next_sibling('span')
            if next_span and next_span.get('title'):
                return next_span.get('title').strip()
            return tag.parent.get_text(strip=True).replace(tag.get_text(strip=True), '').strip()
        return ""

    metadata.update({
        "takeEffect": get_meta_value("施行日期"),
        "whoMake": get_meta_value("制定机关"),
        "status": get_meta_value("时效性"),
        "lawType": get_meta_value("法规类别")
    })

    # ==========================================
    # 2. 清理干扰
    # ==========================================
    for el in soup.find_all(['script', 'style', 'textarea', 'footer', 'header']):
        el.decompose()

    # ==========================================
    # 3. 增强：规范化 DOM 结构，彻底解决嵌套和无标签文本问题
    # ==========================================
    # a. 消除源码格式带来的换行符干扰（避免法条被意外拦腰截断）
    for text_node in soup.find_all(string=True):
        if text_node.parent and text_node.parent.name not in ['pre', 'code']:
            cleaned = text_node.replace('\n', ' ').replace('\r', '')
            text_node.replace_with(cleaned)

    # b. 将所有的 <br>, <br/> 替换为换行符
    for br in soup.find_all('br'):
        br.replace_with('\n')

    # c. 把所有的行内标签解包（unwrap），使得文本不被割裂（例如保留 <a> 里的文本且无缝衔接）
    inline_tags = ['span', 'a', 'strong', 'b', 'i', 'em', 'u', 'font', 'sup', 'sub', 'label']
    for tag in soup.find_all(inline_tags):
        tag.unwrap()

    # d. 对于块级元素，在其前后强制插入换行符，确保其内容独立成行
    block_tags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td', 'th', 'table', 'ul', 'ol']
    for tag in soup.find_all(block_tags):
        tag.insert_before(NavigableString('\n'))
        tag.insert_after(NavigableString('\n'))

    # ==========================================
    # 4. 收集所有可能的条目 (基于纯文本行扫描)
    # ==========================================
    article_candidates = defaultdict(list)
    ctx = {"chapter": "", "section": "", "article_num": "", "article_content": []}

    def clean_hierarchy_text(text):
        return re.sub(r'^第[一二三四五六七八九十百千]+[章节编]\s*', '', text).strip()

    def flush_to_candidates():
        if ctx["article_num"] and ctx["article_content"]:
            full_text = "\n".join(ctx["article_content"]).strip()
            if full_text:
                path = [metadata["source"]]
                if ctx["chapter"]: path.append(clean_hierarchy_text(ctx["chapter"]))
                if ctx["section"]: path.append(clean_hierarchy_text(ctx["section"]))

                prefix = "——".join(path)
                entry = {
                    "content": f"{prefix}——{full_text}",
                    "raw_text_len": len(full_text),  # 用于后续长度排序
                    "meta": {
                        **metadata,
                        "chapter": ctx["chapter"],
                        "section": ctx["section"],
                        "articleNumber": ctx["article_num"]
                    }
                }
                article_candidates[ctx["article_num"]].append(entry)
        ctx["article_content"] = []

    # 提取处理过后的全部纯文本，按换行符切割成干净的列表
    raw_text = soup.get_text()
    lines = raw_text.split('\n')

    for line in lines:
        # 去除全角空格和首尾留白
        text = line.replace('\u3000', ' ').strip()
        if not text:
            continue

        # 识别章/节
        if re.match(r'^第[一二三四五六七八九十百千]+章', text):
            flush_to_candidates()
            ctx["chapter"], ctx["section"] = text, ""
            continue
        elif re.match(r'^第[一二三四五六七八九十百千]+节', text):
            flush_to_candidates()
            ctx["section"] = text
            continue

        # 识别条
        article_match = re.match(r'^(第[一二三四五六七八九十百千]+条)\s*(.*)', text)
        if article_match:
            flush_to_candidates()
            ctx["article_num"] = article_match.group(1)
            ctx["article_content"].append(text)
        elif ctx["article_num"]:
            # 处理款项缩进
            if re.match(r'^（[一二三四五六七八九十]+）|^\([0-9]+\)', text):
                ctx["article_content"].append(f"    {text}")
            else:
                ctx["article_content"].append(text)

    flush_to_candidates()

    # ==========================================
    # 5. 去重过滤逻辑 (保留倒数第二长)
    # ==========================================
    final_chunks = []
    index_counter = 0

    for art_num in article_candidates:
        versions = article_candidates[art_num]

        # 对该条目的所有版本按长度从小到大排序
        versions.sort(key=lambda x: x["raw_text_len"])

        # 逻辑：保留倒数第二长
        if len(versions) >= 2:
            selected = versions[-2]
        else:
            selected = versions[-1]

        final_chunks.append({
            "content": selected["content"],
            "metadata": selected["meta"],
            "chunkId": str(index_counter),
            "embedding": []
        })
        index_counter += 1

    return final_chunks