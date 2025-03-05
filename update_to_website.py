# 将模组上传至MC百科
import Selenium
import requests

url = "https://modfile.mcmod.cn/admin/"

# 检查是否能链接
def check_connection():
    try:
        requests.get(url)
        return True
    except requests.exceptions.RequestException:
        return False

print(check_connection())
