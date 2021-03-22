from telegram import InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("New game", callback_data='play')],

])


main_keyboard_admin = InlineKeyboardMarkup([

    [InlineKeyboardButton("\U0001F37A New game", callback_data='play')],
    [InlineKeyboardButton("\U0001F4F1 Settings", callback_data='setting')]

])


ingame_keyboard = InlineKeyboardMarkup([

    [InlineKeyboardButton("\U0001F37A Next turn", callback_data="next")]

])
