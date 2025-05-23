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
        self.root.geometry("900x700")
        
        # 设置字体
        self.title_font = ("Microsoft YaHei UI", 16, "bold")
        self.header_font = ("Microsoft YaHei UI", 11)
        self.normal_font = ("Microsoft YaHei UI", 10)
        self.small_font = ("Microsoft YaHei UI", 9)
        self.mono_font = ("Microsoft YaHei UI", 10)
        
        # 设置主题颜色
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=self.normal_font)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=self.normal_font)
        self.style.configure("DropFrame.TFrame", background="#e3f2fd", relief="solid", borderwidth=2)
        self.style.configure("TLabelframe.Label", font=self.header_font)
        
        # 自定义按钮样式
        self.style.configure("Type.TButton", 
                           padding=10,
                           relief="flat",
                           background="#e0e0e0",
                           foreground="black")
        self.style.map("Type.TButton",
                      background=[("active", "#2196F3"), ("pressed", "#1976D2")],
                      foreground=[("active", "white"), ("pressed", "white")])
        
        self.create_widgets()
        self.delete_thread = None
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="智能文件清理工具", font=self.title_font)
        title_label.pack(pady=(0, 20))
        
        # 文件夹选择部分
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(folder_frame, text="文件夹路径:", font=self.header_font).pack(side=tk.LEFT)
        
        # 拖放区域
        self.drop_frame = ttk.Frame(folder_frame, style="DropFrame.TFrame")
        self.drop_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.folder_entry = tk.Entry(self.drop_frame, font=self.normal_font)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.folder_entry.drop_target_register(DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.handle_drop)
        
        # 拖放提示标签
        self.drop_label = ttk.Label(self.drop_frame, 
                                  text="将文件或文件夹拖放到这里",
                                  font=self.small_font,
                                  foreground="gray")
        self.drop_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(folder_frame, text="浏览", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        # 文件类型选择部分
        type_frame = ttk.LabelFrame(main_frame, text="文件类型选择", padding="10")
        type_frame.pack(fill=tk.X, pady=10)
        
        # 预设类型按钮
        preset_frame = ttk.Frame(type_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_frame, text="预设类型:", font=self.header_font).pack(side=tk.LEFT, padx=5)
        
        self.type_buttons = {}
        for ext, text in [('.lrc', '.lrc'), ('.txt', '.txt'), 
                         ('.log', '.log'), ('.tmp', '.tmp')]:
            btn = tk.Button(preset_frame, text=text,
                          command=lambda e=ext: self.toggle_type(e),
                          bg="#e0e0e0",
                          activebackground="#2196F3",
                          activeforeground="white",
                          relief="flat",
                          padx=10,
                          pady=5,
                          font=self.normal_font)
            btn.pack(side=tk.LEFT, padx=5)
            self.type_buttons[ext] = btn
        
        # 默认选中 .lrc
        self.selected_types = {'.lrc'}
        self.type_buttons['.lrc'].configure(bg="#2196F3", fg="white")
        
        # 自定义类型
        custom_frame = ttk.Frame(type_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="自定义类型:", font=self.header_font).pack(side=tk.LEFT, padx=5)
        self.custom_entry = ttk.Entry(custom_frame, font=self.normal_font)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(custom_frame, text="(用逗号分隔，例如: .bak, .old)", 
                 font=self.small_font, foreground="gray").pack(side=tk.LEFT)
        
        # 模式选择
        mode_frame = ttk.Frame(type_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        self.recursive_mode = tk.BooleanVar(value=False)
        self.recursive_check = ttk.Checkbutton(mode_frame, 
                                             text="多层文件夹模式（包含子文件夹）",
                                             variable=self.recursive_mode,
                                             style="TCheckbutton")
        self.recursive_check.pack(side=tk.LEFT, padx=5)
        
        # 操作按钮和进度条
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.delete_button = ttk.Button(button_frame, text="开始删除", 
                                      command=self.start_delete,
                                      style="TButton")
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = ScrolledText(log_frame, height=15, wrap=tk.WORD,
                                   font=self.mono_font)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
    def toggle_type(self, ext):
        if ext in self.selected_types:
            self.selected_types.remove(ext)
            self.type_buttons[ext].configure(bg="#e0e0e0", fg="black")
        else:
            self.selected_types.add(ext)
            self.type_buttons[ext].configure(bg="#2196F3", fg="white")
        
    def handle_drop(self, event):
        path = event.data
        path = path.strip('{}').strip('"')
        if os.path.exists(path):
            if os.path.isfile(path):
                path = os.path.dirname(path)
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.drop_label.configure(text="已选择文件夹")
            
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
            self.drop_label.configure(text="已选择文件夹")
            
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
            if self.recursive_mode.get():
                # 多层文件夹模式
                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext in exts:
                            try:
                                os.remove(file_path)
                                self.log_message(f"已删除：{os.path.relpath(file_path, folder_path)}")
                                count += 1
                            except Exception as e:
                                errors.append(f"删除失败：{os.path.relpath(file_path, folder_path)} - {str(e)}")
            else:
                # 单层文件夹模式
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
        exts = list(self.selected_types)
        
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