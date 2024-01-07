from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_raw_to_debug_channel
from config import LOUNGE


class MMR(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='mmr',
        description='Your mmr',
        guild_ids=LOUNGE
    )
    async def mmr(self, ctx):
        await ctx.defer(ephemeral=True)
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>')
            return
        else:
            pass
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT p.mmr, r.rank_name FROM player as p JOIN ranks as r ON p.rank_id = r.rank_id WHERE p.player_id = %s;', (ctx.author.id,))
                mmr = temp[0][0]
                rank_name = temp[0][1]
            if temp:
                pass
            else:
                await ctx.respond('``Error 43:`` Player not found')
                return
            if mmr is None:
                mmr = "n/a"
            await ctx.respond(f'`MMR:` {mmr} | `Rank:` {rank_name}. If this looks wrong, try the `/verify` command.')
            return
        except Exception as e:
            await send_raw_to_debug_channel(self.client, '/mmr command triggered by player without mmr: ', e)
            await ctx.respond('Use `/verify` to register for Lounge before checking your MMR.')
            return

def setup(client):
    client.add_cog(MMR(client))