import ruamel.yaml
import os

yaml = ruamel.yaml.YAML(typ='rt')


class Config:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.load_config()

    def create_default_config(self):
        default_config = """
# == Configuration for Mcmod_mod_updater/用于Mcmod_mod_updater的配置 ==

# === API token for authentication/用于认证的API令牌 ===
# you can get your token from https://console.curseforge.com/?#/api-keys
# 你可以从https://console.curseforge.com/?#/api-keys获取你的token
CURSEFORGE_API_KEY: 
POOL_SIZE: 5

# === Database paths/数据位置 ===
# Path to the Excel database file that contains mod information, which is provided by MCMOD Website owner
# 包含模组信息的Excel数据库文件的路径，由MCMOD网站所有者提供
# The program will delete expired download cache folders, you can set the maximum number of cache folders and the maximum survival time of cache folders (unit: days)
# 程序会删除过期的下载缓存文件夹，你可以设置最大缓存文件夹数量和缓存文件夹的最大存活时间（单位：天）
DATABASE_PATH: ./Database.xlsx
MAX_DOWNLOAD_CACHE_FOLDERS: 5
MAX_DOWNLOAD_CACHE_AGE_DAYS: 30

# === Download setting/下载设置 ===
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

# === Selenium configuration/Selenium的浏览器配置 ===
# If you want to use Selenium to upload new mod files to MCMOD, set Selenium_enable to True
# 如果你想使用Selenium上传新的Mod文件到MCMOD，你需要将Selenium_enable设置为True
# You need to set download_enable to True to use Selenium
# 你需要将上方的download_enable设置为True才能使用Selenium
Selenium_enable: False

# If you want to use a custom driver path, fill in the path to the browser driver in Custom_driver_path, the program will use the custom driver path first
# 如果你想使用自定义驱动路径，请在Custom_driver_path填入为浏览器驱动的路径，程序会优先使用自定义驱动路径
CUSTOM_DRIVER_PATH:
# Please select the browser on your computer (or custom path)
# 请选择你电脑上（或自定义路径的）的浏览器
# Supported browsers: Chrome, Edge, Firefox
# 支持的浏览器：Chrome, Edge, Firefox
Browser: Edge

# === Zmail configuration/Zmail的配置 ===
# Zmail is a simple email sending tool, you can use it to send mod update notifications to your email
# if Zmail_enable is False, Zmail will not be used. If enabled, please download zmail by yourself
# Zmail是一个简单的邮件发送工具，你可以使用它将Mod更新通知发送到你的邮箱
# 如果Zmail_enable为False，Zmail将不会被使用，如果启用，请自行下载zmail库
Zmail_enable: False

ZMAIL_HOST: smtp.example.com
ZMAIL_PORT: 
ZMAIL_SSL: True
ZMAIL_USERNAME: your_username
ZMAIL_PASSWORD: your_password
ZMAIL_TO: to_an_email_address

# === End of configuration/配置结束 ===
# === Please do not delete or change the content below unless you know what you are doing ===
# === 请不要删除或更改下方的内容，除非你知道你在做什么 ===
LastModified: 
Finished_upload: True
Cookies:

# === Blacklist configuration/黑名单配置 ===
# Mods that fail to be read four times will be added to the blacklist
# 累计四次读取失败的模组将会被添加到黑名单
blacklist_enabled: False
blacklist: 
    -

"""
        with open(self.config_file, 'w', encoding='utf-8') as file:
            file.write(default_config)

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")

        with open(self.config_file, 'r', encoding='utf-8') as file:
            try:
                config = yaml.load(file) or {}

            except Exception as e:
                raise ValueError(f"Error parsing configuration file: {e}")

            self.CURSEFORGE_API_KEY = config.get('CURSEFORGE_API_KEY', None)
            self.DATABASE_PATH = config.get('DATABASE_PATH', None)
            self.POOL_SIZE = config.get('POOL_SIZE', 5)
            self.MAX_DOWNLOAD_CACHE_FOLDERS = config.get('MAX_DOWNLOAD_CACHE_FOLDERS', 5)
            self.MAX_DOWNLOAD_CACHE_AGE_DAYS = config.get('MAX_DOWNLOAD_CACHE_AGE_DAYS', 30)

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
            self.CUSTOM_DRIVER_PATH = config.get('CUSTOM_DRIVER_PATH', None)
            self.Browser = config.get('Browser', 'Edge')

            self.Zmail_enable = config.get('Zmail_enable', False)
            self.ZMAIL_HOST = config.get('ZMAIL_HOST', None)
            self.ZMAIL_PORT = config.get('ZMAIL_PORT', None)
            self.ZMAIL_SSL = config.get('ZMAIL_SSL', True)
            self.ZMAIL_USERNAME = config.get('ZMAIL_USERNAME', None)
            self.ZMAIL_PASSWORD = config.get('ZMAIL_PASSWORD', None)
            self.ZMAIL_TO = config.get('ZMAIL_TO', None)

            self.LastModified = config.get('LastModified', None)
            self.Finished_upload = config.get('Finished_upload', True)
            self.Cookies = config.get('Cookies', None)

            self.blacklist_enabled = config.get('blacklist_enabled', False)
            self.blacklist = config.get('blacklist', list())

            # 检查是否为空
            if not self.CURSEFORGE_API_KEY:
                raise ValueError("CURSEFORGE_API_KEY is not set.")
            if not self.DATABASE_PATH:
                raise ValueError("DATABASE_PATH is not set.")
            if os.path.exists(self.DATABASE_PATH) is False:
                raise FileNotFoundError(f"DATABASE_PATH '{self.DATABASE_PATH}' not found.")
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
                if not self.ZMAIL_PORT:
                    raise ValueError("ZMAIL_PORT is not set.")
            if self.Selenium_enable:
                if self.CUSTOM_DRIVER_PATH is not None and os.path.exists(self.CUSTOM_DRIVER_PATH) is False:
                    raise FileNotFoundError(f"CUSTOM_DRIVER_PATH '{self.CUSTOM_DRIVER_PATH}' not found.")
                if self.Browser not in ['Chrome', 'Edge', 'Firefox']:
                    raise ValueError("Browser is not supported.")

    def write_config(self, key, value):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = yaml.load(file)
        if key in config:
            config[key] = value
        else:
            raise KeyError(f"Key '{key}' not found in configuration file.")
        with open(self.config_file, 'w', encoding='utf-8') as file:
            yaml.dump(config, file)


config = Config()

if __name__ == "__main__":
    try:
        config = Config()
        print("===Configuration Test===")
    except (FileNotFoundError, ValueError) as e:
        print(e)
