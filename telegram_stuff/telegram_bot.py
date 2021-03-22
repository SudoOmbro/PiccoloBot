from telegram.ext import Updater, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters

from telegram_stuff.bot_menu_handlers import game_start_handler, in_game_handler, States, end_command_handler, \
    start_command_handler, game_entrypoint_handler, edit_entrypoint_handler, add_dare_handler, edit_dare_menu_handler, \
    edit_dare_attribute_handler, show_all_dares_handler, about_command_handler


class PiccoloBot:

    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)

        game_conversation_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(game_entrypoint_handler, pattern="play")],
            states={
                States.GET_PLAYERS: [MessageHandler(Filters.text, game_start_handler)],
                States.IN_GAME: [CallbackQueryHandler(in_game_handler, pattern="next")]
            },
            fallbacks=[CommandHandler("end", end_command_handler)]
        )

        edit_dares_conversation_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(edit_entrypoint_handler, pattern="edit")],
            states={
                States.MAIN_EDIT_MENU: [CallbackQueryHandler(add_dare_handler, pattern="add"),
                                        CallbackQueryHandler(show_all_dares_handler, pattern="show"),
                                        CallbackQueryHandler(end_command_handler, pattern="back")],
                States.EDIT_DARE_MENU: [CallbackQueryHandler(edit_dare_menu_handler)],
                States.EDIT_DARE_ATTRIBUTE: [MessageHandler(Filters.text, edit_dare_attribute_handler)]
            },
            fallbacks=[CommandHandler("end", end_command_handler)]
        )

        self.updater.dispatcher.add_handler(CommandHandler("start", start_command_handler))
        self.updater.dispatcher.add_handler(CommandHandler("about", about_command_handler))
        self.updater.dispatcher.add_handler(game_conversation_handler)
        self.updater.dispatcher.add_handler(edit_dares_conversation_handler)


    def start(self):
        self.updater.start_polling()
        self.updater.idle()
