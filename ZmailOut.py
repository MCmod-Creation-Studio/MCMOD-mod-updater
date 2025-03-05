# 导入必要的模块和库
import config_reader
from datetime import datetime
import zmail
from Data_updater import DuplicatesList


def read_env():
    """
    读取环境变量配置
    :return: 包含环境变量配置的字典
    """
    # 从配置文件中读取邮件服务所需的配置
    config = config_reader.Config()
    env = {
        "zmail_host": config.ZMAIL_HOST,
        "zmail_port": config.ZMAIL_PORT,
        "zmail_ssl": config.ZMAIL_SSL,
        "zmail_username": config.ZMAIL_USERNAME,
        "zmail_password": config.ZMAIL_PASSWORD,
        "zmail_to": config.ZMAIL_TO
    }
    return env


# 读取环境变量配置
env = read_env()
# 检查是否设置了所有必要的环境变量
if not all(env.values()):
    raise EnvironmentError("Please set environment variables.")

# 初始化邮件服务器连接
server = zmail.server(env["zmail_username"], env["zmail_password"], smtp_host=env["zmail_host"],
                      smtp_port=env["zmail_port"], smtp_ssl=env["zmail_ssl"])

# 准备邮件正文
output = ''
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
    'subject': '{}模组更新检测报告'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    'content_text': content_text
}
print("已发送正文：\n", mail_body)
# 发送邮件
server.send_mail(env["zmail_to"], mail_body)
