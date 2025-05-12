import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinterdnd2 import DND_FILES, TkinterDnD

class FileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能文件清理工具")
        self.root.geometry("800x600")
        
        # 设置主题颜色
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        
        self.create_widgets()
        self.delete_thread = None
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件夹选择部分
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="文件夹路径:").pack(side=tk.LEFT)
        self.folder_entry = tk.Entry(folder_frame)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 设置拖放
        self.folder_entry.drop_target_register(DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.handle_drop)
        ttk.Button(folder_frame, text="浏览", command=self.browse_folder).pack(side=tk.LEFT)
        
        # 预设文件类型
        preset_frame = ttk.LabelFrame(main_frame, text="预设文件类型", padding="5")
        preset_frame.pack(fill=tk.X, pady=5)
        
        self.lrc_var = tk.BooleanVar(value=True)
        self.txt_var = tk.BooleanVar()
        self.log_var = tk.BooleanVar()
        self.tmp_var = tk.BooleanVar()
        
        ttk.Checkbutton(preset_frame, text=".lrc", variable=self.lrc_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(preset_frame, text=".txt", variable=self.txt_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(preset_frame, text=".log", variable=self.log_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(preset_frame, text=".tmp", variable=self.tmp_var).pack(side=tk.LEFT, padx=5)
        
        # 自定义类型
        custom_frame = ttk.LabelFrame(main_frame, text="自定义类型", padding="5")
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="扩展名（逗号分隔）:").pack(side=tk.LEFT)
        self.custom_entry = ttk.Entry(custom_frame)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 按钮和进度条
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.delete_button = ttk.Button(button_frame, text="开始删除", command=self.start_delete)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
    def handle_drop(self, event):
        # 处理拖放的文件或文件夹
        path = event.data
        # 移除可能的引号和大括号
        path = path.strip('{}').strip('"')
        if os.path.exists(path):
            if os.path.isfile(path):
                path = os.path.dirname(path)
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
            
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def delete_files(self, folder_path, exts):
        self.log_message(f"开始处理文件夹：{folder_path}")
        count = 0
        errors = []
        
        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in exts:
                        try:
                            os.remove(file_path)
                            self.log_message(f"已删除：{filename}")
                            count += 1
                        except Exception as e:
                            errors.append(f"删除失败：{filename} - {str(e)}")
            
            self.log_message(f"操作完成，共删除 {count} 个文件")
            if errors:
                self.log_message("以下文件删除失败：")
                for error in errors:
                    self.log_message(error)
        except Exception as e:
            self.log_message(f"发生错误：{str(e)}")
        finally:
            self.root.after(0, self.delete_completed)
            
    def delete_completed(self):
        self.delete_button.config(state=tk.NORMAL)
        self.progress.stop()
        self.progress.pack_forget()
        
    def start_delete(self):
        folder_path = self.folder_entry.get()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "请先选择有效的文件夹路径!")
            return
            
        # 收集所有扩展名
        exts = []
        # 预设类型
        if self.lrc_var.get():
            exts.append('.lrc')
        if self.txt_var.get():
            exts.append('.txt')
        if self.log_var.get():
            exts.append('.log')
        if self.tmp_var.get():
            exts.append('.tmp')
        
        # 自定义类型
        custom_exts = [e.strip().lower() for e in self.custom_entry.get().split(',') if e.strip()]
        for ext in custom_exts:
            if not ext.startswith('.'):
                ext = '.' + ext
            if ext not in exts:
                exts.append(ext)
        
        if not exts:
            messagebox.showerror("错误", "请至少选择一种文件类型!")
            return
        
        # 启动删除线程
        self.delete_button.config(state=tk.DISABLED)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.progress.start()
        
        self.delete_thread = threading.Thread(
            target=self.delete_files,
            args=(folder_path, exts),
            daemon=True
        )
        self.delete_thread.start()

def main():
    root = TkinterDnD.Tk()
    app = FileCleanerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()