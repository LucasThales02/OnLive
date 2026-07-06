from flask import Flask, request, jsonify, redirect
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

    # Validar cliente
    cliente = (
        supabase.table("clientes")
        .select("*")
        .eq("usuario", username)
        .eq("senha", password)
        .eq("ativo", True)
        .execute()
    )

    if not cliente.data:

        return jsonify({
            "user_info": {
                "auth": 0,
                "status": "Disabled"
            }
        })

    cliente = cliente.data[0]

    # Login
    if not action:

        return jsonify({
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": cliente["usuario"],
                "password": cliente["senha"],
                "active_cons": "1",
                "max_connections": str(
                    cliente.get("max_connections", 1)
                )
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

        streams = (
            supabase.table("streams")
            .select("*")
            .eq("tipo", "LIVE")
            .eq("ativo", True)
            .execute()
        )

        retorno = []

        for s in streams.data:

            retorno.append({
                "stream_id": s["id"],
                "name": s["nome"],
                "stream_icon": s["logo"] or "",
                "category_id": str(s["categoria_id"]),
                "stream_type": "live"
            })

        return jsonify(retorno)

    return jsonify([])


@app.route("/live/<username>/<password>/<int:stream_id>.ts")
def live_stream(username, password, stream_id):

    # Validar cliente
    cliente = (
        supabase.table("clientes")
        .select("*")
        .eq("usuario", username)
        .eq("senha", password)
        .eq("ativo", True)
        .execute()
    )

    if not cliente.data:
        return "Acesso negado", 403

    stream = (
        supabase.table("streams")
        .select("*")
        .eq("id", stream_id)
        .eq("tipo", "LIVE")
        .eq("ativo", True)
        .execute()
    )

    if not stream.data:
        return "Canal não encontrado", 404

    url_stream = stream.data[0]["url_stream"]

    return redirect(url_stream)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
