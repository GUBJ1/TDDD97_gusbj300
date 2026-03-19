from flask import Flask, request, jsonify, g
from flask_sock import Sock
import json
import database_helper
import re

app = Flask(__name__)
sock = Sock(app)

@app.route("/")
def root():
    return app.send_static_file("client.html")

signedInUsers={}
userTokens = {}    
userSockets = {}      

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "database", None)
    if db is not None:
        db.close()
        print("DB connection closed")

@sock.route("/ws")
def ws_route(ws):
    token = request.args.get("token")

    if not token or token not in signedInUsers:
        ws.close()
        return

    email = signedInUsers[token]
    userSockets[email] = ws

    try:
        while True:
            data = ws.receive()
            if data is None:
                break
    except Exception as e:
        print("WebSocket error:", e)
    finally:
        if userSockets.get(email) == ws:
            userSockets.pop(email, None)


@app.route("/signIn", methods=["POST"])
def signIn_route():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    result = database_helper.findUserByEmail(email)

    if result is None:
        print("fel mail tihi")
        return {"success": False, "message": "User not found"}, 401
    
    if result["password"] != password:
        print("fel lösen tihi")
        return {"success": False, "message": "Wrong password!"}, 401
    
    old_token = userTokens.get(email)
    old_ws = userSockets.get(email)

    if old_ws:
        old_ws.send(json.dumps({"type": "force_logout"}))

    if old_token:
        signedInUsers.pop(old_token, None)

    token = database_helper.generateToken()
    signedInUsers[token] = email
    userTokens[email] = token

    response = jsonify({"success": True, "message": "Signed in!,"})
    response.headers["Authorization"] = token

    return response, 200

    
@app.route("/signUp", methods=["POST"])
def signUp_route():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    firstName = data.get("firstName")
    familyName = data.get("familyName")
    gender = data.get("gender")
    city = data.get("city")
    country = data.get("country")
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' #kollar mail format

    if None in([email, password, firstName, familyName, gender, city, country]):
        return {"success": False, "message": "Missing input"}
    elif not re.match(emailPattern, email):
        return {"success": False, "message": "Incorrect email format"}
    elif len(password) < 6:
        return {"success": False, "message": "Password is too short"}

    result = database_helper.createUser(email, password, firstName, familyName, gender, city, country)

    if result == False:
        return {"success": False, "message": "Database ERROR!"}, 401
    
    return {"success": True, "message": "User created!"}, 200
    

@app.route("/signOut", methods=["POST"])
def signOut_route():
    token = request.headers.get("Authorization")

    print("token:", token)
    print("inloggaed 2:", signedInUsers)

    email = signedInUsers.pop(token)

    if userTokens.get(email) == token:
        userTokens.pop(email, None)

    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token"}, 401
    
    signedInUsers.pop(token)
    return {"success": True, "message": "Succesfully signed out"}, 200


@app.route("/changePassword", methods=["POST"])
def changePassword_route():
    token = request.headers.get("Authorization")
    data = request.json
    oldPassword = data.get("oldPassword")
    newPassword = data.get("newPassword")

    print("token,",token)
    email = signedInUsers.get(token)

    print("email,",email)
    if email is None:
        return {"success": False, "message": "Token error!"}, 401

    result = database_helper.findUserByEmail(email)

    if result["password"] != oldPassword:
        return {"success": False, "message": "fel lösen"}, 401
    
    if len(newPassword) < 6:
        return {"success": False, "message": "för kort lösen"}, 401
    
    update = database_helper.changePassword(email, newPassword)

    if update == False:
        return {"success": False, "message": "Database ERROR!"}, 401
    
    return {"success": True, "message": "Password Changed!"}, 200
    

@app.route("/getUserDataByToken", methods=["GET"])
def getUserDataByToken_route():
    token = request.headers.get("Authorization")

    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token!"}, 401

    email = signedInUsers.get(token)
    result = database_helper.findUserByEmail(email)

    if result is None:
        return {"success": False, "message": "user not found"}, 401
    

    return jsonify({"success": True, "message": "User found", "data": dict(result)}), 200


@app.route("/getUserDataByEmail", methods=["GET"])
def getUserDataByEmail_route():
    token = request.headers.get("Authorization")
    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token!"}, 401
    
    email = request.args.get("email")
    result = database_helper.findUserByEmail(email)
    
    if result is None:
        return {"success": False, "message": "user not found"}, 401


    return jsonify({"success": True, "message": "User found", "data": dict(result)}), 200


@app.route("/getUserMessageByToken", methods=["GET"])
def getUserMessageByToken():
    token = request.headers.get("Authorization")

    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token!"}, 401
    
    email = signedInUsers.get(token)
    result = database_helper.getUserMsg(email)
    messages = [dict(row) for row in result]

    if result is None:
        return {"success": False, "message": "user not found"}, 401
    
    print(messages)
    return jsonify({"success": True, "message": "User found", "data": messages}), 200

    
@app.route("/getUserMessageByEmail", methods=["GET"])
def getUserMessageByEmail_route():
    token = request.headers.get("Authorization")
    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token!"}, 401

    email = request.args.get("email")
    result = database_helper.getUserMsg(email)
    messages = [dict(row) for row in result]

    if result is None:
        return {"success": False, "message": "user not found"}, 401
    
    print(messages)
    
    return jsonify({"success": True, "message": "User found", "data": messages}), 200


@app.route("/postMessage", methods=["POST"])
def postMessage_route():
    data = request.json
    token = request.headers.get("Authorization")
    if token not in signedInUsers:
        return {"success": False, "message": "Invalid token!"}, 401
    
    email = signedInUsers[token]
    
    message = data.get("message")
    receiver = data.get("receiver")    
    if receiver == None:
        receiver = email
    print("email", email, "message", message, "receiver",receiver)

    if len(message) == 0:
        return {"success": False, "message": "Message is empty"}, 401

    result = database_helper.createMessage(email, receiver, message)

    if result == False:
        return{"success": False, "message": "FEEEEEEL"}, 401
    
    return{"success": True, "message": "yay posted"}, 200

    
if __name__ == "__main__":
    app.run(debug=True)


