import yaml
import os

class Config:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.load_config()

    def create_default_config(self):
        default_config = """
# Configuration for Mcmod_mod_updater
# Mcmod_mod_updater程序的配置文件

# API token for authentication
# you can get your token from https://console.curseforge.com/?#/api-keys
# 你可以从https://console.curseforge.com/?#/api-keys获取你的token
CURSEFORGE_API_KEY: 

# File paths
# Path to the Excel database file that contains mod information, which is provided by MCMOD Website owner
# 包含模组信息的Excel数据库文件的路径，由MCMOD网站所有者提供
DATABASE_PATH: ./Database.xlsx

# Download setting
# If you want to download the mod files, set DOWNLOAD_ON to True
# 如果你想该程序下载Mod文件，请将DOWNLOAD_ON设置为True
download_enable: True
headers : {
    'Referer': '',
    'If-None-Match': '"LMyW4mgAfp2S0ragPuZKjIpMkas="',
    'If-Modified-Since': 'Wed, 25 Oct 2020 09:37:56 GMT',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
}
DOWNLOAD_PATH: ./Mods
TIMEOUT_RETRY: 5

# Selenium configuration
# If you want to use Selenium to upload new mod files to MCMOD, set Selenium_enable to True
# 如果你想使用Selenium上传新的Mod文件到MCMOD，你需要将Selenium_enable设置为True
# You need to set download_enable to True to use Selenium
# 你需要将上方的download_enable设置为True才能使用Selenium
Selenium_enable: False

# Zmail configuration
# Zmail is a simple email sending tool, you can use it to send mod update notifications to your email
# if Zmail_enable is False, Zmail will not be used
# Zmail是一个简单的邮件发送工具，你可以使用它将Mod更新通知发送到你的邮箱
# 如果Zmail_enable为False，Zmail将不会被使用
Zmail_enable: False

ZMAIL_HOST: smtp.example.com
ZMAIL_PORT: 
ZMAIL_SSL: True
ZMAIL_USERNAME: your_username
ZMAIL_PASSWORD: your_password
ZMAIL_TO: to_an_email_address


"""
        with open(self.config_file, 'w', encoding='utf-8') as file:
            file.write(default_config)

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")

        with open(self.config_file, 'r', encoding='utf-8') as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing configuration file: {e}")

            self.CURSEFORGE_API_KEY = config.get('CURSEFORGE_API_KEY', None)
            self.DATABASE_PATH = config.get('DATABASE_PATH', None)
            self.download_enable = config.get('download_enable', False)
            self.headers = config.get('headers', {
    'Referer': '',
    'If-None-Match': '"LMyW4mgAfp2S0ragPuZKjIpMkas="',
    'If-Modified-Since': 'Wed, 25 Oct 2020 09:37:56 GMT',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
})
            self.TIMEOUT_RETRY = config.get('TIMEOUT_RETRY', 5)
            self.DOWNLOAD_PATH = config.get('DOWNLOAD_PATH', None)
            self.Selenium_enable = config.get('Selenium_enable', False)
            self.Zmail_enable = config.get('Zmail_enable', False)
            self.ZMAIL_HOST = config.get('ZMAIL_HOST', None)
            self.ZMAIL_PORT = config.get('ZMAIL_PORT', None)
            self.ZMAIL_SSL = config.get('ZMAIL_SSL', True)
            self.ZMAIL_USERNAME = config.get('ZMAIL_USERNAME', None)
            self.ZMAIL_PASSWORD = config.get('ZMAIL_PASSWORD', None)
            self.ZMAIL_TO = config.get('ZMAIL_TO', None)

            # 检查是否为空
            if not self.CURSEFORGE_API_KEY:
                raise ValueError("CURSEFORGE_API_KEY is not set.")
            if not self.DATABASE_PATH:
                raise ValueError("DATABASE_PATH is not set.")
            if self.download_enable:
                if not self.DOWNLOAD_PATH:
                    raise ValueError("DOWNLOAD_PATH is not set.")
            if self.Zmail_enable:
                if not self.ZMAIL_USERNAME:
                    raise ValueError("ZMAIL_USERNAME is not set.")
                if not self.ZMAIL_PASSWORD:
                    raise ValueError("ZMAIL_PASSWORD is not set.")
                if not self.ZMAIL_TO:
                    raise ValueError("ZMAIL_TO is not set.")
                if not self.ZMAIL_HOST:
                    raise ValueError("ZMAIL_HOST is not set.")

config = Config()


if __name__ == "__main__":
    try:
        config = Config()
        print("===Configuration Test===")
    except (FileNotFoundError, ValueError) as e:
        print(e)