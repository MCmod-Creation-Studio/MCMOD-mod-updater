# MC百科模组文件上传懒人处理
主要是懒得检查模组更新导致的。
## 功能
检查模组更新
下载最新模组
列出模组数据
发送邮件通知
## 实现
通过Cfwidget、ModrinthAPI获取模组更新，利用CurseforgeAPI、ModrinthAPI下载模组
通过向喵呜机~~勒索索取~~给定表格（B列到E列）![给定列表数据示例](https://github.com/IBeiKui/MCMOD-mod-updater/assets/50074117/0a1f0fb3-12ae-4f92-b429-7d1b5c61e7df)
通过Zmail发送邮件。如果你希望用邮件通知你上传的话，运行ZmailOut.py

运行效果：
![Pasted image 20240214142809](https://github.com/IBeiKui/MCMOD-mod-updater/assets/50074117/116e2e48-403b-40d8-90ea-822ebcc99665)

如果你想定时获取更新，我推荐你使用Microsoft荣誉出品的任务计划程序定时运行本程序。
## 前置
软件：**Python3.8**
第三方库：**requests，openpyxl，rich，urllib3，PyTaskbar**，（可选）Zmail
环境变量设置：
main.py：
DATABASE_PATH （给定表格的路径，如：**C:/MCmodFile.xlsx**）

Mod_downloader.py:
CURSEFORGE_API_KEY

ZmailOut.py：
ZMAIL_USERNAME （发件人邮箱）
ZMAIL_PASSWORD （发件人邮箱密码）
ZMAIL_HOST （发信服务器地址，如：**smtp.qq.com**）
ZMAIL_PORT （发信服务器地址端口，如：**465**）
ZMAIL_SSL （SSL是否开启，如：**True**）
ZMAIL_TO （收件人邮箱）
