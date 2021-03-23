from telegram import InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("\U0001F37A New game", callback_data='play')],

])


main_keyboard_admin = InlineKeyboardMarkup([

    [InlineKeyboardButton("\U0001F37A New game", callback_data='play')],
    [InlineKeyboardButton("\U0001F4F1 Settings", callback_data='edit')]

])


ingame_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("\U0001F37A Next turn", callback_data="next")]

])


main_edit_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("add dare", callback_data="add"),
     InlineKeyboardButton("edit dare", callback_data="edit")],
    [InlineKeyboardButton("Show all saved dares", callback_data="show")],
    [InlineKeyboardButton("formatting help", callback_data="help")],
    [InlineKeyboardButton("Back", callback_data="back")]

])


edit_dare_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("edit start text", callback_data="start_text"),
     InlineKeyboardButton("edit end text", callback_data="end_text")],
    [InlineKeyboardButton("edit duration", callback_data="duration"),
     InlineKeyboardButton("edit wiggle", callback_data="wiggle")],
    [InlineKeyboardButton("edit involved players", callback_data="involved_players"),
     InlineKeyboardButton("edit random strings", callback_data="strings")],
    [InlineKeyboardButton("Save & exit", callback_data="save")]

])
