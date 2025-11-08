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