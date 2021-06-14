import json

from discord.ext import ipc
from quart import Quart, jsonify, request
from quart_cors import cors
from time import time


app = Quart(__name__)
# TODO allow_origin=re.compile(r"http://localhost:.*")
#      needs higher Python & Quart version
app = cors(app, allow_origin="*")
app.config.from_object(__name__)


ipc_client = ipc.Client(secret_key="SOME_SECRET_KEY")


@app.route("/ping", methods=["GET"])
async def ping():
    """
    Send a ping request, monitors bot latency, endpoint time, and PSQL latency
    """
    latency = await ipc_client.request("get_bot_latency")

    return jsonify({"bot_latency": latency, "response_sent": time()})


@app.route("/dm", methods=["POST"])
async def send_dm():
    """
    Send a DM to the given user
    """
    data = json.loads((await request.body).decode('UTF-8'))

    dm = await ipc_client.request(
        "send_dm",
        user=int(data["userid"]),
        message=data.get("message")
    )

    return jsonify({"response": dm})


if __name__ == "__main__":
    app.run()
