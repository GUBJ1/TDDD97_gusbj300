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
    email = database_helper.getEmailByToken(token)

    if not token or email is None:
        ws.close()
        return

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

    if not data:
        return {"message": "missing input"}, 400

    if result is None:
        return {"success": False, "message": "User not found"}, 401
    
    if result["password"] != password:
        return {"success": False, "message": "Wrong password!"}, 401

    if email in userSockets:
        old_ws = userSockets[email]
        old_ws.send(json.dumps({"type": "force_logout"}))

    token = database_helper.generateToken()
    print("token", token)

    database_helper.deleteTokenByEmail(email) #tar bort gamla
    database_helper.storeToken(email, token)

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
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    existing = database_helper.findUserByEmail(email)

    if None in([email, password, firstName, familyName, gender, city, country]):
        return {"success": False, "message": "Missing input"}, 400
    elif not re.match(emailPattern, email):
        return {"success": False, "message": "Incorrect email format"}, 400
    elif len(password) < 6:
        return {"success": False, "message": "Password is too short"}, 400
    if existing is not None:
        return {"message": "user_exists"}, 409

    result = database_helper.createUser(email, password, firstName, familyName, gender, city, country)

    if result == False:
        return {"success": False, "message": "Database ERROR!"}, 500
    
    return {"success": True, "message": "User created!"}, 201
    

@app.route("/signOut", methods=["POST"])
def signOut_route():
    token = request.headers.get("Authorization")

    if not token:
        return {"success": False, "message": "Missing token"}, 400
    
    email = database_helper.getEmailByToken(token)

    if email is None:
        return {"message": "invalid token"}, 401

    success = database_helper.deleteToken(token)

    if not success:
        return {"success": False, "message": "Failed to delete token"}, 500

    return {"success": True, "message": "Successfully signed out"}, 200


@app.route("/changePassword", methods=["POST"])
def changePassword_route():
    token = request.headers.get("Authorization")
    data = request.json
    oldPassword = data.get("oldPassword")
    newPassword = data.get("newPassword")

    email = database_helper.getEmailByToken(token)

    if email is None:
        return {"success": False, "message": "Token error!"}, 401

    result = database_helper.findUserByEmail(email)

    if result["password"] != oldPassword:
        return {"success": False, "message": "Wrong old password"}, 400
    
    if len(newPassword) < 6:
        return {"success": False, "message": "för kort lösen"}, 400
    
    update = database_helper.changePassword(email, newPassword)

    if update == False:
        return {"success": False, "message": "Database ERROR!"}, 500
    
    return {"success": True, "message": "Password Changed!"}, 200
    

@app.route("/getUserDataByToken", methods=["GET"])
def getUserDataByToken_route():
    token = request.headers.get("Authorization")

    email = database_helper.getEmailByToken(token)

    if email is None:
        return {"success": False, "message": "Invalid token!"}, 401

    result = database_helper.findUserByEmail(email)

    if result is None:
        return {"success": False, "message": "user not found"}, 401
    
    return jsonify({"success": True, "message": "User found", "data": dict(result)}), 200


@app.route("/getUserDataByEmail", methods=["GET"])
def getUserDataByEmail_route():
    token = request.headers.get("Authorization")

    emailCheck = database_helper.getEmailByToken(token)

    if emailCheck is None:
        return {"success": False, "message": "Invalid token!"}, 401
    
    email = request.args.get("email")
    result = database_helper.findUserByEmail(email)
    
    if result is None:
        return {"success": False, "message": "user not found"}, 404

    return jsonify({"success": True, "message": "User found", "data": dict(result)}), 200


@app.route("/getUserMessageByToken", methods=["GET"])
def getUserMessageByToken():
    token = request.headers.get("Authorization")

    email = database_helper.getEmailByToken(token)

    if email is None:
        return {"success": False, "message": "Invalid token!"}, 401
    
    result = database_helper.getUserMsg(email)
    messages = [dict(row) for row in result]

    if result is None:
        return {"success": False, "message": "user not found"}, 401
    
    return jsonify({"success": True, "message": "User found", "data": messages}), 200

    
@app.route("/getUserMessageByEmail", methods=["GET"])
def getUserMessageByEmail_route():
    token = request.headers.get("Authorization")

    emailCheck = database_helper.getEmailByToken(token)

    if emailCheck is None:
        return {"success": False, "message": "Invalid token!"}, 401

    email = request.args.get("email")
    result = database_helper.getUserMsg(email)
    messages = [dict(row) for row in result]

    if result is None:
        return {"success": False, "message": "user not found"}, 404
    
    return jsonify({"success": True, "message": "User found", "data": messages}), 200


@app.route("/postMessage", methods=["POST"])
def postMessage_route():
    data = request.json
    token = request.headers.get("Authorization")

    email = database_helper.getEmailByToken(token)

    if email is None:
        return {"success": False, "message": "Invalid token!"}, 401
    
    message = data.get("message")
    receiver = data.get("receiver")    
    if receiver == None:
        receiver = email

    if len(message) == 0:
        return {"success": False, "message": "Message is empty"}, 400

    result = database_helper.createMessage(email, receiver, message)

    if result == False:
        return{"success": False, "message": "FEEEEEEL"}, 500
    
    return{"success": True, "message": "yay posted"}, 201

    
if __name__ == "__main__":
    app.run(debug=True)