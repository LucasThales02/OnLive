from flask import Flask, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

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

        categorias = (
            supabase.table("categorias")
            .select("*")
            .eq("tipo", "LIVE")
            .eq("ativo", True)
            .execute()
        )

        retorno = []

        for c in categorias.data:

            retorno.append({
                "category_id": str(c["id"]),
                "category_name": c["nome"]
            })

        return jsonify(retorno)

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
