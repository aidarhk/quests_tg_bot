import os
import time
import random

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.util import quick_markup

from config import token
from templates import *
from keyboards import make_roll_attributes, main_menu_kb
from database import *

bot = telebot.TeleBot(token=token)

user_state = {}

WAIT_TIME = 1 * 60 * 60 

@bot.message_handler(commands=["start"])
def start_cmd(message):
	chat_id = message.chat.id

	gif_path = os.path.join("static", "gif", "start.gif")
	if os.path.exists(gif_path):
		with open(gif_path, "rb") as gif_file:
			bot.send_animation(
				chat_id=chat_id,
				animation=gif_file,
				caption="Утро. Ты открываешь глаза и не понимаешь где ты. Как тебя зовут?"
			)
	else:
		bot.send_message(
			chat_id=chat_id,
			text="Утро. Ты открываешь глаза и не понимаешь где ты. Как тебя зовут?"
		)

	user_state[chat_id] = {
		"step": "awaiting_name",
		"player": player.copy()
	}

@bot.callback_query_handler(func=lambda call: call.data == "free_item")
@bot.message_handler(commands=["free_item"])
def free_item(message):
	try:
		user_id = message.chat.id
	except:
		user_id = message.message.chat.id

	current_time = time.time()
	last = user_state[user_id]["player"]["last_free_item_time"]

	if current_time - last >= WAIT_TIME:
		user_state[user_id]["player"]["last_free_item_time"] = current_time
		# здесь устроим подключение к бд
		potion = get_item("Малое зелье лечения")
		if potion:
			user_state[user_id]["player"]["inventory"].append(potion)
			bot.send_message(
				chat_id=user_id, 
				text="Вы получили бесплатное зелье лечения!"
			)
	else:
		remainig_time = WAIT_TIME - (current_time - last)
		bot.send_message(
			chat_id=user_id,
			text=(f"Вы сможете получить бесплатное зелье через {remainig_time // 3600} часов"
				f"{(remainig_time % 3600) // 60} минут {remainig_time % 60} секунд")
		)

@bot.message_handler(commands=["main_menu"])
def main_menu(message):
	user_id = message.chat.id

	player = user_state[user_id]["player"]

	text = (f"Персонаж {player["name"]}\n\n"
		f"Характеристики: \n"
		f"❤️ {player["hp"]}\n"
		f"🛡 {player["armor"]}\n"
		f"💪 {player["strenght"]}\n"
		f"🏃 {player["agility"]}\n"
		f"🗣 {player["charisma"]}\n"
		f"🧠 {player["intellect"]}\n"
		f"🎒 {player["inventory"]}"
		)

	bot.send_message(
		chat_id=user_id,
		text=text,
		reply_markup=main_menu_kb()
	)


@bot.callback_query_handler(func=lambda call: call.data.startswith("roll_"))
def handle_roll_buttons(call):
	chat_id = call.message.chat.id


	if (user_state[chat_id]["player"]["strenght"] != 0 
		and user_state[chat_id]["player"]["agility"] != 0
		and user_state[chat_id]["player"]["charisma"] != 0
		and user_state[chat_id]["player"]["intellect"] != 0):

		bot.send_message(
			chat_id=chat_id,
			text=f"Все характеристики определены!"
		)
		return

	attributes = call.data.split("_")[-1]

	dice_message = bot.send_dice(
		chat_id=chat_id,
		emoji="🎲"
	)

	time.sleep(5)

	dice_message = dice_message.dice.value

	if attributes == "strenght":
		user_state[chat_id]["player"]["strenght"] = dice_message
		text = f"Твоя сила растёт! Теперь твоя сила: {dice_message}"
	elif attributes == "agility":
		user_state[chat_id]["player"]["agility"] = dice_message
		text = f"Твоя ловкость растёт! Теперь твоя ловкость: {dice_message}"
	elif attributes == "charisma":
		user_state[chat_id]["player"]["charisma"] = dice_message
		text = f"Твоя харизма растёт! Теперь твоя харизма: {dice_message}"
	elif attributes == "intellect":
		user_state[chat_id]["player"]["intellect"] = dice_message
		text = f"Твой интеллект растёт! Теперь твой интеллект: {dice_message}"

	bot.send_message(
		chat_id=chat_id,
		text=text
	)

	user_state[chat_id]["player"]["roll_count"] += 1
	if user_state[chat_id]["player"]["roll_count"] == 4:
		main_menu(call.message)

