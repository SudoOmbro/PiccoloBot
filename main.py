from bot.bot import Bot
from utils.filesystem import load_json
from utils.globals import Globals


def main():
    settings = load_json("config")
    Globals.admins_list = settings["admins"]
    bot = Bot(settings["token"])
    bot.start()


if __name__ == '__main__':
    main()
