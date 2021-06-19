import json

from discord.ext import ipc
from functions.database import custom_commands
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


@app.route("/custom", methods=["GET"])
async def get_all_custom_commands():
    """
    Return a list of all custom commands in the bot
    """
    commands = custom_commands.get_all()

    return jsonify(commands)


@app.route("/custom/<command_id>")
async def get_custom_command(command_id):
    try:
        command_id = int(command_id)
    except ValueError:
        # Id is not an int
        return unprocessable_entity("Parameter id was not a valid integer.")

    command = custom_commands.get_by_id(command_id)

    if command is None:
        return page_not_found("")

    return jsonify(command)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "No resource could be found matching the given URL."}), 404


@app.errorhandler(422)
def unprocessable_entity(e):
    return jsonify({"error": e}), 422


if __name__ == "__main__":
    app.run()
