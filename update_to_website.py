# 将模组上传至MC百科
import os.path
import time
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from typing import Tuple
import config
from distutils.version import LooseVersion
import mod_downloader

yaml = config.yaml
config = config.config

url = "https://modfile-dl.mcmod.cn/admin/"
login_url = "https://www.mcmod.cn/login/"
center_url = "https://center.mcmod.cn/"
if config.DOWNLOAD_PATH and config.LastModified:
    upload_folder = str(os.path.join(config.DOWNLOAD_PATH, config.LastModified))
else:
    raise ValueError("DOWNLOAD_PATH or LastModified is not set.")

# 选择浏览器
if config.CUSTOM_DRIVER_PATH is None:
    if config.Browser == "Chrome":
        drive = webdriver.Chrome()
    elif config.Browser == "Firefox":
        drive = webdriver.Firefox()
    elif config.Browser == "Edge":
        drive = webdriver.Edge()
else:
    if config.Browser == "Chrome":
        drive = webdriver.Chrome(service=ChromeService(config.CUSTOM_DRIVER_PATH))
    elif config.Browser == "Firefox":
        drive = webdriver.Firefox(service=FirefoxService(config.CUSTOM_DRIVER_PATH))
    elif config.Browser == "Edge":
        drive = webdriver.Edge(service=EdgeService(config.CUSTOM_DRIVER_PATH))

if drive is None:
    raise ValueError("Unable to find the browser driver.")

drive.implicitly_wait(3)
if config.Cookies:
    drive.get(url)
    drive.delete_all_cookies()
    for cookie in config.Cookies:
        drive.add_cookie(cookie)
    drive.refresh()


# 检查是否能链接
def check_connection():
    try:
        print("正在连接至MC百科文件管理后台...")
        drive.get(url)
        if drive.find_elements(By.CLASS_NAME, "modfile-select-frame"):
            print("连接成功！")
            return True
        elif drive.find_elements(By.CLASS_NAME, "html-tag"):
            print("没有权限访问文件管理后台，请检查是否登录了MC百科。")
            print("将弹出窗口要求登录... 登录后程序将继续运行")
            if login():
                return check_connection()
            else:
                end_connection("登陆失败")
    except Exception as e:
        print("未定义的错误：", e)
        return False


# 登录
def login():
    try:
        drive.get(login_url)
        # if config.Is_QQ_Login:
        #     drive.find_element(By.CLASS_NAME, 'header-user unlogin').find_elements(By.ID, "li")[1].click()
        # # 等待用户输入，检测到https://center.mcmod.cn/打开时停止等待
        while drive.current_url.startswith("https://center.mcmod.cn/") is False and drive.find_elements(By.CLASS_NAME,
                                                                                                        'header-user-avatar') == []:
            #         if config.Is_QQ_Login and drive.switch_to.frame('login_frame'):
            #             drive.find_element(By.ID,'switcher_plogin').click()
            #             drive.find_element(By.ID,'u').send_keys(config.Login_username)
            #             drive.find_element(By.ID,'p').send_keys(config.Login_password)
            #             drive.find_element(By.ID,'login_button').click()
            pass
        print("登录成功！")
        drive.get(url)
        time.sleep(1)
        config.write_config("Cookies", drive.get_cookies())
        return True
    except Exception as e:
        print("打开页面错误：", e)
        return False


def upload_mod(available_files_path) -> Tuple[bool, str]:
    # 先打开上传页面
    # https://modfile-dl.mcmod.cn/admin/{McmodID}
    last_McmodID = ""


    for path in available_files_path:
        try:
            with open(os.path.join(upload_folder, path), 'r', encoding='utf-8') as file:
                content = yaml.load(file)
                filename = content['fileName']
                print("正在上传：", filename)
                skip_mark = False
                McmodID = content['McmodID']

                if last_McmodID != McmodID:
                    last_McmodID = McmodID
                    drive.get(f"{url}/{McmodID}")
                    uploaded_files_name = [uploaded_file.text for uploaded_file in
                                           drive.find_elements(By.CLASS_NAME, "file-name")]
                    # 上传文件
                try:
                    if filename in uploaded_files_name:
                        print("文件已存在，跳过上传")
                        skip_mark = True

                    if skip_mark:
                        continue
                    print("正在自动化操作，请勿接触键盘")
                    drive.find_element(By.XPATH, "//button[contains(text(),'上传文件')]").click()
                    time.sleep(0.8)
                    drive.find_element(By.XPATH, "//label[@id='modfile-select-label']").click()
                    time.sleep(0.8)
                    to_type = os.path.abspath(os.path.join(upload_folder, filename))
                    pyperclip.copy(to_type)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.8)
                    pyautogui.typewrite("\n")
                    time.sleep(0.5)
                    fill_mod_detail(content)

                    # 5秒检查时间，可手动关闭页面跳过本次上传
                    Countdown = 5
                    while Countdown < 0:
                        if not drive.find_elements(By.CLASS_NAME, "modal fade show"):
                            print("检测到取消按钮，跳过上传")
                            skip_mark = True
                        time.sleep(1)
                        Countdown -= 1
                    if skip_mark:
                        continue

                    drive.find_element(By.XPATH, "//button[@id='modfile-upload-btn']").click()
                    while drive.find_elements(By.XPATH, "//button[contains(text(),'妥')]") is not []:
                        time.sleep(0.1)
                        drive.find_element(By.XPATH, "//button[contains(text(),'妥')]").click()
                        break
                    time.sleep(1)
                except Exception as e:
                    print("上传文件错误：", e)
                    print("跳过该文件")
                    pass
        except Exception as e:
            return False, f"打开文件错误：{e}，跳过该文件，{filename}"
    return True, "全部文件上传成功"


