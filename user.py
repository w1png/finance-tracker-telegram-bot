import sqlite3
from family import Family

conn = sqlite3.connect("data.db")
c = conn.cursor()

def user_exists(user_id):
    c.execute("SELECT * FROM users WHERE user_id=?", [user_id])
    return len(list(c)) == 1

def create_user(user_id):
    c.execute("INSERT INTO users VALUES (?, ?)", [user_id, None])
    conn.commit()

class User:
    def __init__(self, user_id):
        self.__user_id = user_id

        if not user_exists(self.get_user_id()):
            create_user(self.get_user_id())

    def get_user_id(self):
        return int(self.__user_id)

    def __clist(self):
        c.execute("SELECT * FROM users WHERE user_id=?", [self.get_user_id()])
        return list(c)[0]

    def is_in_family(self):
        return bool(self.__clist()[1])
    
    def get_family(self):
        return Family(self.__clist()[1])

    def create_invite(self, family_id):
        c.execute("INSERT INTO invites VALUES (?, ?)", [self.get_user_id(), family_id])
        conn.commit()

    def get_invites(self):
        c.execute("SELECT * FROM invites WHERE user_id=?", [self.get_user_id()])
        return [invite[1] for invite in list(c)]

    def is_invited(self, family_id):
        c.execute("SELECT * FROM invites WHERE family_id=?", [family_id])
        return len(list(c)) == 1

    def delete_invite(self, family_id):
        c.execute("DELETE FROM invites WHERE family_id=?", [family_id])
        conn.commit()
        

