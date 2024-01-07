import discord
from discord.ext import commands
import math
import DBA 
from helpers.checkers import check_if_banned_characters
from helpers.checkers import check_if_mogi_id_exists
from helpers.senders import send_to_debug_channel
from helpers import set_uid_roles
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID

# missing 4 races = 2/3
# missing 6 races = 1/2
# missing 7 races = 5/12
# missing 8 races = 1/3
# missing 9 races = 1/4
# missing 10 races = 1/6
# missing 11 races = 1/12
# missing the whole mogi = no loss

class ReduceLossCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zreduce_loss',
        description='Reduce the loss for 1 player in 1 mogi',
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zreduce_loss(self, ctx,
                           player: discord.Option(str, description='Player name', required=True),
                           mogi_id: discord.Option(int, description='Which mogi?', required=True),
                           reduction: discord.Option(str, description='Missing # of races: (4-12) = (2/3, 2/3, 1/2, 5/12, 1/3, 1/4, 1/6, 1/12)', required=True)):
        await ctx.defer()
        with DBA.DBAccess() as db:
            player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
        if player_id:
            pass
        else:
            await ctx.respond('Player not found')
            return
        y = await check_if_mogi_id_exists(mogi_id)
        if y:
            pass
        else:
            await ctx.respond('Mogi ID not found')
            return
        z = await check_if_banned_characters(reduction)
        if z:
            await ctx.respond("Bad input")
            return
        else:
            pass
        # Get the mmr change
        reduce = str(reduction).split("/")
        multiplier = int(reduce[0]) / int(reduce[1])
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT mmr_change, prev_mmr FROM player_mogi WHERE player_id = %s AND mogi_id = %s;',
                                (player_id, mogi_id))
                temp2 = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))
                mmr_change = temp[0][0]
                prev_mmr = temp[0][1]
                mmr = temp2[0][0]
        except Exception:
            await ctx.respond('``Error 40:`` tell popuko or try again later')
            return
        reverted_mmr_change = mmr_change * -1  # opposite of mmr_change
        reverted_mmr = mmr + reverted_mmr_change  # temp variable
        adjusted_mmr_change = int(math.floor(mmr_change * multiplier))  # mmr change * reduction value
        adjusted_mmr = reverted_mmr + adjusted_mmr_change  # player mmr
        adjusted_new_mmr = int(math.floor(prev_mmr + adjusted_mmr_change))  # pm new_mmr
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player_mogi SET mmr_change = %s, new_mmr = %s WHERE player_id = %s AND mogi_id = %s;',
                           (adjusted_mmr_change, adjusted_new_mmr, player_id, mogi_id))
                db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (adjusted_mmr, player_id))
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f'player_name: {player} | mogi id: {mogi_id} | reduction: {reduction} | {e}')
            await ctx.respond('``Error 41:`` FATAL ERROR uh oh uh oh uh oh')
            return
        await set_uid_roles(self.client, player_id)
        await ctx.respond(
            f'Loss was reduced for <@{player_id}>.\nChange: `{mmr_change}` -> `{adjusted_mmr_change}`\nMMR: `{mmr}` -> `{adjusted_mmr}`')


def setup(client):
    client.add_cog(ReduceLossCog(client))
