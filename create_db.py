import sqlite3

conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER, family_id INTEGEr)")
c.execute("CREATE TABLE IF NOT EXISTS families (family_id INTEGER, creator_id INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS invites (user_id INTEGER, family_id INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS bills (bill_id INTEGER, family_id INTEGER, user_id INGEGER, price REAL, message TEXT, date TEXT)")
conn.commit()
conn.close()
