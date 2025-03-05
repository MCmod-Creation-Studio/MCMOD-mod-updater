# MC百科模组文件上传懒人处理
主要是懒得检查模组更新导致的。
## 功能（简略版）
检查模组更新

下载最新模组

列出模组数据

发送邮件通知

模拟浏览器在文件后台上传文件

## 功能

## 工作流程

1. **初始化阶段**：
   - 加载配置文件，如果不存在则创建默认配置
   - 验证必要配置（如 API 密钥、数据库路径）

2. **模组信息获取**：
   - 从 Curseforge 或 Modrinth API 获取模组文件信息
   - 解析响应，获取文件名、下载链接、日期和版本信息

3. **文件下载过程**：
   - 创建目录结构（以时间戳命名的文件夹）
   - 使用流式下载，显示进度条
   - 下载失败时自动重试（最多 `TIMEOUT_RETRY` 次）
   - 保存模组文件及其元数据（YAML 格式）

4. **数据库更新**：
   - 更新 Excel 数据库中的模组信息
   - 保存更改，失败时创建备份文件

5. **可选的自动上传**：
   - 如果启用，使用 Selenium 自动化浏览器
   - 访问 MCMOD 网站并上传新下载的模组文件
   - 通过配置中的 `LastModified` 和 `Finished_upload` 跟踪进度
   - 使用配置中的 `Cookies` 保存登录状态，避免重复登录

6. **可选的邮件通知**：
   - 如果 `Zmail_enable` 为 `True`，使用 Zmail 库发送模组更新通知
   - 邮件内容为所有获得更新的模组名称、获取到的更新时间、上次获取的时间

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
5. 如果你想使用Zmail发送邮件，你需要手动下载zmail依赖，并在配置文件中填入邮箱信息
```shell pip install zmail```

## 配置项
- CURSEFORGE_API_KEY: CurseforgeAPI的API_KEY
- POOL_SIZE: 访问线程数
- DATABASE_PATH: 给定表格的文件路径(.xlsx)

- download_enable: 是否下载模组（默认开启）
- headers: 请求头
- DOWNLOAD_PATH: 下载路径
- TIMEOUT_RETRY: 超时重试次数


- Selenium_enable: 是否使用Selenium（用于模拟用户操作MC百科文件后台，需要启用download_enable选项才可用）（默认关闭）
- CUSTOM_DRIVER_PATH: 自定义浏览器驱动路径
- Browser: 浏览器


- Zmail_enable: 是否使用Zmail（默认关闭）
- ZMAIL_HOST: 邮箱服务器
- ZMAIL_PORT: 端口
- ZMAIL_SSL: 是否使用SSL
- ZMAIL_USERNAME: 邮箱用户名
- ZMAIL_PASSWORD: 邮箱密码
- ZMAIL_TO: 发送邮件的地址