# Функция для расчета урона
def calculate_damage(attacker_strength, defender_armor):
	damage = attacker_strength - defender_armor
	return damage if damage > 0 else 0

# Инициализация боя
def init_battle(hero, enemy, chat_id):
	markup = quick_markup({'💥Удар💥': {'callback_data': 'attack'}}, row_width=1)

	stats_message = bot.send_message(chat_id=chat_id,
									 text=f"🥷🏼 {hero['name']} (HP: {hero['hp']}) vs 👹 {enemy['name']} (HP: {enemy['hp']})",
									 reply_markup=markup)

	user_state[chat_id]['stats_message'] = stats_message


# Обработка нажатия кнопки "Удар"
@bot.callback_query_handler(func=lambda call: call.data == 'attack')
def attack(call):
	chat_id = call.message.chat.id
	user_id = chat_id

	markup = quick_markup({'💥Удар💥': {'callback_data': 'attack'}}, row_width=1)

	stats_message = user_state[chat_id]['stats_message']

	# Определяем героя
	hero = user_state[user_id]['player']

	enemy = user_state[user_id]['enemy']

	# Моделируем бросок кубика для атаки
	dice_message = bot.send_dice(chat_id)

	# После анимации кубика нужно вычислить урон
	damage_to_enemy = calculate_damage(dice_message.dice.value + hero['strenght'], enemy['armor'])
	enemy["hp"] -= damage_to_enemy

	time.sleep(5)

	bot.send_message(chat_id=user_id,
					 text=f"{hero['name']} наносит {damage_to_enemy} урона {enemy['name']}.")

	if enemy["hp"] <= 0:
		enemy["hp"] = 0
		bot.send_message(chat_id, f"{hero['name']} победил {enemy['name']}!")

		# Удаляем информацию о противнике
		del user_state[user_id]['enemy']

		# Удаляем сообщение о статистике
		del user_state[chat_id]['stats_message']
	else:
		damage_to_hero = calculate_damage(enemy["strenght"], hero['armor'])
		hero['hp'] -= damage_to_hero
		bot.send_message(chat_id, f"{enemy['name']} наносит {damage_to_hero} урона {hero['name']}.")

		if hero['hp'] <= 0:
			hero['hp'] = 0
			bot.send_message(chat_id, f"{enemy['name']} победил {hero['name']}!")

			# Удаляем информацию о противнике
			del user_state[user_id]['enemy']

			# Удаляем сообщение о статистике
			del user_state[chat_id]['stats_message']

	# Обновляем текст сообщения с учетом урона
	bot.edit_message_text(chat_id=chat_id,
						  message_id=stats_message.message_id,
						  text=f"{hero['name']} (HP: {hero['hp']}) vs {enemy['name']} (HP: {enemy['hp']})",
						  reply_markup=markup)


@bot.message_handler(commands=['fight'])
def start_battle(message):
	user_id = message.chat.id
	hero = user_state[user_id]['player']
	enemy = random.choice(enemies)
	user_state[user_id]['enemy'] = enemy
	init_battle(hero, enemy, message.chat.id)


@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id]["step"] == "awaiting_name")
def set_character_name(message):
	print("set_character_name")
	chat_id = message.chat.id
	name = message.text

	user_state[chat_id]["player"]["name"] = name
	user_state[chat_id]["step"] = "awaiting_attributes"

	bot.send_message(
		chat_id=chat_id,
		text="Великий бог рандома дал вам выбор. Вы можете повлияеть на свои характеристики. Выберите испытание:",
		reply_markup=make_roll_attributes()
	)

bot.infinity_polling()
