from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API ONLINE"

@app.route("/player_api.php")
def player_api():

    username = request.args.get("username")
    password = request.args.get("password")
    action = request.args.get("action")

    # Login sem action
    if not action:

        return jsonify({
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": username,
                "password": password,
                "active_cons": "1",
                "max_connections": "1"
            }
        })

    # Categorias Live TV
    if action == "get_live_categories":

        return jsonify([
            {
                "category_id": "1",
                "category_name": "ABERTA"
            },
            {
                "category_id": "2",
                "category_name": "ESPORTES"
            }
        ])

    # Canais Live TV
    if action == "get_live_streams":

        return jsonify([
            {
                "stream_id": 1,
                "name": "Globo SP",
                "stream_icon": "",
                "category_id": "1",
                "stream_type": "live"
            }
        ])

    return jsonify([])
