from flask import Flask, request, jsonify, redirect, Response
from supabase import create_client
import os

app = Flask(__name__)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)


@app.route("/")
def home():
    return "API ONLINE ✅"


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

    # Login Xtream
    if not action:

        return jsonify({
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": cliente.get("usuario"),
                "password": cliente.get("senha"),
                "active_cons": "1",
                "max_connections": str(
                    cliente.get("max_connections", 1)
                ),
                "allowed_output_formats": [
                    "ts",
                    "m3u8"
                ]
            },
            "server_info": {
                "url": "onlive-yi4x.onrender.com",
                "port": "443",
                "https_port": "443",
                "server_protocol": "https",
                "timezone": "America/Sao_Paulo"
            }
        })

    # Categorias LIVE
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

    # Streams LIVE
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
                "num": s["id"],
                "name": s["nome"],
                "stream_type": "live",
                "stream_id": s["id"],
                "stream_icon": s.get("logo", "") or "",
                "epg_channel_id": "",
                "added": "",
                "category_id": str(s["categoria_id"]),
                "custom_sid": "",
                "tv_archive": 0,
                "direct_source": s["url_stream"]
                "tv_archive_duration": 0
            })

        return jsonify(retorno)

    return jsonify([])


@app.route("/get.php")
def get_m3u():

    username = request.args.get("username")
    password = request.args.get("password")

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

    categorias = (
        supabase.table("categorias")
        .select("*")
        .execute()
    )

    mapa_categorias = {}

    for c in categorias.data:
        mapa_categorias[c["id"]] = c["nome"]

    streams = (
        supabase.table("streams")
        .select("*")
        .eq("tipo", "LIVE")
        .eq("ativo", True)
        .execute()
    )

    m3u = "#EXTM3U\n\n"

    for s in streams.data:

        categoria = mapa_categorias.get(
            s["categoria_id"],
            "OUTROS"
        )

        m3u += (
            f'#EXTINF:-1 '
            f'tvg-id="" '
            f'tvg-name="{s["nome"]}" '
            f'tvg-logo="{s.get("logo", "")}" '
            f'group-title="{categoria}",'
            f'{s["nome"]}\n'
            f'https://onlive-yi4x.onrender.com/live/'
            f'{username}/{password}/{s["id"]}.ts\n'
        )

    return Response(
        m3u,
        mimetype="text/plain"
    )


@app.route("/live/<username>/<password>/<int:stream_id>.ts")
def live_stream(username, password, stream_id):

    cliente = (
        supabase.table("clientes")
        .select("id")
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

    return redirect(
        stream.data[0]["url_stream"],
        code=302
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
