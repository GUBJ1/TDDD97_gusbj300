from flask import Flask, request, jsonify
import json
import database_helper

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Flask!"




@app.route("/signIn", methods=["POST"])
def signIn_route():
    result = database_helper.signIn(request.json)

    if result["success"] == False:
        return jsonify(result), 401
    
    return jsonify(result), 200
    
@app.route("/signUp", methods=["POST"])
def signUp_route():
    result = database_helper.signUp(request.json)

    if result["success"] == False:
        return jsonify(result), 400

    return jsonify(result), 200
    


@app.route("/signOut", methods=["POST"])
def signOut_route():
    token = request.headers.get("Authorization")

    result = database_helper.signOut(token)

    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200


@app.route("/changePassword", methods=["POST"])
def changePassword_route():
    token = request.headers.get("Authorization")

    result = database_helper.changePassword(token, request.json)
    if result["success"] == False:
        return jsonify(result), 400
    
    return jsonify(result), 200
    

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


