import os

def delete_lrc_files(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 '{folder_path}' 不存在。")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否以 .lrc 结尾
        if filename.endswith(".lrc"):
            file_path = os.path.join(folder_path, filename)
            try:
                # 删除文件
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    # 指定要删除 .lrc 文件的文件夹路径
    folder_path = "E:\iphone\其他"

    # 调用函数删除 .lrc 文件
    delete_lrc_files(folder_path)