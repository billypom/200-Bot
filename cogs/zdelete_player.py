import discord
from discord.ext import commands
from DBA import DBAccess 
from helpers.checkers import check_if_uid_exists
from helpers import Confirm
from config import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID

class DeletePlayerCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zdelete_player',
        description='ADMIN ONLY [DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING]',
        guild_ids=LOUNGE
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zdelete_player(self, ctx, discord_id: discord.Option(str, 'Discord ID', required=True)):
        await ctx.defer()
        channel = self.client.get_channel(ctx.channel.id)
        x = await check_if_uid_exists(discord_id)
        if x:
            pass
        else:
            await ctx.respond('Player does not exist')
            return
        with DBAccess() as db:
            temp = db.query('select p.player_id, p.player_name, p.mmr, r.rank_name FROM player p JOIN ranks r ON p.rank_id = r.rank_id where player_id = %s;', (discord_id,))
        confirmation = Confirm(ctx.author.id)
        await channel.send(f'Are you sure you want to delete this player?\n<@{discord_id}>\n`Name:`{temp[0][1]}\n`MMR:`{temp[0][2]}\n`Rank:`{temp[0][3]}', view=confirmation, delete_after=300)
        await confirmation.wait()
        if confirmation.value is None:
            await ctx.respond('Timed out...')
            return
        elif confirmation.value:  # yes
            with DBAccess() as db:
                db.execute('DELETE FROM player WHERE player_id = %s;', (discord_id,))
            await ctx.respond('Player deleted successfully')
            return
        else:
            await ctx.respond('Operation cancelled.')
            return

def setup(client):
    client.add_cog(DeletePlayerCog(client))