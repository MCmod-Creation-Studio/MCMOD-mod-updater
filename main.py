#!/usr/bin/env python3
import asyncio
import os
import re
import shutil
import sys
import time
from datetime import datetime


class ModManagerApp:
    def __init__(self):
        # Import configuration at initialization
        import config
        self.config = config.config
        self.logger = self._setup_logger()

    def _setup_logger(self):
        return print

    async def cleanup_mod_folders(self):
        """Clean up old mod folders based on config settings"""
        download_path = self.config.DOWNLOAD_PATH
        max_folders = self.config.MAX_DOWNLOAD_CACHE_FOLDERS
        max_age_days = self.config.MAX_DOWNLOAD_CACHE_AGE_DAYS

        if not os.path.exists(download_path):
            self.logger(f"下载目录 {download_path} 不存在，跳过清理")
            return

        # Get all subdirectories
        all_subdirs = [os.path.join(download_path, d) for d in os.listdir(download_path)
                       if os.path.isdir(os.path.join(download_path, d))]

        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\+\d{2}-\d{2}-\d{2}\.\d+')
        timestamp_dirs = [d for d in all_subdirs if timestamp_pattern.match(os.path.basename(d))]

        if not timestamp_dirs:
            self.logger("没有符合时间戳格式的模组文件夹需要清理")
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
                    self.logger(f"删除过期文件夹 ({folder_age_days:.1f} 天): {os.path.basename(folder_path)}")
                    timestamp_dirs.remove(folder_path)
                    deleted_count += 1
                except Exception as e:
                    self.logger(f"删除文件夹 {folder_path} 失败: {e}")

        # Delete oldest folders if we have more than max_folders
        while len(timestamp_dirs) > max_folders:
            oldest_folder = timestamp_dirs.pop(0)
            try:
                shutil.rmtree(oldest_folder)
                self.logger(f"删除最旧文件夹: {os.path.basename(oldest_folder)}")
                deleted_count += 1
            except Exception as e:
                self.logger(f"删除文件夹 {oldest_folder} 失败: {e}")

        if deleted_count > 0:
            self.logger(f"共清理 {deleted_count} 个模组文件夹")
        else:
            self.logger("没有需要清理的模组文件夹")

    async def update_data(self):
        """Update mod data from APIs"""
        if self.config.Zmail_enable:
            try:
                import ZmailOut
                self.logger("正在通过邮件发送更新通知...")
                # If ZmailOut has an async function, call it with await
                if hasattr(ZmailOut, 'send_mail_async'):
                    await ZmailOut.send_mail_async()
                else:
                    # Run in executor if it's synchronous
                    await asyncio.to_thread(ZmailOut.send_mail)
            except Exception as e:
                self.logger(f"邮件发送失败: {e}")
        else:
            try:
                import data_updater
                self.logger("正在更新模组数据...")
                # If data_updater has an async main function, call it
                if hasattr(data_updater, 'main'):
                    await data_updater.main()
                # Fall back to the latest_upload_async function if it exists
                elif hasattr(data_updater, 'latest_upload_async'):
                    await data_updater.latest_upload_async()
            except Exception as e:
                self.logger(f"更新模组数据失败: {e}")

    async def upload_to_website(self):
        """Upload mods to website if enabled"""
        if not self.config.Selenium_enable:
            return

        if self.config.download_enable:
            if not self.config.Finished_upload:
                self.logger("Selenium 已启用，开始上传")
                try:
                    import update_to_website
                    # If update_to_website has an async main function, call it
                    if hasattr(update_to_website, 'main_async'):
                        await update_to_website.main_async()
                    else:
                        # Run in executor if it's synchronous
                        await asyncio.to_thread(lambda: update_to_website)
                except Exception as e:
                    self.logger(f"上传到网站失败: {e}")
            else:
                self.logger("没有需要上传的文件")
        else:
            raise Exception("You need to set download_enable to True to use Selenium. Check your config file.")

    async def run(self):
        """Main application entry point"""
        self.logger(f"=== 模组管理器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        try:
            # Step 1: Clean up old mod folders
            self.logger("启动程序将会清理下载缓存目录中的过期文件夹，具体过期时间可到config.yaml中修改")
            await self.cleanup_mod_folders()

            # Step 2: Update configuration
            self.config.load_config()

            # Step 3: Update mod data
            await self.update_data()

            # Step 4: Upload to website if enabled
            await self.upload_to_website()

            self.logger(f"=== 操作完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            return 0
        except Exception as e:
            self.logger(f"程序执行出错: {e}")
            return 1


# Application entry point
def main():
    app = ModManagerApp()
    return asyncio.run(app.run())


if __name__ == "__main__":
    sys.exit(main())