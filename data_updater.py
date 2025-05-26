import config
from datetime import datetime
import PyTaskbar
import aiohttp
import asyncio
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from rich.progress import Progress
from urllib3 import disable_warnings as urllib3_disable_warnings
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Import custom downloader module
from mod_downloader import download_mod_metadata
import time

config = config.Config()
DATABASE_PATH = config.DATABASE_PATH
download_enable = config.download_enable
POOL_SIZE = config.POOL_SIZE

# Set request headers
headers = config.headers

# Ignore urllib3 warnings
urllib3_disable_warnings()
# Define fill colors
green_fill = PatternFill(patternType='solid', fgColor='90EE90')  # Light green
red_fill = PatternFill(patternType='solid', fgColor='D94600')  # Red
blue_fill = PatternFill(patternType='solid', fgColor='A0C4FF')  # Light blue

# Initialize global variables
max_rowFIX = unmatchedSum = matchedSum = 0
DuplicatesList = []
processesTime = datetime.now()
validify_processesTime = str(processesTime).replace(" ", "+").replace(":", "-")

# Check if DATABASE_PATH environment variable is set
if not DATABASE_PATH:
    raise Exception('DATABASE_PATH environment variable not set.')

# Load Excel workbook
wb = load_workbook(DATABASE_PATH)
exl = wb.active

# Initialize taskbar progress bar
prog = PyTaskbar.Progress()
prog.init()
prog.setState('loading')


# Get Excel cell value by column and row
def Vexl(column, row):
    return exl[f"{column}{row}"].value


# Update time information
def time_update(type: str, row, time):
    Row_Str = str(row)
    if type == "Latest":
        exl["H" + Row_Str] = Vexl("G", row)
        exl["G" + Row_Str] = Vexl("F", row)
        exl["F" + Row_Str] = str(time)
    elif type == "Json":
        exl["L" + Row_Str] = Vexl("K", row)
        exl["K" + Row_Str] = Vexl("J", row)
        exl["J" + Row_Str] = str(time)


# Check for duplicates
def check_duplicates(num_id):
    if Vexl("F", num_id) != Vexl("G", num_id):
        exl[f"F{num_id}"].fill = red_fill
        return False
    else:
        exl[f"F{num_id}"].fill = green_fill
        return True


# Get max row count from Excel
for max_rowFIX, row in enumerate(exl, 1):
    if all(c.value is None for c in row):
        break
max_rowFIX -= 2


# Get Curseforge project API JSON data
async def get_cfwidget_api_json_async(cf_project_id, session):
    retry_count = 0
    max_retries = config.TIMEOUT_RETRY

    while retry_count < max_retries:
        try:
            async with session.get(f'https://api.cfwidget.com/{cf_project_id}',
                                   headers=headers, ssl=False, timeout= 420) as response:
                return await response.json()
        except aiohttp.ClientResponseError as e:
            # Handle specific HTTP errors
            if e.status == 404:
                return {"files": []}
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Error getting Curseforge data for {cf_project_id} after {max_retries} attempts: {e}")
                return {"files": []}
            else:
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"Attempt {retry_count} failed for {cf_project_id}, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)


# Get Modrinth project API JSON data
async def get_modrinth_api_json_async(mr_project_id, session):
    retry_count = 0
    max_retries = config.TIMEOUT_RETRY

    while retry_count < max_retries:
        try:
            async with session.get(f'https://api.modrinth.com/v2/project/{mr_project_id}',
                                   headers=headers, ssl=False, timeout= 420) as response:
                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return {"files": [], "error": "不存在"}
        except Exception as e:
            if "Expecting value: line 1 column 1 (char 0)" in str(e):
                return {"versions": [], "updated": "不存在"}
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Error getting Modrinth data for {mr_project_id} after {max_retries} attempts: {e}")
                return {"versions": [], "updated": ""}
            else:
                wait_time = 2 ** retry_count  # Exponential backoff
                print(
                    f"Attempt {retry_count} failed for {mr_project_id} because {e}, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)


def add_unreachable_mod_to_blacklist(row: int):
    """Check if the mod name is in the blacklist."""
    # 如果F、G、H列均为“读取失败”，则列入黑名单
    if Vexl("F", row) == "读取失败" and Vexl("G", row) == "读取失败" and Vexl("H", row) == "读取失败":
        mod_name = Vexl("C", row)
        if mod_name not in config.blacklist:
            config.blacklist.append(mod_name)
            print(f"检测到多次读取{mod_name}失败，其将列入检测黑名单")
            config.write_config("blacklist", config.blacklist)
            # 给涂上蓝色
            exl[f"F{row}"].fill = blue_fill


async def process_mod_async(num_id, session, progress, task):
    mod_name = Vexl("C", num_id)
    latest_time = ""
    file_ids = []

    try:
        curseforge_id = Vexl("D", num_id)
        modrinth_id = Vexl("E", num_id)

        if curseforge_id is not None:
            website = "Curseforge"
            if not str(curseforge_id).count("/"):
                json_data = await get_cfwidget_api_json_async(curseforge_id, session)
                if 'files' in json_data and json_data['files']:
                    file_ids = [i["id"] for i in json_data['files']]
                    latest_time = str(dict(json_data['files'][0])['uploaded_at'])
                else:
                    raise ValueError("获取Curseforge数据为空")
            else:
                latest_time = ""
                for m in str(curseforge_id).split("/"):
                    json_data = await get_cfwidget_api_json_async(m, session)
                    if 'files' in json_data and json_data['files']:
                        file_ids += [i["id"] for i in json_data['files']]
                        latest_time += str(dict(json_data['files'][0])['uploaded_at']) + "  "
                    else:
                        raise ValueError("获取Curseforge数据为空")

        elif modrinth_id is not None:
            website = "Modrinth"
            if not str(modrinth_id).count("/"):
                json_data = await get_modrinth_api_json_async(modrinth_id, session)
                if json_data:
                    file_ids = json_data["versions"]
                    latest_time = str(json_data['updated'])
                else:
                    raise ValueError("获取Modrinth数据为空")
            else:
                latest_time = ""
                for m in str(modrinth_id).split("/"):
                    json_data = await get_modrinth_api_json_async(m, session)
                    if json_data:
                        file_ids += json_data["versions"]
                        latest_time += str(json_data['updated']) + "  "
                    else:
                        raise ValueError("获取Modrinth数据为空")
        else:
            latest_time = "读取失败"
            if config.blacklist_enabled:
                add_unreachable_mod_to_blacklist(num_id)

            website = None

        # Update time and check for duplicates
        time_update("Latest", num_id, latest_time)
        time_update("Json", num_id, file_ids)
        matched = check_duplicates(num_id)

        return {
            "num_id": num_id,
            "mod_name": mod_name,
            "latest_time": latest_time,
            "file_ids": file_ids,
            "website": website if 'website' in locals() else None,
            "id": curseforge_id or modrinth_id,
            "matched": matched
        }

    except Exception as err:
        print(f"{num_id - 1} {mod_name} 出现错误:{err}，跳过该项")
        return {
            "num_id": num_id,
            "mod_name": mod_name,
            "latest_time": "读取过程出现错误",
            "file_ids": "",
            "matched": False
        }
    finally:
        # Update progress regardless of success or failure
        progress.update(task, advance=1, description=f"[yellow]f[ {num_id - 1}/{max_rowFIX} ]处理中...")
        prog.setProgress(int(round(num_id * 100 / max_rowFIX, 0)))


# Modified download function to be async
async def download_mod_metadata_async(website, mod_type, time_str, mod_id, file_ids):
    # You'll need to modify your download_mod_metadata function to be async
    # or use a thread executor if it must remain synchronous
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, download_mod_metadata, website, mod_type, time_str, mod_id, file_ids
    )


