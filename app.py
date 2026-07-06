from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API ONLINE"

@app.route("/player_api.php")
def player_api():

    username = request.args.get("username")
    password = request.args.get("password")

    return jsonify({
        "user_info": {
            "auth": 1,
            "username": username
        }
    })

if __name__ == "__main__":
    app.run()
