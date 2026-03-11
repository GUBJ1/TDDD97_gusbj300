from flask import Flask, request, jsonify
import json
import database_helper

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Flask!"

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/signIn", methods=["POST"])
def signIn_route():
    email = request.form['logInEmail']
    password = request.form['password']
    result = signIn_route({"username": email, "password": password})

    if result["success"] == False:
        return jsonify(result), 401
    
    return jsonify(result), 200
    

    

    