def is_valid_version(version_str):
    available_version_special_word = ['w', 'Snapshot', '.'] + [str(i) for i in range(10)]
    for word in available_version_special_word:
        if word in version_str:
            return True
    return False


def fill_mod_detail(info):
    platform_tick = False
    function_tick = False
    tag_tick = False
    auto_tick_content = ""
    ask_handle_reason = ""

    # 填写文件信息
    # 支持MC版本
    # //input[@id='modfile-upload-mcver']
    # Sort versions using LooseVersion
    valid_versions = [version for version in info['gameVersions'] if is_valid_version(version)]
    sorted_versions = sorted(valid_versions, key=LooseVersion)

    # 整合版本
    # 当连续的版本号出现三个及以上时，将其合并为一个版本范围
    # 例如 [1.16 1.16.1 1.16.2 1.16.3 1.16.4 1.16.5] => 1.16-1.16.5
    # 跨二级版本号的版本不会被合并
    # 例如 [1.16 1.16.1 1.16.2 1.17 1.18 1.18.1] => 1.18.1/1.18/1.17/1.16-1.16.2
    # 整合版本
    version_groups = {}
    for v in sorted_versions:
        parts = v.split('.')
        if len(parts) >= 2:
            major = '.'.join(parts[:2])
            if major not in version_groups:
                version_groups[major] = []
            version_groups[major].append(v)
        else:
            if v not in version_groups:
                version_groups[v] = []
            version_groups[v].append(v)

    merged_versions = []
    # 处理每个主版本组
    for major in sorted(version_groups.keys(), key=LooseVersion, reverse=True):
        group = sorted(version_groups[major], key=LooseVersion)
        if len(group) >= 3:
            # 如果有3个或以上版本，合并它们
            merged_versions.append(f"{group[0]}-{group[-1]}")
        else:
            # 否则，单独添加
            merged_versions.extend(sorted(group, key=LooseVersion, reverse=True))

    merged_versions.reverse()
    content = "/".join(merged_versions)

    drive.find_element(By.ID, "modfile-upload-mcver").send_keys(content)

    # 支持平台
    # JAVA版 (JAVA Edition)/基岩版 (Bedrock Edition)
    if info['gameType'] == "Java":
        drive.find_element(By.XPATH, "//label[@for='class-data-platform-1-upload']").click()
        platform_tick = True
        auto_tick_content += "JAVA版 "
    if info['gameType'] == "Bedrock":
        drive.find_element(By.XPATH, "//label[@for='class-data-platform-2-upload']").click()
        platform_tick = True
        auto_tick_content += "基岩版 "

    # 运作方式
    # Forge Fabric Quilt NeoForge Rift LiteLoader Sandbox 数据包 行为包 资源包 命令方块 文件覆盖 其他
    # 重生你按钮序号不要乱放qwq
    if "forge" in info['gameVersions'] or "Forge" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-1-upload']").click()
        function_tick = True
        auto_tick_content += "Forge "
    if "fabric" in info['gameVersions'] or "Fabric" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-2-upload']").click()
        function_tick = True
        auto_tick_content += "Fabric "
    if "quilt" in info['gameVersions'] or "Quilt" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-11-upload']").click()
        function_tick = True
        auto_tick_content += "Quilt "
    if "neoforge" in info['gameVersions'] or "NeoForge" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-13-upload']").click()
        function_tick = True
        auto_tick_content += "NeoForge "
    if "rift" in info['gameVersions'] or "Rift" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-3-upload']").click()
        function_tick = True
        auto_tick_content += "Rift "
    if "liteloader" in info['gameVersions'] or "LiteLoader" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-4-upload']").click()
        function_tick = True
        auto_tick_content += "LiteLoader "
    # if "sandbox" in info['gameVersions']:
    #     drive.find_element(By.XPATH, "//label[@for='class-data-api-9-upload']").click()  # who r u?
    #     function_tick = True
    if "datapack" in info['gameVersions'] or "Datapack" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-5-upload']").click()
        function_tick = True
        auto_tick_content += "数据包 "
        # 对在Curseforge获取的数据包进行提醒
        if "forgecdn" in info['downloadUrl']:
            print("请注意，该“数据包”的文件标签判断可能不准确，因无法从Curseforge API准确判断是否为数据包")

    if info['fileName'].endswith(".mcaddon"):
        drive.find_element(By.XPATH, "//label[@for='class-data-api-8-upload']").click()
        function_tick = True
        auto_tick_content += "行为包 "
    if info['fileName'].endswith(".mcpack"):
        drive.find_element(By.XPATH, "//label[@for='class-data-api-12-upload']").click()
        function_tick = True
        auto_tick_content += "资源包 "

    # 文件标签
    # Snapshot: 快照Beta: 测试版Dev: 开发版Lite: 精简版Client: 仅客户端Server: 仅服务端
    # 如果所有版本都是快照版本 "w" 或 "Snapshot" 且 is_valid_version
    if all([is_valid_version(version) for version in info['gameVersions']]) and all(
            ["w" in version or "Snapshot" in version for version in info['gameVersions']]):
        drive.find_element(By.XPATH, "//label[@for='class-data-tags-snapshot-upload']").click()
        tag_tick = True
        auto_tick_content += "Snapshot "
    if info['fileState'] == "beta":
        drive.find_element(By.XPATH, "//label[@for='class-data-tags-beta-upload']").click()
        tag_tick = True
        auto_tick_content += "Beta "
    # if "Dev" in info['fileState']:
    #     drive.find_element(By.XPATH, "//label[@for='class-data-tags-dev-upload']").click() # 木有这个
    #     tag_tick = True
    # if "Lite" in info['fileState']:
    #     drive.find_element(By.XPATH, "//label[@for='class-data-tags-lite-upload']").click() # 木有这个
    #     tag_tick = True
    if not ("Client" in info['gameVersions'] and "Server" in info['gameVersions']):
        if "Client" in info['gameVersions']:
            drive.find_element(By.XPATH, "//label[@for='class-data-tags-client-upload']").click()
            tag_tick = True
            auto_tick_content += "仅客户端 "
        if "Server" in info['gameVersions']:
            drive.find_element(By.XPATH, "//label[@for='class-data-tags-server-upload']").click()
            tag_tick = True
            auto_tick_content += "仅服务端 "

    # 检验自动操作是否成功完成
    if not platform_tick:
        ask_handle_reason += "支持平台未被自动填写"
    if not function_tick:
        ask_handle_reason += "运作方式未被自动填写"
    if not tag_tick:
        ask_handle_reason += "文件标签未被自动填写"
        print("请注意，该项目文件标签未被自动填写")

    if any([platform_tick, function_tick]):
        print("自动化操作完成！")
        print("自动化操作内容：", auto_tick_content)
    else:
        print("自动化操作失败：", ask_handle_reason)
        print("已自动化填写的内容：", auto_tick_content)
        print("请手动填写信息后点击上传按钮")
        while drive.find_elements(By.XPATH, "//p[contains(text(),'成功上传文件 1 个：')]"):
            if drive.find_elements(By.XPATH, "//p[contains(text(),'成功覆盖文件 1 个：')]"):
                print("文件已存在，跳过上传")
                break
            pass


