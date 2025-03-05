# 将模组上传至MC百科
import os.path
import time
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import Tuple
import config
import json

yaml = config.yaml
config = config.config

url = "https://modfile-dl.mcmod.cn/admin/"
login_url = "https://www.mcmod.cn/login/"
center_url = "https://center.mcmod.cn/"
upload_folder = str(os.path.join(config.DOWNLOAD_PATH, config.LastModified))

# 选择浏览器
if config.CUSTOM_DRIVER_PATH is None:
    if config.Browser == "Chrome":
        drive = webdriver.Chrome()
    elif config.Browser == "Firefox":
        drive = webdriver.Firefox()
    elif config.Browser == "Edge":
        drive = webdriver.Edge()
else:
    service = Service(executable_path=config.CUSTOM_DRIVER_PATH)

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
        drive.get(url)
        print("正在连接至MC百科文件管理后台...")
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


def upload_mod() -> Tuple[bool, str]:
    # 先打开上传页面
    # https://modfile-dl.mcmod.cn/admin/{McmodID}
    last_McmodID = ""
    for path in os.listdir(upload_folder):
        # 打开txt文件
        if path.endswith(".yaml"):
            # try:
            with open(os.path.join(upload_folder, path), 'r', encoding='utf-8') as file:
                content = yaml.load(file)
                filename = content['fileName']
                print("正在上传：", filename)
                McmodID = content['McmodID']
                if last_McmodID != McmodID:
                    last_McmodID = McmodID
                    drive.get(f"{url}/{McmodID}")
                    # 上传文件
                    # try:
                    for uploaded_file_name in drive.find_elements(By.CLASS_NAME, "file-name"):
                        if uploaded_file_name.text == filename.split(".")[0]:
                            print("文件已存在，跳过上传")
                            continue
                    print("正在自动化操作，请勿接触键盘")
                    drive.find_element(By.XPATH, "//button[contains(text(),'上传文件')]").click()
                    drive.find_element(By.XPATH, "//label[@id='modfile-select-label']").click()
                    time.sleep(1)
                    to_type = os.path.abspath(os.path.join(upload_folder, filename))
                    pyperclip.copy(to_type)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                    pyautogui.typewrite("\n", interval=2)
                    time.sleep(0.5)
                    fill_mod_detail(content)
                    time.sleep(15)
                    drive.find_element(By.XPATH, "//button[contains(text(),'妥')]").click()
                    time.sleep(1)
        #         except Exception as e:
        #             return False, f"上传文件错误：{e}，跳过该文件"
        # except Exception as e:
        #     return False, f"打开文件错误：{e}，跳过该文件"
    return True, "全部文件上传成功"

def is_valid_version(version_str):
    available_version_special_word = ['w','Snapshot','.'] + [str(i) for i in range(10)]
    for word in available_version_special_word:
        if word in version_str:
            return True
    return False

def fill_mod_detail(info):
    platform_tick = False
    function_tick = False
    tag_tick = False
    ask_handle_reason = ""

    # 填写文件信息
    # 支持MC版本
    # //input[@id='modfile-upload-mcver']
    content = ""
    for version in info['gameVersions']:
        if is_valid_version(version):
            content += version + "/"
    content = content[:-1]
    drive.find_element(By.ID, "modfile-upload-mcver").send_keys(content)

    # 支持平台
    # JAVA版 (JAVA Edition)/基岩版 (Bedrock Edition)
    if info['gameType'] == "Java":
        drive.find_element(By.XPATH, "//label[@for='class-data-platform-1-upload']").click()
        platform_tick = True
    if info['gameType'] == "Bedrock":
        drive.find_element(By.XPATH, "//label[@for='class-data-platform-2-upload']").click()
        platform_tick = True

    # 运作方式
    # Forge Fabric Quilt NeoForge Rift LiteLoader Sandbox 数据包 行为包 资源包 命令方块 文件覆盖 其他
    if "forge" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-1-upload']']").click()
        function_tick = True
    if "fabric" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-2-upload']']").click()
        function_tick = True
    if "quilt" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-3-upload']']").click()
        function_tick = True
    if "neoforge" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-4-upload']']").click()
        function_tick = True
    if "rift" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-5-upload']']").click()
        function_tick = True
    if "liteloader" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-6-upload']']").click()
        function_tick = True
    # if "sandbox" in info['gameVersions']:
    #     drive.find_element(By.XPATH, "//label[@for='class-data-api-7-upload']']").click()  # who r u?
    #     function_tick = True
    if "datapack" in info['gameVersions']:
        drive.find_element(By.XPATH, "//label[@for='class-data-api-8-upload']']").click()  # TODO:实际上木有这个
        function_tick = True
    if info['fileName'].endswith(".mcaddon"):
        drive.find_element(By.XPATH, "//label[@for='class-data-api-9-upload']']").click()
        function_tick = True
    if info['fileName'].endswith(".mcpack"):
        drive.find_element(By.XPATH, "//label[@for='class-data-api-10-upload']']").click()
        function_tick = True

    # 文件标签
    # Snapshot: 快照Beta: 测试版Dev: 开发版Lite: 精简版Client: 仅客户端Server: 仅服务端
        # 如果所有版本都是快照版本
    if all([is_valid_version(version) and "w" in version for version in info['gameVersions']]):
        drive.find_element(By.XPATH, "//label[@for='class-data-tags-snapshot-upload']").click()
        tag_tick = True
    if info['fileState'] == "beta":
        drive.find_element(By.XPATH, "//label[@for='class-data-tags-beta-upload']").click()
        tag_tick = True
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
        if "Server" in info['gameVersions']:
            drive.find_element(By.XPATH, "//label[@for='class-data-tags-server-upload']").click()
            tag_tick = True

    # 检验自动操作是否成功完成
    if not platform_tick:
        ask_handle_reason += "支持平台未被自动填写"
    if not function_tick:
        ask_handle_reason += "运作方式未被自动填写"
    if not tag_tick:
        ask_handle_reason += "文件标签未被自动填写"

    if all([platform_tick, function_tick, tag_tick]):
        print("自动化操作完成！")
    else:
        print("自动化操作失败：", ask_handle_reason)
        print("请手动填写信息后点击上传按钮")
        while drive.find_elements(By.XPATH, "//p[contains(text(),'成功上传文件 1 个：')]"):
            if drive.find_elements(By.XPATH, "//p[contains(text(),'成功覆盖文件 1 个：')]"):
                print("文件已存在，跳过上传")
                break
            pass


def end_connection(reason: str):
    drive.quit()
    print("已关闭浏览器，原因：", reason)


if check_connection():
    # 检查待上传的文件夹是否存在
    if os.path.exists(upload_folder):
        print("已找到待上传的文件夹：", upload_folder)
        # 上传文件
        feedback = upload_mod()
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
