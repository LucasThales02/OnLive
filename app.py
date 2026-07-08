from flask import Flask, request, jsonify, Response
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
    action = request.args.get("action", "").lower()

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

    # LOGIN
    if not action:

        return jsonify({
            "user_info": {
                "auth": "1",
                "status": "Active",
                "username": cliente["usuario"],
                "password": cliente["senha"],
                "message": "",
                "exp_date": "2145916800",
                "is_trial": "0",
                "active_cons": "1",
                "created_at": "1710000000",
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
                "rtmp_port": "443",
                "timezone": "America/Sao_Paulo",
                "timestamp_now": "1710000000"
            }
    })
    
    # LIVE CATEGORIES
    if action == "get_live_categories":

        categorias = (
            supabase.table("categorias")
            .select("*")
            .eq("tipo", "LIVE")
            .eq("ativo", True)
            .execute()
        )

        return jsonify([
            {
                "category_id": str(c["id"]),
                "category_name": c["nome"]
            }
            for c in categorias.data
        ])

    # LIVE STREAMS
    if action == "get_live_streams":

        streams = (
            supabase.table("streams")
            .select("*")
            .eq("tipo", "LIVE")
            .eq("ativo", True)
            .execute()
        )

        return jsonify([
            {
                "num": s["id"],
                "name": s["nome"],
                "stream_type": "live",
                "stream_id": s["id"],
                "stream_icon": s.get("logo", "") or "",
                "category_id": str(s["categoria_id"]),
                "direct_source": s["url_stream"]
            }
            for s in streams.data
        ])

    # MOVIE CATEGORIES
    if action == "get_vod_categories":

        categorias = (
            supabase.table("categorias")
            .select("*")
            .eq("tipo", "MOVIE")
            .eq("ativo", True)
            .execute()
        )

        return jsonify([
            {
                "category_id": str(c["id"]),
                "category_name": c["nome"]
            }
            for c in categorias.data
        ])

    # MOVIES
    if action == "get_vod_streams":

        streams = (
            supabase.table("streams")
            .select("*")
            .eq("tipo", "MOVIE")
            .eq("ativo", True)
            .execute()
        )

        return jsonify([
            {
                "stream_id": s["id"],
                "name": s["nome"],
                "stream_icon": s.get("capa", "") or "",
                "category_id": str(s["categoria_id"]),
                "container_extension": "mp4",
                "direct_source": s["url_stream"]
            }
            for s in streams.data
        ])

    # SERIES CATEGORIES
    if action == "get_series_categories":
    
        categorias = (
            supabase.table("categorias")
            .select("*")
            .eq("tipo", "SERIES")
            .eq("ativo", True)
            .execute()
        )
    
        return jsonify([
            {
                "category_id": str(c["id"]),
                "category_name": c["nome"]
            }
            for c in categorias.data
        ])

    # SERIES
    if action == "get_series":

        streams = (
            supabase.table("streams")
            .select("*")
            .eq("tipo", "SERIES")
            .eq("ativo", True)
            .execute()
        )

        return jsonify([
            {
                "series_id": s["id"],
                "name": s["nome"],
                "cover": s.get("capa", "") or "",
                "category_id": str(s["categoria_id"])
            }
            for s in streams.data
        ])

    return jsonify([])

@app.route("/panel_api.php")
def panel_api():
    return player_api()
    
@app.route("/api.php")
def api():
    return player_api()

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

    mapa_categorias = {
        c["id"]: str(c["nome"]).strip()
        for c in categorias.data
    }

    streams = (
        supabase.table("streams")
        .select("*")
        .eq("ativo", True)
        .order("categoria_id")
        .execute()
    )

    m3u = "#EXTM3U\n\n"

    for s in streams.data:

        categoria = str(
            mapa_categorias.get(
                s["categoria_id"],
                "OUTROS"
            )
        ).strip()

        if s["tipo"] == "MOVIE":
            grupo = f"Filmes | {categoria}"

        elif s["tipo"] == "SERIES":
            grupo = f"Series | {categoria}"

        else:
            grupo = categoria

        grupo = grupo.strip()

        logo = (
            s.get("capa")
            or s.get("logo")
            or ""
        )

        m3u += (
            f'#EXTINF:-1 '
            f'tvg-name="{s["nome"]}" '
            f'tvg-logo="{logo}" '
            f'group-title="{grupo}",{s["nome"]}\n'
            f'{s["url_stream"]}\n\n'
        )

    return Response(
        m3u,
        mimetype="application/x-mpegURL",
        headers={
            "Content-Disposition": "attachment; filename=lista.m3u"
        }
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
