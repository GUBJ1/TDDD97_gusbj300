from flask import Flask, request, jsonify, g
import json
import database_helper
import re

app = Flask(__name__)

signedInUsers={}

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "database", None)
    if db is not None:
        db.close()
        print("DB connection closed")


@app.route("/signIn", methods=["POST"])
def signIn_route():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    result = database_helper.findUserByEmail(email)

    if result is None:
        return {"success": False, "message": "User not found"}, 401
    
    if result["password"] != password:
        return {"success": False, "message": "Wrong password!"}, 401
    
    token = database_helper.generateToken()
    signedInUsers[token] = email
    print("TOKEN: ", token)

    return {"success": True, "message": "Signed in!"}, 200

    
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

    result = database_helper.signOut(token)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200




# @app.route("/changePassword", methods=["POST"])
# def changePassword_route():
#     token = request.headers.get("Authorization")

#     result = database_helper.changePassword(token, request.json)
#     if result["success"] == False:
#         return jsonify(result), 400
    
#     return jsonify(result), 200

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

    result = database_helper.getUserDataByToken(token)
    print(result)
    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200


@app.route("/getUserDataByEmail", methods=["GET"])
def getUserDataByEmail_route():
    token = request.headers.get("Authorization")
    email = request.args.get("email")

    result = database_helper.getUserDataByEmail(token, email)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200
    

@app.route("/getUserMessageByToken", methods=["GET"])
def getUserMessageByToken_route():
    token = request.headers.get("Authorization")

    result = database_helper.getUserMessageByToken(token)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200


@app.route("/getUserMessageByEmail", methods=["GET"])
def getUserMessageByEmail_route():
    token = request.headers.get("Authorization")
    email = request.args.get("email")

    result = database_helper.getUserMessageByEmail(token, email)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200


@app.route("/postMessage", methods=["POST"])
def postMessage_route():
    token = request.headers.get("Authorization")

    result = database_helper.postMessage(token, request.json)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200

    
if __name__ == "__main__":
    app.run(debug=True)


