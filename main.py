from bot.bot import Bot
from utils.filesystem import load_json


def main():
    settings = load_json("config")
    bot = Bot(settings["token"])
    bot.start()


if __name__ == '__main__':
    main()
