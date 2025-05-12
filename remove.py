import os
import threading
import PySimpleGUI as sg

sg.theme('DarkBlue3')

def log_message(window, message):
    window.write_event_value('-LOG-', message)

def delete_files(folder_path, exts, window):
    log_message(window, f"开始处理文件夹：{folder_path}")
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
                        log_message(window, f"已删除：{filename}")
                        count += 1
                    except Exception as e:
                        errors.append(f"删除失败：{filename} - {str(e)}")
        
        log_message(window, f"操作完成，共删除 {count} 个文件")
        if errors:
            log_message(window, "以下文件删除失败：")
            for error in errors:
                log_message(window, error)
    except Exception as e:
        log_message(window, f"发生错误：{str(e)}")

def process_dropped_path(path):
    if os.path.isfile(path):
        return os.path.dirname(path)
    elif os.path.isdir(path):
        return path
    return None

layout = [
    [sg.Text('文件夹路径:', size=(12,1)), 
     sg.Input(key='-FOLDER-', enable_events=True, expand_x=True, tooltip='拖放文件夹到这里'),
     sg.FolderBrowse()],
    
    [sg.Frame('预设文件类型', [
        [sg.Checkbox('.lrc', default=True, key='-LRC-'),
         sg.Checkbox('.txt', key='-TXT-'),
         sg.Checkbox('.log', key='-LOG-'),
         sg.Checkbox('.tmp', key='-TMP-')]
    ])],
    
    [sg.Frame('自定义类型', [
        [sg.Text('扩展名（逗号分隔）:', size=(15,1)),
         sg.Input(key='-CUSTOM-', tooltip='例如: .bak, .old', expand_x=True)]
    ])],
    
    [sg.Button('开始删除', key='-DELETE-'), 
     sg.ProgressBar(100, orientation='h', size=(20,20), key='-PROGRESS-', visible=False),
     sg.Push(), 
     sg.Button('退出')],
    
    [sg.Multiline('', key='-LOG-', size=(70, 15), autoscroll=True, 
                 disabled=True, write_only=True, expand_x=True, expand_y=True)]
]

window = sg.Window('智能文件清理工具', layout, resizable=True, finalize=True)

def main():
    delete_thread = None
    while True:
        event, values = window.read()
        
        if event in (sg.WINDOW_CLOSED, '退出'):
            break
        
        # 处理拖放事件
        elif event == '-FOLDER-':
            paths = values['-FOLDER-'].split(';')
            valid_path = None
            for path in paths:
                cleaned_path = path.strip().replace('"', '')
                if os.path.exists(cleaned_path):
                    valid_path = process_dropped_path(cleaned_path)
                    break
            if valid_path:
                window['-FOLDER-'].update(valid_path)
        
        # 处理删除操作
        elif event == '-DELETE-':
            folder_path = values['-FOLDER-']
            if not folder_path or not os.path.isdir(folder_path):
                sg.popup_error('请先选择有效的文件夹路径!')
                continue
                
            # 收集所有扩展名
            exts = []
            # 预设类型
            for ext in ['-LRC-', '-TXT-', '-LOG-', '-TMP-']:
                if values[ext]:
                    exts.append(ext[1:-1].lower())
            
            # 自定义类型
            custom_exts = [e.strip().lower() for e in values['-CUSTOM-'].split(',') if e.strip()]
            for ext in custom_exts:
                if not ext.startswith('.'):
                    ext = '.' + ext
                if ext not in exts:
                    exts.append(ext)
            
            if not exts:
                sg.popup_error('请至少选择一种文件类型!')
                continue
            
            # 启动删除线程
            window['-DELETE-'].update(disabled=True)
            window['-PROGRESS-'].update(visible=True)
            delete_thread = threading.Thread(
                target=delete_files, 
                args=(folder_path, exts, window),
                daemon=True
            )
            delete_thread.start()
        
        # 更新日志
        elif event == '-LOG-':
            window['-LOG-'].update(values[event] + '\n', append=True)
        
        # 重置界面
        elif event == '-DONE-':
            window['-DELETE-'].update(disabled=False)
            window['-PROGRESS-'].update(visible=False)

    window.close()

if __name__ == '__main__':
    main()