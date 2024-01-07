from discord.ext import commands
import DBA
from helpers.checkers import check_if_mogi_is_ongoing
from config import MAX_PLAYERS_IN_MOGI
from helpers.senders import send_to_debug_channel

class VotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='votes',
        description='See the current votes',
        # guild_ids=LOUNGE
    )
    async def votes(self, ctx):
        await ctx.defer()
        is_ongoing = await check_if_mogi_is_ongoing(ctx)
        if is_ongoing:
            pass
        else:
            await ctx.respond('The vote has not started.')
            return
        vote_dict = {}
        return_string = ""
        remove_chars = {
            39: None,  # '
            91: None,  # [
            93: None,  # ]
        }
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT p.player_name, l.vote FROM player as p JOIN lineups as l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
            vote_dict = {1: [], 2: [], 3: [], 4: [], 6: []}
            for player in temp:
                if player[1] in vote_dict:
                    vote_dict[player[1]].append(player[0])
                else:
                    vote_dict[player[1]] = [player[0]]
            return_string = f'`FFA:` {vote_dict[1]}\n`2v2:` {vote_dict[2]}\n`3v3:` {vote_dict[3]}\n`4v4:` {vote_dict[4]}\n`6v6:` {vote_dict[6]}'
            return_string = return_string.translate(remove_chars)
        except Exception as e:
            await send_to_debug_channel(self.bot, ctx, f'/votes | {e}')
            await ctx.respond('`Error 64:` Could not retrieve the votes')
        await ctx.respond(return_string)

def setup(bot):
    bot.add_cog(VotesCog(bot))
