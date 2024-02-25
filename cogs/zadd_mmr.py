import discord
from discord.ext import commands
from DBA import DBAccess
from config import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID


class AddMMRCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zadd_mmr',
        description='Add MMR to a player',
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def zadd_mmr(self, ctx,
                       player: discord.Option(str, 'Player name', required=True),
                       mmr: discord.Option(int, 'Amount of MMR to add to the player', required=True)):
        await ctx.defer()

        # Check if player exists
        with DBAccess() as db:
            player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
        if player_id:
            pass
        else:
            await ctx.respond('Player not found')
            return
        # Get current MMR of player
        with DBAccess() as db:
            current_mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))[0][0]
        # Calculate new MMR
        new_mmr = current_mmr + mmr
        # Update player record
        with DBAccess() as db:
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (new_mmr, player_id))
        await ctx.respond(f'{mmr} MMR added to <@{player_id}>\n`{current_mmr}` -> `{new_mmr}`')

def setup(client):
    client.add_cog(AddMMRCog(client))
