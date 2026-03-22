import secrets
import string
import sqlite3
from flask import g
import uuid


DATABASE = "database.db"


def getDb():
    db = getattr(g, "database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def generateToken(length=32):
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token

def storeToken(email, token):
    try:
        getDb().execute("INSERT INTO tokens (token, email) VALUES (?, ?)",(token, email))
        getDb().commit()

        return True
    except Exception as e:
        print("Database error", e)
        return False

def deleteToken(token):
    try:
        getDb().execute("DELETE FROM tokens WHERE token=?", (token,))
        getDb().commit()
        return True
    
    except Exception as e:
        print ("DATABASE ERROR")
        return False

def deleteTokenByEmail(email):
    try:
        getDb().execute("DELETE FROM tokens WHERE email=?",(email,))
        getDb().commit()
        return True

    except Exception as e:
        print("Database error", e)
        return False

def getEmailByToken(token):
    try:
        cursor = getDb().execute("SELECT email FROM tokens WHERE token = ?",(token,))
        row = cursor.fetchone()
        return row["email"]

    except Exception as e:
        print ("DATABASE ERROR", e)
        return False

def quit():
    db = getattr(g, "database", None)
    if db is not None:
        db.close()



def createUser(email, password, firstName, familyName, gender, city, country):
    try:
        getDb().execute("INSERT INTO users (email, password, firstName, familyName, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (email, password, firstName, familyName, gender, city, country))
        getDb().commit()

        return True
    except Exception as e:
        print("Database error:", e)
        return False


def changePassword(email, newPassword):
    try:
        cursor = getDb().execute("UPDATE users SET password=? WHERE email=?",(newPassword, email))
        getDb().commit()
        changed = cursor.rowcount
        cursor.close()

        if changed == 0:
            return False
        return True
    except Exception as e:
        print("database error :", e)
        return False


def findUserByEmail(email):
    try:
        cursor = getDb().execute("SELECT * FROM users WHERE email=?", (email,))
        row = cursor.fetchone()
        cursor.close()

        return row
    except Exception as e:
        print("Database error:", e)
        return False


def getUserMsg(email):
    try:
        cursor = getDb().execute("SELECT * FROM messages WHERE receiver=?",(email,)) 
        rows = cursor.fetchall()
        cursor.close()

        return rows
    except Exception as e:
        print("Database error:", e)
        return False


def createMessage(email, receiver, message):
    try:
        getDb().execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",(email, receiver, message))
        getDb().commit()

        return True
    except Exception as e:
        print("Database error:", e)
        return False
    


    


                                            