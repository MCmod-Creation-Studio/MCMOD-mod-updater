import config

config = config.config

if config.Zmail_enable:
    import ZmailOut
else:
    import Data_updater

if config.Selenium_enable:
    if config.download_enable:
        if not config.Finished_upload:
            print("Selenium 已启用，开始上传")
            import update_to_website
        else:
            print("没有需要上传的文件")
    else:
        raise Exception("You need to set download_enable to True to use Selenium. Check your config file.")

