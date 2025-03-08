import config

config = config.config

# 检查存储下载模组文件的路径，如果文件夹大于10个（默认），或文件夹名的时间戳大于30天，则删除
import os
import time

def cleanup_mod_folders():
    download_path = config.DOWNLOAD_PATH
    max_folders = config.MAX_DOWNLOAD_CACHE_FOLDERS
    max_age_days = config.MAX_DOWNLOAD_CACHE_AGE_DAYS

    if not os.path.exists(download_path):
        print(f"下载目录 {download_path} 不存在，跳过清理")
        return

    all_subdirs = [os.path.join(download_path, d) for d in os.listdir(download_path)
                   if os.path.isdir(os.path.join(download_path, d))]

    import re
    timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\+\d{2}-\d{2}-\d{2}\.\d+')
    timestamp_dirs = [d for d in all_subdirs if timestamp_pattern.match(os.path.basename(d))]

    if not timestamp_dirs:
        print("没有符合时间戳格式的模组文件夹需要清理")
        return

    timestamp_dirs.sort(key=lambda x: os.path.getctime(x))

    now = time.time()
    deleted_count = 0

    for folder_path in timestamp_dirs[:]:
        folder_age_days = (now - os.path.getctime(folder_path)) / (60 * 60 * 24)
        if folder_age_days > max_age_days:
            try:
                import shutil
                shutil.rmtree(folder_path)
                print(f"删除过期文件夹 ({folder_age_days:.1f} 天): {os.path.basename(folder_path)}")
                timestamp_dirs.remove(folder_path)
                deleted_count += 1
            except Exception as e:
                print(f"删除文件夹 {folder_path} 失败: {e}")

    while len(timestamp_dirs) > max_folders:
        oldest_folder = timestamp_dirs.pop(0)
        try:
            import shutil
            shutil.rmtree(oldest_folder)
            print(f"删除最旧文件夹: {os.path.basename(oldest_folder)}")
            deleted_count += 1
        except Exception as e:
            print(f"删除文件夹 {oldest_folder} 失败: {e}")

    if deleted_count > 0:
        print(f"共清理 {deleted_count} 个模组文件夹")
    else:
        print("没有需要清理的模组文件夹")



# 执行清理
print("启动程序将会清理下载缓存目录中的过期文件夹，具体过期时间可到config.yaml中修改")
cleanup_mod_folders()

if config.Zmail_enable:
    import ZmailOut
else:
    import Data_updater

config = config.load_config()

if config.Selenium_enable:
    if config.download_enable:
        if not config.Finished_upload:
            print("Selenium 已启用，开始上传")
            import update_to_website
        else:
            print("没有需要上传的文件")
    else:
        raise Exception("You need to set download_enable to True to use Selenium. Check your config file.")

