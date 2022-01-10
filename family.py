import sqlite3
from random import randint

import user as usr
from bill import Bill
from datetime import datetime, timedelta

conn = sqlite3.connect("data.db")
c = conn.cursor()

def family_exists(family_id):
    c.execute("SELECT * FROM families WHERE family_id=?", [family_id])
    return len(list(c)) == 1

def create_family(creator_id):
    creator = usr.User(creator_id)
    while True:
        family_id = randint(100000, 999999)
        if not family_exists(family_id):
            break
    c.execute("INSERT INTO families VALUES (?, ?)", [family_id, creator.get_user_id()])
    conn.commit()
    Family(family_id).add_user(creator_id)

class Family:
    def __init__(self, family_id):
        self.__family_id = family_id

    def delete_family(self):
        for user in self.get_user_list():
            self.remove_user(user.get_user_id())
        c.execute("DELETE FROM bills WHERE family_id=?", [self.get_family_id()])
        c.execute("DELETE FROM families WHERE family_id=?", [self.get_family_id()])
        conn.commit()

    def get_family_id(self):
        return int(self.__family_id)

    def __clist(self):
        c.execute("SELECT * FROM families WHERE family_id=?", [self.get_family_id()])
        return list(c)[0]

    def get_user_list(self):
        c.execute("SELECT * FROM users WHERE family_id=?", [self.get_family_id()])
        return list(map(usr.User, [user[0] for user in list(c)]))

    def add_user(self, user_id):
        c.execute("UPDATE users SET family_id=? WHERE user_id=?", [self.get_family_id(), user_id])
        conn.commit()
        
    def remove_user(self, user_id):
        c.execute("UPDATE users SET family_id=? WHERE user_id=?", [None, user_id])
        conn.commit()
        if not self.get_user_list() or user_id == self.get_creator().get_user_id():
            self.delete_family()

    def get_creator(self):
        return usr.User(self.__clist()[1])

    def get_bills(self, user_id=None):
        if user_id:
            user = usr.User(user_id)
            c.execute("SELECT * FROM bills WHERE family_id=? AND user_id=?", [self.get_family_id(), user_id])
        else:
            c.execute("SELECT * FROM bills WHERE family_id=?", [self.get_family_id()])
        return list(map(Bill, [bill[0] for bill in list(c)]))

    def get_bills_30_days(self, user_id=None):
        approved_bill_list = list()
        date_last_month = datetime.now() - timedelta(days=30)
        for bill in self.get_bills(user_id)[::-1]:
            if bill.get_date() > date_last_month:
                approved_bill_list.append(bill)
            else:
                break
        return approved_bill_list
    
    def get_total_30_days(self, user_id=None):
        total = 0
        for bill in self.get_bills_30_days(user_id):
            total += bill.get_price()
        return total

