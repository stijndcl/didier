from discord.ext import commands, ipc


class IPC(commands.Cog):
    def __init__(self, client):
        self.client = client

    @ipc.server.route()
    async def send_dm(self, data):
        print("got here")
        user = self.client.get_user(data.user)
        await user.send(data.message)
        print("sent")
        return True

    @ipc.server.route()
    async def get_bot_latency(self):
        """
        Get Didier's latency
        """
        return str(round(self.client.latency * 1000))


def setup(client):
    client.add_cog(IPC(client))
