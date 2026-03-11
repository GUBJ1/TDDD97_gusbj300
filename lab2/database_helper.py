import secrets
import string
import sqlite3
from flask import g
import uuid
import re

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


def signIn(data_json):
    email = data_json.get("email")
    password = data_json.get("password")
    cursor = getDb().execute("SELECT email, password FROM users WHERE email=?",(email,))
    user = cursor.fetchone() #fetchone plockar ut en i taget frpn db
    cursor.close()
    if user == None:
        return {"success": False, "message": "User not found."}
    elif user ['password'] != password:
        return {"success": False, "message": "Incorrect password."}
    
    token = generateToken()
    signedInUsers[token] = email

    print("token:", token)
    print("inloggade:", signedInUsers)

    return {"success": True, "message": "Sign in successful.", "data": token}

def signUp (data_json):
    email = data_json.get("email")
    password = data_json.get("password")
    firstName = data_json.get("firstName")
    familyName = data_json.get("familyName")
    gender = data_json.get("gender")
    city = data_json.get("city")
    country = data_json.get("country")
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' #kollar mail format
    if None in([email, password, firstName, familyName, gender, city, country]):
        return {"success": False, "message": "Missing input"}
    elif not re.match(emailPattern, email):
        return {"success": False, "message": "Incorrect email format"}
    elif len(password) < 6:
        return {"success": False, "message": "Password is too short"}
    
    cursor = getDb().execute("SELECT email, password FROM users WHERE email=?",(email,))
    if cursor.fetchone():
        cursor.close()
        return {"success": False, "message": "User already exists"}
    cursor.close()

    getDb().execute("INSERT INTO users (email, password, firstName, familyName, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (email, password, firstName, familyName, gender, city, country))
    getDb().commit()
    return {"success": True, "message": "User created successfully."}


def signOut (token):

    print("token:", token)
    print("inloggaed 2:", signedInUsers)

    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token"}
    
    signedInUsers.pop(token)
    return {"success": True, "message": "Succesfully signed out"}
    



def changePassword(token, data_json):
    oldPassword = data_json.get("oldPassword")
    newPassword = data_json.get("newPassword")
    email = signedInUsers.get(token)
    cursor = getDb().execute("SELECT password FROM users WHERE email=?",(email,)) 

    row = cursor.fetchone()
    cursor.close()

    if row is None: #gamla lösenordet
        return {"success": False, "message": "sus error"}
    
    
    if row["password"] != oldPassword:
        return {"success": False, "message": "Wrong password"}
    
    if len(newPassword) < 6:
        return {"success": False, "message": "Too short password"}
    
    cursor = getDb().execute("UPDATE users SET password=? WHERE email=?", (newPassword, email))

    getDb().commit()
    cursor.close()

    return {"success": True, "message": "Changed!"}


def getUserDataByToken(token):
    email = signedInUsers.get(token)
    cursor = getDb().execute("SELECT * FROM users WHERE email=?",(email,)) 

    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return {"success": False, "message": "User not fund!"}
    
    return {"success": True, "message": "User found!", "data": dict(row)}

        
def getUserDataByEmail(token, email)
    if signedInUsers.get(token) is None:
        return {"success": False, "message": "Token erröör"}
    
    cursor = getDb().execute("SELECT * FROM users WHERE email=?",(email,)) 

    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return {"success": False, "message": "hittar ingen user på mailen"}
    
    return {"success": True, "message": "success!", "data": dict(row)}
    
    
                                            