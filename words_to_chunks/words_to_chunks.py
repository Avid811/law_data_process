import os
import re
import json


def parse_txt_to_chunks(filepath, custom_status="", custom_whoMake="", custom_lawType=""):
    # ==========================================
    # 0. 读取文件
    # ==========================================
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # 兼容不同编码格式的TXT文件
        with open(filepath, 'r', encoding='gbk') as f:
            lines = f.readlines()

    # ==========================================
    # 1. 提取 source (去除开头的空行，取第一行非空文本)
    # ==========================================
    while lines and not lines[0].strip():
        lines.pop(0)

    if lines:
        source_name = lines.pop(0).strip()  # 取出第一行并从源数据中移除，不再参与切分
    else:
        # Fallback 兜底方案
        filename = os.path.basename(filepath)
        source_name = os.path.splitext(filename)[0]

    # ==========================================
    # 2. 提取 takeEffect (施行日期/公布日期/发布日期)
    # ==========================================
    full_text = "\n".join(lines)
    take_effect = ""
    # 匹配“施行/公布/发布日期”，兼容冒号空格，以及 "YYYY年MM月DD日", "YYYY-MM-DD", "YYYY.MM.DD" 等日期格式
    date_pattern = r'(?:施行|公布|发布)日期\s*[:：]?\s*([0-9]{4}[年\-\.][0-9]{1,2}[月\-\.][0-9]{1,2}日?)'
    match = re.search(date_pattern, full_text)
    if match:
        take_effect = match.group(1)

    # ==========================================
    # 3. 初始化元数据结构
    # ==========================================
    metadata_base = {
        "source": source_name,
        "takeEffect": take_effect,
        "lawType": custom_lawType,
        "whoMake": custom_whoMake,
        "status": custom_status,
        "chapter": "",
        "section": "",
        "articleNumber": ""
    }

    final_chunks = []
    chunk_index = 0

    def add_chunk(content, meta):
        nonlocal chunk_index
        final_chunks.append({
            "content": content,
            "metadata": meta,
            "chunkId": str(chunk_index),
            "embedding": []
        })
        chunk_index += 1

    # ==========================================
    # 4. 递归切分策略定义 (普通文档)
    # ==========================================
    # 使用正则表达式的“正向前瞻断言 (?=...)”，确保切分时标题自身不会被删去
    REGEXES = [
        r'(?m)^(?=[一二三四五六七八九十]+、)',  # Level 0: 大标题
        r'(?m)^(?=（[一二三四五六七八九十]+）)',  # Level 1: 中标题
        r'(?m)^(?=\d+\.)'  # Level 2: 小标题
    ]

    def recursive_split_block(text, level, meta):
        if not text.strip():
            return []

        # 边界控制：如果当前切分块字数 < 200，或者已经用尽了所有级别的标题，则直接成 chunk
        if len(text) < 200 or level >= len(REGEXES):
            return [{"content": f"{text.strip()}", "metadata": meta.copy()}]

        pattern = REGEXES[level]
        parts = re.split(pattern, text)
        parts = [p.strip() for p in parts if p.strip()]

        # 当前级别没有切分开（找不到该级别的标题），进入下一级标题尝试
        if len(parts) <= 1:
            return recursive_split_block(text, level + 1, meta)

        # 发生了切分，遍历子块进行长度判断
        chunks = []
        for part in parts:
            if len(part) < 200:
                # 按照当前标题切分后，若该块 size < 200，则直接成chunk不再下探
                chunks.append({"content": f"{source_name}——{part.strip()}", "metadata": meta.copy()})
            else:
                # 否则继续进入下一级标题切分
                chunks.extend(recursive_split_block(part, level + 1, meta))

        return chunks

    # ==========================================
    # 5. 解析文本，区分表格行和普通段落
    # ==========================================
    table_started = False
    text_buffer = []

    def flush_text_buffer():
        nonlocal text_buffer
        if text_buffer:
            text = "\n".join(text_buffer)
            # 文本累积完后触发递归切分
            chunks = recursive_split_block(text, level=0, meta=metadata_base)
            for c in chunks:
                add_chunk(c["content"], c["metadata"])
            text_buffer = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # 检测到表格开始标识
        if "算法专项治理清单指引" in line:
            flush_text_buffer()  # 清空上方普通文本
            table_started = True
            add_chunk(f"{source_name}——{line}", metadata_base.copy())
            continue

        if table_started:
            # 判断是否是表格头或表格数据行
            if line.startswith("序号") or "核验项目" in line or re.match(r'^\d+\s+', line):
                add_chunk(f"{source_name}——算法专项治理清单指引——{line}", metadata_base.copy())
            else:
                # 校验：如果不像表格数据，判断是否属于正文段落(以大标题或中标题开头)来退出表格模式
                if re.match(r'^[一二三四五六七八九十]+、', line) or line.startswith("（一）"):
                    table_started = False
                    text_buffer.append(line)
                else:
                    add_chunk(f"{source_name}——算法专项治理清单指引——{line}", metadata_base.copy())
        else:
            text_buffer.append(line)

    # 循环结束后处理剩余缓冲
    flush_text_buffer()

    return final_chunks


# ==========================================
# 执行入口
# ==========================================
if __name__ == "__main__":
    # 配置目标文件路径
    file_path = r"C:\Users\Administrator\PycharmProjects\FinalHomeWork\words_to_chunks\《关于开展“清朗·网络平台算法典型问题治理”专项行动的通知》.txt"

    if not os.path.exists(file_path):
        print(f"找不到指定文件：{file_path}，请检查路径是否正确。")
    else:
        print("====== 元数据录入（直接回车可置空） ======")
        user_status = input("请输入 status (例如：现行有效): ").strip()
        user_whoMake = input("请输入 whoMake (例如：国家互联网信息办公室): ").strip()
        user_lawType = input("请输入 lawType (例如：规范性文件): ").strip()
        print("==========================================\n")

        print("正在处理切分...")
        # 执行切分，将用户输入作为参数传入
        result_chunks = parse_txt_to_chunks(
            filepath=file_path,
            custom_status=user_status,
            custom_whoMake=user_whoMake,
            custom_lawType=user_lawType
        )

        # 输出并保存为按行分隔的 JSON 对象 (JSON Lines 格式) txt 文件
        output_file = "chunks_result.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for chunk in result_chunks:
                # 使用 json.dumps 将单个字典序列化为单行字符串，不包含换行符或缩进
                json_line = json.dumps(chunk, ensure_ascii=False)
                f.write(json_line + "\n")

        print(f"切分成功！共生成 {len(result_chunks)} 个 Chunks。")
        print(f"提取到的 Source: {result_chunks[0]['metadata']['source'] if result_chunks else '未知'}")
        print(f"提取到的 TakeEffect: {result_chunks[0]['metadata']['takeEffect'] if result_chunks else '未找到'}")
        print(f"切分结果已按行保存至：{os.path.abspath(output_file)}")