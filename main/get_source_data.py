import os
import json
from typing import List, Dict, Any

# 导入你已经写好的 embedding 方法
from main.api.get_embedding import get_embedding


def process_chunks_and_embed(folder_path: str) -> List[Dict[str, Any]]:
    """
    读取指定文件夹下的所有 txt 文档，合并为 List[dict]，并调用 embedding 接口填充数据。
    """
    merged_data: List[Dict[str, Any]] = []

    # ==========================================
    # 第一步：遍历文件夹，将所有 txt 中的 json 合并为 List[dict]
    # ==========================================
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return merged_data

    # 遍历目标文件夹下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            # 按行读取 txt 文件 (JSON Lines 格式)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue  # 跳过空行

                    try:
                        # 解析 JSON 并追加到列表中
                        json_obj = json.loads(line)
                        merged_data.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"解析 JSON 失败 | 文件: {filename} | 错误: {e}")

    print(f"文件读取完成，共收集到 {len(merged_data)} 条 Chunk 数据。")

    # ==========================================
    # 第二步：遍历 List[dict]，调用 get_embedding 替换 embedding 内容
    # ==========================================
    print("开始调用 Embedding 模型处理数据...")
    for item in merged_data:
        content = item.get("content", "")
        if content:
            # 调用你的方法获取向量
            vector = get_embedding(
                text=content,
                model="text-embedding-v3",
                dimensions=1024,
                encoding_format="float"
            )
            # 替换原本为空的 embedding 列表
            item["embedding"] = vector

    print("所有数据的 Embedding 替换完成！")

    return merged_data


if __name__ == "__main__":
    # 定义你的目标文件夹路径 (使用 raw string 'r' 避免 Windows 路径转义问题)
    target_folder = r"C:\Users\Administrator\PycharmProjects\FinalHomeWork\part_chunks_source"

    # 执行主处理函数
    final_data_list = process_chunks_and_embed(target_folder)

    # ==========================================
    # 补充：通常处理完你需要把结果保存下来，如果需要可以取消下方注释
    # ==========================================
    output_path = r"C:\Users\Administrator\PycharmProjects\FinalHomeWork\processed_chunks.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data_list, f, ensure_ascii=False, indent=4)
    print(f"最终结果已保存至: {output_path}")