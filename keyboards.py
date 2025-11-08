import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_roll_attributes():
	keyboard = InlineKeyboardMarkup()

	strenght_button = InlineKeyboardButton("Бросить на силу", callback_data="roll_strenght")
	agility_button = InlineKeyboardButton("Бросить на ловкость", callback_data="roll_agility")
	charisma_button = InlineKeyboardButton("Бросить на харизму", callback_data="roll_charisma")
	intellect_button = InlineKeyboardButton("Бросить на интеллект", callback_data="roll_intellect")

	keyboard.add(strenght_button, agility_button)
	keyboard.add(charisma_button, intellect_button)

	return keyboard

def main_menu_kb():
	keyboard = InlineKeyboardMarkup()

	strenght_button = InlineKeyboardButton("Стастистика", callback_data="pass")
	
	free_btn = InlineKeyboardButton("Бесплатный предмет", callback_data="free_item")
	road = InlineKeyboardButton("В путь", callback_data="start_road")

	keyboard.add(strenght_button)
	keyboard.add(free_btn)
	keyboard.add(road)

	return keyboard