def end_connection(reason: str):
    drive.quit()
    print("已关闭浏览器，原因：", reason)

def get_available_files_path():
    listdir = os.listdir(upload_folder)
    available_files_path = []
    # 处理有相同ModID和gameVersions的情况，只保留最新版本
    temp_comparison = dict()
    for path in listdir:
        if path.endswith(".yaml"):
            with open(os.path.join(upload_folder, path), 'r', encoding='utf-8') as file:
                content = yaml.load(file)
                mod_id = content['McmodID']
                game_versions = content['gameVersions']
                comparison = str(mod_id).join(game_versions)
                if comparison in temp_comparison:
                    if LooseVersion(path) > LooseVersion(temp_comparison[comparison]):
                        print(f"{temp_comparison[comparison]}有更新的版本{path}，将覆盖旧版本")
                        temp_comparison[comparison] = path
                    else:
                        continue
                else:
                    temp_comparison[comparison] = path

    for i in temp_comparison.values():
        available_files_path.append(i)

    for path in listdir:
        with open(os.path.join(upload_folder, path), 'r', encoding='utf-8') as file:
            content = yaml.load(file)
            mod_downloader.requests_download(content['downloadUrl'], config.LastModified, content['fileName'])

    return available_files_path


config.load_config()
if not config.Finished_upload:
    if check_connection():
        # 检查待上传的文件夹是否存在
        if os.path.exists(upload_folder):
            print("已找到待上传的文件夹：", upload_folder)
            # 上传文件
            feedback = upload_mod(get_available_files_path())
            if feedback[0]:
                print("上传成功！")
                config.write_config("Finished_upload", True)
                end_connection("上传成功")
            else:
                print("上传失败：", feedback[1])
                end_connection(feedback[1])
        else:
            print("没有找到待上传的文件夹：", upload_folder)
            config.write_config("Finished_upload", True)
            end_connection("没有找到待上传的文件夹")
    else:
        end_connection("无法连接至服务器")
else:
    print("没有需要上传的文件")
    end_connection("没有需要上传的文件")
