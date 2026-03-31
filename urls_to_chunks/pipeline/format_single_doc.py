from bs4 import BeautifulSoup
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
    # 3. 收集所有可能的条目 (解决重复的核心：暂存)
    # ==========================================
    # 使用字典存储：{ "第一条": [版本1, 版本2, ...] }
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

    # 线性扫描
    all_elements = soup.find_all(['p', 'div'], recursive=True)
    for p in all_elements:
        # 严格防重：如果当前节点内部还有 p 或 div，跳过，只取最底层含文字的节点
        if p.find(['p', 'div']):
            continue

        text = p.get_text(" ", strip=True).replace('\u3000', ' ')
        if not text: continue

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
    # 4. 去重过滤逻辑 (倒数第二长)
    # ==========================================
    final_chunks = []
    # 按照法条出现的顺序排序（第一条, 第二条...）
    # 注意：这里假设条目是按顺序解析出来的
    sorted_article_keys = sorted(article_candidates.keys(), key=lambda x: len(x))  # 简单排序，如果需要严格数字序需转换

    index_counter = 0
    for art_num in article_candidates:
        versions = article_candidates[art_num]

        # 对该条目的所有版本按长度从小到大排序
        versions.sort(key=lambda x: x["raw_text_len"])

        # 逻辑：保留倒数第二长
        # 如果只有1个版本，就选这一个；如果有多个，选 index = -2
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