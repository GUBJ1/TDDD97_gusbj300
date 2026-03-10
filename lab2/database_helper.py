from random import random
import sqlite3
from flask import g
import uuid
import re

DATABASE = "database.db"
loggedInUsers = {}

def getDb():
    db = getattr(g, "database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def quit():
    db = getattr(g, "database", None)
    if db is not None:
        db.close()

def signIn(data_json):
    email = data_json.get("username")
    password = data_json.get("password")
    in = getDb().execute("SELECT * FROM users WHERE email=?")