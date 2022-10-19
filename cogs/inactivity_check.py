import discord
from discord.ext import commands, tasks

class inactivity_check(commands.Cog):
    def __init__(self, client):
        self.index = 0
        self.printer.start()
        self.client = client

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5)
    async def printer(self):
        print(self.index)
        self.index +=1

def setup(client):
    client.add_cog(inactivity_check(client))