# Process latest uploaded mod information
async def latest_upload_async():
    global DuplicatesList, matchedSum, unmatchedSum
    matchedSum = unmatchedSum = 0

    with Progress() as progress:
        task = progress.add_task("[red]正在初始化......", total=max_rowFIX)

        # Create connection limit to avoid overwhelming servers
        connector = aiohttp.TCPConnector(limit=POOL_SIZE, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create a list of tasks
            tasks = []
            for num_id in range(2, max_rowFIX + 2):
                if config.blacklist_enabled and Vexl("C", num_id) not in config.blacklist:
                    tasks.append(process_mod_async(num_id, session, progress, task))

            # Execute all tasks concurrently with gather
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    print(f"Task failed with exception: {result}")
                    continue

                try:
                    if not result["matched"] and result['latest_time'] != "读取过程出现错误":
                        DuplicatesList.append(
                            f"{result['num_id']}: {result['mod_name']} || {result['latest_time']} | {Vexl('G', result['num_id'])}")
                        unmatchedSum += 1

                        if download_enable and 'website' in result and result['website']:
                            num_id = result['num_id']
                            # Look for most recent valid list as pastJson
                            pastJson = None
                            try:
                                if not (isinstance(eval(Vexl("K", num_id)), list)):
                                    pastJson = Vexl("K", num_id)
                                elif not (isinstance(eval(Vexl("L", num_id)), list)):
                                    pastJson = Vexl("L", num_id)
                                elif not (isinstance(eval(Vexl("J", num_id)), list)):
                                    pastJson = Vexl("J", num_id)
                            except:
                                pastJson = None

                            if pastJson:
                                try:
                                    fileID = list(set(result['file_ids']).difference(set(eval(pastJson))))
                                    if fileID:
                                        await download_mod_metadata_async(
                                            result['website'],
                                            Vexl("B", num_id),
                                            validify_processesTime,
                                            result['id'],
                                            fileID
                                        )
                                except Exception as e:
                                    print(f"Error processing file differences: {e}")
                    else:
                        matchedSum += 1

                except Exception as e:
                    print(f"Error processing result: {e}")

        progress.update(task, advance=0, description="[green][ √ ]已完成处理！")


# Main execution function
async def main():
    # Initialize time updates
    time_update("Latest", 1, processesTime)
    time_update("Json", 1, processesTime)

    # Report blacklist status
    if config.blacklist_enabled:
        if isinstance(config.blacklist, list):
            blacklisted_count = len(config.blacklist)
        else:
            config.blacklist = list()
            blacklisted_count = 0
        if blacklisted_count > 0:
            print(f"当前有 {blacklisted_count} 个模组在黑名单中，这些模组将被跳过处理")

    # Start processing latest uploaded mod information
    await latest_upload_async()

    # Print summary information
    print(f"匹配：{matchedSum}，不匹配：{unmatchedSum}")
    print(datetime.now(), "完成遍历")
    if DuplicatesList:
        print(f"发现已更新的模组：\n {DuplicatesList}")
        config.write_config("LastModified", str(datetime.now()))
        config.write_config("Finished_upload", False)
    else:
        print("没有发现已更新的模组")

    # Save Excel file
    try:
        wb.save(DATABASE_PATH)
        print("所有改动已成功保存")
    except Exception as E:
        new_path = DATABASE_PATH.replace(".xlsx", f"_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        print("保存出错: {0}\n 将保存至新文件{1}".format(E, new_path))
        wb.save(new_path)

    # Update taskbar status
    prog.setState('done')


# Run the async main function
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()