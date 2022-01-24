import sqlite3
from random import randint
from datetime import datetime, timedelta
import user as usr

conn = sqlite3.connect("data.db")
c = conn.cursor()

SERVER_TIMEZONE_HOUR_DIFFERENCE = 3


def bill_exists(bill_id):
    c.execute("SELECT * FROM bills WHERE bill_id=?", [bill_id])
    return len(list(c)) == 1


def create_bill(family_id, user_id, price, message):
    while True:
        bill_id = randint(100000, 999999)
        if not bill_exists(bill_id):
            break
    c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?)", [bill_id, family_id, user_id, price, message, (datetime.now() + timedelta(hours=SERVER_TIMEZONE_HOUR_DIFFERENCE)).strftime("%Y-%m-%d %H:%M:%S")])
    conn.commit()
    return Bill(bill_id)


class Bill:
    def __init__(self, bill_id):
        self.__bill_id = bill_id

    def get_bill_id(self):
        return self.__bill_id

    def __clist(self):
        c.execute("SELECT * FROM bills WHERE bill_id=?", [self.get_bill_id()])
        return list(c)[0]

    def get_family_id(self):
        return self.__clist()[1]

    def get_user(self):
        return usr.User(self.__clist()[2])
    
    def get_price(self):
        return self.__clist()[3]

    def get_message(self):
        return self.__clist()[4]
    
    def get_date_string(self):
        return self.__clist()[5]

    def get_date(self):
        return datetime.now().strptime(self.__clist()[5], "%Y-%m-%d %H:%M:%S")
        


def get_bill_list():
    c.execute("SELECT * FROM bills")
    return list(map(Bill, [bill[0] for bill in list(c)]))
