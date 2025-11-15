import sqlite3

db = "db.db"
conn = sqlite3.connect(db, check_same_thread=False)
cur = conn.cursor()

"""
	"Малое зелье лечения": {
		"attribute": "hp",
		"value": 10,
	},
"""

def get_item(item):
	cur.execute("SELECT * FROM equipment WHERE item_name = ?", (item,))
	r = cur.fetchall()
	r = r[0]

	if r:
		result = {
			"item_name": r[1],
			"attribute": r[3],
			"value": r[2]
		}

		return result
	else:
		return {}

def add_user(user_id, user_state):
	"""
	user_state = {
		"step": "awaiting_name",
		"player": {
			"name": "",
			"hp": 100,
			"armor": 0,
			"strenght": 0,
			"agility": 0,
			"charisma": 0,
			"intellect": 0,
			"inventory": [],
			"last_free_item_time": 0,
			"roll_count": 0
		}
	}
	"""
	ins = """
		INSERT INTO 
		users (user_id, step, name, hp, armor, strenght, 
			agility, charisma, intellect, inventory,
			last_free_item_time, roll_count) 
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
	"""

	inventory = ",".join(user_state["player"]["inventory"])

	data = (
		user_id,
		user_state["step"],
		user_state["player"]["name"],
		user_state["player"]["hp"],
		user_state["player"]["armor"],
		user_state["player"]["strenght"],
		user_state["player"]["agility"],
		user_state["player"]["charisma"],
		user_state["player"]["intellect"],
		inventory,
		user_state["player"]["last_free_item_time"],
		user_state["player"]["roll_count"],
	)

	if not user_id in get_all_username():
		cur.execute(ins, data)
		conn.commit()

def get_all_username():
	cur.execute("SELECT user_id FROM users")
	result = cur.fetchall()

	return [i[0] for i in result]

def get_user(user_id):
	cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
	result = cur.fetchall()

	user_state = {
		result[0][0]: {
			"step": result[0][1],
			"player": {
				"name": result[0][2],
				"hp": result[0][3],
				"armor": result[0][4],
				"strenght": result[0][5],
				"agility": result[0][6],
				"charisma": result[0][7],
				"intellect": result[0][8],
				"inventory": result[0][9].split(),
				"last_free_item_time": result[0][10],
				"roll_count": result[0][11]
			}
		}
	}

	return user_state

def update_data(user_id, user_state):

	inventory = ",".join(user_state["player"]["inventory"])
	data = (
		user_state["step"],
		user_state["player"]["name"],
		user_state["player"]["hp"],
		user_state["player"]["armor"],
		user_state["player"]["strenght"],
		user_state["player"]["agility"],
		user_state["player"]["charisma"],
		user_state["player"]["intellect"],
		inventory,
		user_state["player"]["last_free_item_time"],
		user_state["player"]["roll_count"],
		user_id,
	)


	cur.execute(
		"""
		UPDATE users 
        SET step = ?, 
            name = ?, 
            hp = ?, 
            armor = ?, 
            strenght = ?, 
            agility = ?, 
            charisma = ?, 
            intellect = ?, 
            inventory = ?,
            last_free_item_time = ?, 
            roll_count = ?
        WHERE user_id = ?
		""", 
		data
	)
	conn.commit()