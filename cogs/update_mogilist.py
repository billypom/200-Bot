import discord
from discord.ext import commands, tasks

class update_mogilist(commands.Cog):
    def __init__(self, client):
        self.index = 0
        self.printer.start()
        self.client = client

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5)
    async def printer(self):
        print(f'{self.index} mogilist')
        self.index +=1

def setup(client):
    client.add_cog(update_mogilist(client))