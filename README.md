# MC百科模组文件上传懒人处理
主要是懒得检查模组更新导致的。
## 功能
检查模组更新

下载最新模组

列出模组数据

发送邮件通知

模拟浏览器在文件后台上传文件

## 实现
通过Cfwidget、ModrinthAPI获取模组更新，利用CurseforgeAPI、ModrinthAPI下载模组
通过向喵呜机~~勒索索取~~请求一份给定表格（B列到E列），或仿照下方给定表格示例自行构建。

![给定列表数据示例](https://github.com/IBeiKui/MCMOD-mod-updater/assets/50074117/0a1f0fb3-12ae-4f92-b429-7d1b5c61e7df)

通过Zmail发送邮件。如果你希望用邮件通知你上传的话，你需要在配置文件中启用邮箱通知并填入邮箱信息。

运行效果：
![Pasted image 20240214142809](https://github.com/IBeiKui/MCMOD-mod-updater/assets/50074117/116e2e48-403b-40d8-90ea-822ebcc99665)

如果你想定时获取更新，我推荐你使用Microsoft荣誉出品的任务计划程序定时运行本程序。

## 前置
**Python3.8**

## 使用
1. 下载本项目
2. 安装依赖
```shell pip install -r requirements.txt```
3. 在配置文件中填入CurseforgeAPI、ModrinthAPI等配置
4. 运行
```shell python main.py```
