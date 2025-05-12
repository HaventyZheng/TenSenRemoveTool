import os

def delete_lrc_files(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在。")
        return

    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # 检查文件是否以 .lrc 结尾
            if filename.endswith(".lrc"):
                file_path = os.path.join(root, filename)
                try:
                    # 删除文件
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    # 指定要删除 .lrc 文件的文件夹路径
    folder_path = "E:\Music\KwDownload\song\Iphone\陶喆"

    # 调用函数删除 .lrc 文件
    delete_lrc_files(folder_path)