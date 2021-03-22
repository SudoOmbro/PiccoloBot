from telegram_stuff.telegram_bot import PiccoloBot
from utils.filesystem import load_json
from utils.globals import Globals


def main():
    settings = load_json("config")
    Globals.admins_list = settings["admins"]
    bot = PiccoloBot(settings["token"])
    bot.start()


if __name__ == '__main__':
    main()
