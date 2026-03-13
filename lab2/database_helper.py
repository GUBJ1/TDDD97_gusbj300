import secrets
import string
import sqlite3
from flask import g
import uuid


DATABASE = "database.db"
signedInUsers = {}

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

def quit():
    db = getattr(g, "database", None)
    if db is not None:
        db.close()


def findUserByEmail(email):
    cursor = getDb().execute("SELECT * FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    cursor.close()
    return row

def createUser(email, password, firstName, familyName, gender, city, country):
    try:
        getDb().execute("INSERT INTO users (email, password, firstName, familyName, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (email, password, firstName, familyName, gender, city, country))
        getDb().commit()

        return True
    except Exception as e:
        print("Database error:", e)
        return False


def signOut (token):

    print("token:", token)
    print("inloggaed 2:", signedInUsers)

    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token"}
    
    signedInUsers.pop(token)
    return {"success": True, "message": "Succesfully signed out"}
    

def changePassword(email, newPassword):
    try:
        cursor = getDb().execute("UPDATE users SET password=? WHERE email=?",(newPassword, email))
        getDb().commit()
        row = cursor.fetchone()
        cursor.close()
    
        return True
    except Exception as e:
        print("Database error:", e)
        return False


def getUserDataByToken(token):
    email = signedInUsers.get(token)
    cursor = getDb().execute("SELECT * FROM users WHERE email=?",(email,)) 
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return {"success": False, "message": "User not fund!"}
    
    return {"success": True, "message": "User found!", "data": dict(row)}

        
def getUserDataByEmail(token, email):

    print("EMAIL:", repr(email))

    if signedInUsers.get(token) is None:
        return {"success": False, "message": "Token erröör"}
    
    cursor = getDb().execute("SELECT * FROM users WHERE email=?",(email,)) 
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return {"success": False, "message": "hittar ingen user på mailen"}
    
    return {"success": True, "message": "success!", "data": dict(row)}
    

def getUserMessageByToken(token):

    email = signedInUsers.get(token)
    cursor = getDb().execute("SELECT message FROM messages WHERE sender=?",(email,))
    rows = cursor.fetchall()
    cursor.close()

    messages = [dict(row) for row in rows]

    if email is None:
        return {"success": False, "message": "Incorrect token"}
    
    return {"success": True, "message": "yay found message", "data": messages}


def getUserMessageByEmail(token, email):

    if signedInUsers.get(token) is None:
        return {"success": False, "message": "Token erröör"}
    
    cursor = getDb().execute("SELECT message FROM messages WHERE sender=?",(email,))
    rows = cursor.fetchall()
    cursor.close()

    messages = [dict(row) for row in rows]

    
    return {"success": True, "message": "yay found message", "data": messages}

    
def postMessage(token, data_json):
        
    if signedInUsers.get(token) is None:
        return {"success": False, "message": "Token erröör"}
    
    message = data_json.get("message")
    sender = signedInUsers.get(token)
    reciever = data_json.get("wall")

    if len(message) == 0:
        return {"success": False, "message": "Cant post empty message"}

    cursor = getDb().execute("SELECT email FROM users WHERE email=?",(reciever,))
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return {"success": False, "message": "User doesnt exist :("}
    
    
    cursor = getDb().execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",(sender, reciever, message))
    getDb().commit()
    cursor.close()

    return {"success": True, "message": "posted to wall"}


    


                                            