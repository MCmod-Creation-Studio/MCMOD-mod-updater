import os.path
from datetime import datetime
import config

config = config.Config()
Enabled = config.LOG_ENABLED
log = ""
log_path = os.path.join(config.LOG_PATH, 'latest.log') if config.LOG_ENABLED else None

def toLog(message):
    """Simple logging function to print messages."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    if Enabled:
        global log
        log += f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
        # Save log
        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(log)

def submit_log(process_time):
    # 将latest.log重命名为{process_time}.log
    if not Enabled:
        return
    new_log_path = os.path.join(config.LOG_PATH, f"{process_time}.log")
    os.rename(log_path, new_log_path)
    toLog(f"完整日志已作为 {new_log_path} 备份保存")