from os import makedirs, getenv
import requests as rq
if not getenv('CURSEFORGE_API_KEY'):
    raise Exception('CURSEFORGE_API_KEY environment variable not set.')
headers = {
    'Accept': 'application/json',
    'x-api-key': getenv('CURSEFORGE_API_KEY')
}
def requests_download(url, mcmod_id, time, file_name, file_date, game_versions, release_type):
    print("正在下载：" + url)
    jar = rq.get(url).content
    content = "fileName:" + file_name + "\nMcmodID:" + str(mcmod_id) + "\ndownloadUrl:" + url + "\nfileDate:" + file_date + "\ngameVersions:" + game_versions + " \nfileState:" + release_type
    makedirs('./{0}'.format(time, file_name), exist_ok=True)
    with open('./{0}/{1}'.format(time, file_name), 'wb') as file:
        file.write(jar)
    with open('./{0}/{1}.txt'.format(time, file_name.replace(".jar","")), 'a') as file:
        file.write(content)


def download_mod(website, mcmod_id, time, project_id, file_id):
    for i in file_id:
        if website == "Curseforge":
            i_str = str(i)
            k = rq.get(r'https://api.curseforge.com/v1/mods/{0}/files/{1}'.format(project_id, i), headers=headers,
                       params={'param': '1'}, verify=False).json()
            fileName = k["data"]["fileName"]
            downloadUrl = 'https://edge.forgecdn.net/files/{0}/{1}'.format(i_str[0:4] + "/" + i_str[4:], fileName)
            fileDate = k["data"]["fileDate"]
            releaseType = ["发行版", "测试版"][k["data"]["releaseType"] > 1]
            # releaseType
            # 1 = Release
            # 2 = Beta
            # 3 = Alpha
            gameVersions = str(k["data"]["gameVersions"])
            requests_download(downloadUrl, mcmod_id,
                              str(time).replace(" ", "+").replace(":", "-"),
                              fileName,
                              fileDate.replace(":", "-"),
                              gameVersions,
                              releaseType)

        elif website == "Modrinth":
            k = rq.get(r'https://api.modrinth.com/v2/project/{0}/version/{1}'.format(project_id, i),
                       params={'param': '1'}, verify=False).json()
            downloadUrl = k["files"][0]["url"]
            fileName = k["files"][0]["filename"]
            fileDate = k["date_published"]
            releaseType = k["version_type"]
            gameVersions = str(k["loaders"] + k["game_versions"])
            requests_download(downloadUrl,
                              mcmod_id,
                              str(time).replace(" ", "+").replace(":", "-"),
                              fileName,
                              fileDate.replace(":", "-"),
                              gameVersions,
                              releaseType)
