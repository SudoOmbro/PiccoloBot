from telegram.ext import Updater, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters

from bot.bot_menu_handlers import game_start_handler, in_game_handler, States, end_command_handler, \
    start_command_handler, game_entrypoint_handler


class Bot:

    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)

        ingame_conversation_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(game_entrypoint_handler, pattern="play")],
            states={
                States.GET_PLAYERS: [MessageHandler(Filters.text, game_start_handler)],
                States.IN_GAME: [CallbackQueryHandler(in_game_handler, pattern="next")]
            },
            fallbacks=[CommandHandler("end", end_command_handler)]
        )

        self.updater.dispatcher.add_handler(CommandHandler("start", start_command_handler))
        self.updater.dispatcher.add_handler(ingame_conversation_handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
