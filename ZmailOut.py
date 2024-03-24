
# 导入必要的模块和库
from datetime import datetime
from os import getenv
import zmail
from main import DuplicatesList

def read_env():
    """
    读取环境变量配置
    :return: 包含环境变量配置的字典
    """
    env={}
    # 从环境变量中读取邮件服务所需的配置
    env["zmail_username"] = getenv("ZMAIL_USERNAME")
    env["zmail_password"] = getenv("ZMAIL_PASSWORD")
    env["zmail_host"] = getenv("ZMAIL_HOST")
    env["zmail_port"] = getenv("ZMAIL_PORT")
    env["zmail_ssl"] = getenv("ZMAIL_SSL")
    env["zmail_to"] = getenv("ZMAIL_TO")
    return env

# 读取环境变量配置
env = read_env()
# 检查是否设置了所有必要的环境变量
if not all([env["zmail_username"], env["zmail_host"], env["zmail_password"], env["zmail_port"], env["zmail_ssl"], env["zmail_to"]]):
    raise EnvironmentError("Please set environment variables.")

# 初始化邮件服务器连接
server = zmail.server(env["zmail_username"],env["zmail_password"],smtp_host=env["zmail_host"],smtp_port=env["zmail_port"],smtp_ssl=env["zmail_ssl"])

# 准备邮件正文
output= ''
for i in DuplicatesList:
    output += str(i) + "\n"

# 根据是否有发现已更新的模组来构造不同的邮件内容
if DuplicatesList != []:
    content_text = "发现已更新的模组！：\n MCMODid: 模组名称 || 获取到的更新时间 | 上次获取的时间\n" + output
else:
    content_text = "没有发现已更新的模组"

# 构造邮件正文
mail_body = {
    'to': env["zmail_to"],
    'from': env["zmail_username"],
    'subject':'{}模组更新检测报告'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    'content_text': content_text
}
print(mail_body)
# 发送邮件
server.send_mail(env["zmail_to"], mail_body)