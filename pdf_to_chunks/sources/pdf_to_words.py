import fitz  # 导入 PyMuPDF 库


def pdf_to_text(pdf_path, txt_path):
    """
    将 PDF 文件转换为纯文本 TXT 文件

    :param pdf_path: 输入的 PDF 文件路径
    :param txt_path: 输出的 TXT 文件路径
    """
    try:
        # 打开 PDF 文件
        pdf_document = fitz.open(pdf_path)

        # 使用 utf-8 编码打开或创建目标 txt 文件
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            # 遍历 PDF 中的每一页
            for page_num in range(len(pdf_document)):
                # 加载当前页
                page = pdf_document.load_page(page_num)
                # 提取当前页的文本
                text = page.get_text()

                # 将提取的文本写入文件
                txt_file.write(text)
                # 在每一页结束时添加分隔符或换行，方便阅读（可选）
                txt_file.write("\n\n--- 第 {} 页结束 ---\n\n".format(page_num + 1))

        print(f"✅ 成功将 '{pdf_path}' 转换为 '{txt_path}'")

    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 '{pdf_path}'，请检查路径是否正确。")
    except Exception as e:
        print(f"❌ 转换过程中发生错误：{e}")
    finally:
        # 确保在处理完成后关闭 PDF 文档释放内存
        if 'pdf_document' in locals():
            pdf_document.close()


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 将这里的路径替换为你自己的文件路径
    input_pdf = r"C:\Users\Administrator\PycharmProjects\FinalHomeWork\pdf_to_chunks\sources\网络安全技术_生成式人工智能数据标注安全规范.pdf"
    output_txt = r"C:\Users\Administrator\PycharmProjects\FinalHomeWork\pdf_to_chunks\sources\网络安全技术_生成式人工智能数据标注安全规范.txt"

    pdf_to_text(input_pdf, output_txt)