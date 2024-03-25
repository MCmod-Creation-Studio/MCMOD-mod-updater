# 导入必要的模块，并检查CURSEFORGE_API_KEY环境变量是否已设置
from os import makedirs, getenv
import requests as rq

if not getenv('CURSEFORGE_API_KEY'):
    raise Exception('CURSEFORGE_API_KEY environment variable not set.')
# 设置请求头，使用CURSEFORGE_API_KEY环境变量
headers = {
    'Accept': 'application/json',
    'x-api-key': getenv('CURSEFORGE_API_KEY')
}


def requests_download(url, mcmod_id, time, file_name, file_date, game_versions, release_type):
    """
    下载Mod文件并保存，同时创建包含Mod信息的文本文件。

    :param url: 文件下载链接
    :param mcmod_id: Mod的ID
    :param time: 保存目录的时间戳
    :param file_name: 文件名（不含路径）
    :param file_date: 文件日期
    :param game_versions: 支持的游戏版本
    :param release_type: 发布类型（发行版、测试版、alpha等）

    """
    print("正在下载：" + url)
    jar = rq.get(url).content  # 获取文件内容
    # 构建包含Mod信息的字符串
    content = "fileName:" + file_name + "\nMcmodID:" + str(
        mcmod_id) + "\ndownloadUrl:" + url + "\nfileDate:" + file_date + "\ngameVersions:" + game_versions + " \nfileState:" + release_type
    # 创建保存目录（如果不存在）
    makedirs('./{0}'.format(time, file_name), exist_ok=True)
    # 写入文件内容
    with open('./{0}/{1}'.format(time, file_name), 'wb') as file:
        file.write(jar)
    # 写入包含Mod信息的文本文件
    with open('./{0}/{1}.txt'.format(time, file_name.replace(".jar", "")), 'a') as file:
        file.write(content)


def download_mod(website, mcmod_id, time, project_id, file_id):
    """
    根据提供的网站类型和项目ID下载Mod文件。

    :param website: 网站名称（例如：Curseforge或Modrinth）
    :param mcmod_id: Mod的ID
    :param time: 保存目录的时间戳
    :param project_id: 项目ID
    :param file_id: 文件ID列表
    """
    for i in file_id:
        # 根据网站类型执行不同的API请求和数据处理
        if website == "Curseforge":
            i_str = str(i)
            # 请求Curseforge API获取文件信息
            k = rq.get(r'https://api.curseforge.com/v1/mods/{0}/files/{1}'.format(project_id, i), headers=headers,
                       params={'param': '1'}, verify=False).json()
            fileName = k["data"]["fileName"]
            downloadUrl = 'https://edge.forgecdn.net/files/{0}/{1}'.format(i_str[0:4] + "/" + i_str[4:], fileName)
            fileDate = k["data"]["fileDate"]
            releaseType = ["发行版", "测试版"][k["data"]["releaseType"] > 1]
            gameVersions = str(k["data"]["gameVersions"])
            # 调用函数下载文件
            requests_download(downloadUrl, mcmod_id,
                              str(time).replace(" ", "+").replace(":", "-"),
                              fileName,
                              fileDate.replace(":", "-"),
                              gameVersions,
                              releaseType)

        elif website == "Modrinth":
            # 请求Modrinth API获取文件信息
            k = rq.get(r'https://api.modrinth.com/v2/project/{0}/version/{1}'.format(project_id, i),
                       params={'param': '1'}, verify=False).json()
            downloadUrl = k["files"][0]["url"]
            fileName = k["files"][0]["filename"]
            fileDate = k["date_published"]
            releaseType = k["version_type"]
            gameVersions = str(k["loaders"] + k["game_versions"])
            # 调用函数下载文件
            requests_download(downloadUrl,
                              mcmod_id,
                              str(time).replace(" ", "+").replace(":", "-"),
                              fileName,
                              fileDate.replace(":", "-"),
                              gameVersions,
                              releaseType)

