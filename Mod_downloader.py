# 导入必要的模块，并检查CURSEFORGE_API_KEY环境变量是否已设置
import config
from os import makedirs
import requests as rq
from tqdm import tqdm
yaml = config.yaml
config = config.config
CURSEFORGE_API_KEY = config.CURSEFORGE_API_KEY
TIMEOUT_RETRY = config.TIMEOUT_RETRY
DOWNLOAD_PATH = config.DOWNLOAD_PATH

if not CURSEFORGE_API_KEY:
    raise Exception('CURSEFORGE_API_KEY environment variable not set.')
# 设置请求头，使用CURSEFORGE_API_KEY环境变量
headers = {
    'Accept': 'application/json',
    'x-api-key': CURSEFORGE_API_KEY
}


def requests_download(url, mcmod_id, time, file_name, file_date, game_versions, release_type, game_type):
    """
    下载Mod文件并保存，同时创建包含Mod信息的文本文件。
    :param url: 文件下载链接
    :param mcmod_id: Mod的ID
    :param time: 保存目录的时间戳
    :param file_name: 文件名（不含路径）
    :param file_date: 文件日期
    :param game_versions: 支持的游戏版本
    :param release_type: 发布类型（发行版、测试版、alpha等）
    :param game_type: 游戏类型（Java、Bedrock等）
    """
    print("正在下载：" + url)
    makedirs('./{0}/{1}'.format(DOWNLOAD_PATH, time, file_name), exist_ok=True)  # 创建保存目录（如果不存在）
    # 构建包含Mod信息的字符串

    content = {
        "fileName": file_name,
        "McmodID": mcmod_id,
        "downloadUrl": url,
        "fileDate": file_date,
        "gameVersions": game_versions,
        "fileState": release_type,
        "gameType": game_type

    }
    error_counter = 0
    while error_counter <= TIMEOUT_RETRY:
        try:
            response = rq.get(url, stream=True, timeout=10)  # 开启流式下载
            response.raise_for_status()  # 如果请求失败，抛出异常
            total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小
            with open('./{0}/{1}/{2}'.format(DOWNLOAD_PATH, time, file_name), 'wb') as file:
                progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
                for data in response.iter_content(1024):
                    file.write(data)
                    progress_bar.update(len(data))
                progress_bar.close()
            # 将Mod信息写入文本文件
            with open('./{0}/{1}/{2}.yaml'.format(DOWNLOAD_PATH, time, file_name.replace(".jar", "")), 'a', encoding="UTF-8") as file:
                yaml.dump(content, file)
                if config.Selenium_enable:
                    config.write_config("LastModified", time)
                    config.write_config("Finished_upload", False)
                break
        except Exception as E:
            if error_counter <= TIMEOUT_RETRY:
                print(f"下载失败：{url}，\n原因：{E}\n（重试次数：{error_counter}/5）")
                error_counter += 1
            else:
                with open('./{0}/{1}/{2}.yaml'.format(DOWNLOAD_PATH, time, file_name.replace(".jar", "")), 'a', encoding="UTF-8") as file:
                    file.write("______！该文件下载失败！______\n" + f"原因：{E}" + str(content))
                error_counter = 0


def download_mod(website, mcmod_id, time, project_id, file_id):
    """
    根据提供的网站类型和项目ID下载Mod文件。
    :param website: 网站名称（例如：Curseforge或Modrinth）
    :param mcmod_id: Mod的ID
    :param time: 保存目录的时间戳
    :param project_id: 项目ID
    :param file_id: 文件ID列表
    """
    try:
        for i in file_id:
            # 根据网站类型执行不同的API请求和数据处理
            if website == "Curseforge":
                i_str = str(i)
                # 请求Curseforge API获取文件信息

                k = rq.get(r'https://api.curseforge.com/v1/mods/{0}/files/{1}'.format(project_id, i),
                           headers=headers, params={'param': '1'}, verify=False).json()
                print(k)
                fileName = k["data"]["fileName"]
                downloadUrl = k['data']['downloadUrl']
                fileDate = k["data"]["fileDate"]
                releaseType = ["release", "beta"][k["data"]["releaseType"] > 1]
                gameVersions = k["data"]["gameVersions"]
                if k["data"]["gameId"] == 432:
                    gameType = "Java"
                elif k["data"]["gameId"] == 78022:
                    gameType = "Bedrock"
                else:
                    gameType = "Other"
                # 调用函数下载文件
                requests_download(downloadUrl, mcmod_id,
                                  time,
                                  fileName,
                                  fileDate.replace(":", "-"),
                                  gameVersions,
                                  releaseType, gameType)

            elif website == "Modrinth":
                # 请求Modrinth API获取文件信息
                k = rq.get(r'https://api.modrinth.com/v2/project/version/{0}'.format(i),
                           params={'param': '1'}, verify=False).json()
                project_info = rq.get(r'https://api.modrinth.com/v2/project/{0}'.format(project_id), params={'param': '1'}, verify=False).json()
                downloadUrl = k["files"][0]["url"]
                fileName = k["files"][0]["filename"]
                fileDate = k["date_published"]
                releaseType = "release" if k["version_type"] == "release" else "beta"
                gameVersions = k["loaders"] + k["game_versions"]
                if project_info["client_side"] == "required":
                    gameVersions += ["Client"]
                if project_info["server_side"] == "required":
                    gameVersions += ["Server"]
                gameType = "Java" # Modrinth只有Java版
                # 调用函数下载文件
                requests_download(downloadUrl,
                                  mcmod_id,
                                  time,
                                  fileName,
                                  fileDate.replace(":", "-"),
                                  gameVersions,
                                  releaseType, gameType)
    except Exception as E:
        print("读取失败" + str(E) + "跳过此项目：" + website + ": " + str(project_id))