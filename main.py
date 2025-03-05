import config

config = config.config

if config.Zmail_enable:
    import ZmailOut
else:
    import Data_updater

if config.Selenium_enable:
    if config.download_enable:
        import update_to_website
    else:
        raise Exception("You need to set download_enable to True to use Selenium. Check your config file.")

