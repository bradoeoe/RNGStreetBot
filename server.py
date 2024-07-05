import os
import sqlite3

from flask import Flask, jsonify

app = Flask(__name__)


HEADERS = ["discordId", "rsn", "level", "bracket", "opponentId"]

# default is RNGStreet
GUILD_ID = os.environ.get("GUILD_ID", "532377514975428628")
DB_PATH = f"databases/{GUILD_ID}.db"


def get_player_data():
    conn = sqlite3.connect(DB_PATH)

    c = conn.cursor()
    c.execute("SELECT * FROM gun_game")

    return c.fetchall()


@app.route("/api/players/")
def get_players():
    data = get_player_data()

    payload = list(map(lambda row: dict(zip(HEADERS, row)), data))

    response = jsonify(payload)
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response
