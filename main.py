#!/usr/bin/env python3
import os
import re
import shutil
import time
from datetime import datetime


class ModManagerApp:
    def __init__(self):
        # Import configuration at initialization
        import config
        from toLog import toLog
        self.config = config.Config()
        self.logging = toLog

    async def cleanup_mod_folders(self):
        """Clean up old mod folders based on config settings"""
        download_path = self.config.DOWNLOAD_PATH
        max_folders = self.config.MAX_DOWNLOAD_CACHE_FOLDERS
        max_age_days = self.config.MAX_DOWNLOAD_CACHE_AGE_DAYS

        if not os.path.exists(download_path):
            self.logging(f"下载目录 {download_path} 不存在，跳过清理")
            return

        # Get all subdirectories
        all_subdirs = [os.path.join(download_path, d) for d in os.listdir(download_path)
                       if os.path.isdir(os.path.join(download_path, d))]

        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\+\d{2}-\d{2}-\d{2}\.\d+')
        timestamp_dirs = [d for d in all_subdirs if timestamp_pattern.match(os.path.basename(d))]

        if not timestamp_dirs:
            self.logging("没有符合时间戳格式的模组文件夹需要清理")
            return

        timestamp_dirs.sort(key=lambda x: os.path.getctime(x))

        now = time.time()
        deleted_count = 0

        # Delete folders older than max_age_days
        for folder_path in timestamp_dirs[:]:
            folder_age_days = (now - os.path.getctime(folder_path)) / (60 * 60 * 24)
            if folder_age_days > max_age_days:
                try:
                    shutil.rmtree(folder_path)
                    self.logging(f"删除过期文件夹 ({folder_age_days:.1f} 天): {os.path.basename(folder_path)}")
                    timestamp_dirs.remove(folder_path)
                    deleted_count += 1
                except Exception as e:
                    self.logging(f"删除文件夹 {folder_path} 失败: {e}")

        # Delete the oldest folders if we have more than max_folders
        while len(timestamp_dirs) > max_folders:
            oldest_folder = timestamp_dirs.pop(0)
            try:
                shutil.rmtree(oldest_folder)
                self.logging(f"删除最旧文件夹: {os.path.basename(oldest_folder)}")
                deleted_count += 1
            except Exception as e:
                self.logging(f"删除文件夹 {oldest_folder} 失败: {e}")

        if deleted_count > 0:
            self.logging(f"共清理 {deleted_count} 个模组文件夹")
        else:
            self.logging("没有需要清理的模组文件夹")

    async def cleanup_old_logs(self):
        """Clean up old log files based on config settings"""
        log_path = self.config.LOG_PATH
        max_log_files = self.config.MAX_LOG_FILES
        max_log_age_days = self.config.MAX_LOG_AGE_DAYS

        if not os.path.exists(log_path):
            self.logging(f"日志目录 {log_path} 不存在，跳过清理")
            return

        all_logs = [os.path.join(log_path, f) for f in os.listdir(log_path)
                    if os.path.isfile(os.path.join(log_path, f)) and f.endswith('.log')]

        now = time.time()
        deleted_count = 0

        # Delete logs older than max_log_age_days
        for log_file in all_logs[:]:
            log_age_days = (now - os.path.getctime(log_file)) / (60 * 60 * 24)
            if log_age_days > max_log_age_days:
                try:
                    os.remove(log_file)
                    self.logging(f"删除过期日志文件: {os.path.basename(log_file)} ({log_age_days:.1f} 天)")
                    all_logs.remove(log_file)
                    deleted_count += 1
                except Exception as e:
                    self.logging(f"删除日志文件 {log_file} 失败: {e}")

        # Delete oldest logs if we have more than max_log_files
        while len(all_logs) > max_log_files:
            oldest_log = min(all_logs, key=os.path.getctime)
            try:
                os.remove(oldest_log)
                self.logging(f"删除最旧日志文件: {os.path.basename(oldest_log)}")
                all_logs.remove(oldest_log)
                deleted_count += 1
            except Exception as e:
                self.logging(f"删除日志文件 {oldest_log} 失败: {e}")

        if deleted_count > 0:
            self.logging(f"共清理 {deleted_count} 个日志文件")
        else:
            self.logging("没有需要清理的日志文件")

    async def update_data(self):
        """Update mod data from APIs"""
        if self.config.Zmail_enable:
            try:
                import ZmailOut
                self.logging("正在通过邮件发送更新通知...")
                # If ZmailOut has an async function, call it with await
                if hasattr(ZmailOut, 'send_mail_async'):
                    await ZmailOut.send_mail_async()
                else:
                    # Run in executor if it's synchronous
                    await asyncio.to_thread(ZmailOut.send_mail)
            except Exception as e:
                self.logging(f"邮件发送失败: {e}")
        else:
            try:
                import data_updater
                self.logging("正在更新模组数据...")
                # If data_updater has an async main function, call it
                if hasattr(data_updater, 'main'):
                    await data_updater.main()
                # Fall back to the latest_upload_async function if it exists
                elif hasattr(data_updater, 'latest_upload_async'):
                    await data_updater.latest_upload_async()
            except Exception as e:
                self.logging(f"更新模组数据失败: {e}")

    async def upload_to_website(self):
        """Upload mods to website if enabled"""
        if not self.config.Selenium_enable:
            return

        if self.config.download_enable:
            if not self.config.Finished_upload:
                self.logging("Selenium 已启用，开始上传")
                try:
                    import update_to_website
                    # If update_to_website has an async main function, call it
                    if hasattr(update_to_website, 'main_async'):
                        await update_to_website.main_async()
                    else:
                        # Run in executor if it's synchronous
                        await asyncio.to_thread(lambda: update_to_website)
                except Exception as e:
                    self.logging(f"上传到网站失败: {e}")
            else:
                self.logging("没有需要上传的文件")
        else:
            raise Exception("You need to set download_enable to True to use Selenium. Check your config file.")

    async def run(self):
        """Main application entry point"""
        self.logging(f"=== MC百科文件上传懒人助手 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        try:
            # Step 1: Clean up old mod folders
            self.logging("启动程序将会清理下载缓存目录中的过期文件夹，具体过期时间可到config.yaml中修改")
            await self.cleanup_mod_folders()
            await self.cleanup_old_logs()

            # Step 2: Update configuration
            self.config.load_config()

            # Step 3: Update mod data
            await self.update_data()

            # Step 4: Upload to website if enabled
            await self.upload_to_website()

            self.logging(f"=== 操作完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            return 0
        except Exception as e:
            self.logging(f"程序执行出错: {e}")
            return 1


# Application entry point
import asyncio
import sys


def main():
    # Fix Windows-specific asyncio issues
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Your main code here
        loop.run_until_complete(ModManagerApp().run())
    finally:
        # Ensure proper cleanup of all resources
        try:
            # Cancel all pending tasks
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()

            # Wait for all tasks to be cancelled
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

            # Properly close the event loop
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    sys.exit(main())