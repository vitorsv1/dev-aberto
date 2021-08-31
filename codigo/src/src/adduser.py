#!/usr/bin/python3
"""Populates user DB"""
import sqlite3
import hashlib


def add_user(user, pwd, type_csv):
    """Connects to database, then add all users in users.csv"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('Insert into USERS(user,pass,type) values("{0}","{1}","{2}");'
                   .format(user, pwd, type_csv))
    conn.commit()
    conn.close()


with open('users.csv', 'r', encoding="UTF-8") as file:
    lines = file.read().splitlines()

for users in lines:
    (username, user_type) = users.split(',')
    print(username)
    print(user_type)
    add_user(username, hashlib.md5(username.encode()).hexdigest(), user_type)
