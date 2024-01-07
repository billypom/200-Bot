import discord
import DBA
from discord.ext import commands
from helpers import jp_kr_romanize
from helpers.senders import send_to_verification_log
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.checkers import check_if_uid_exists
from helpers.checkers import check_if_banned_characters
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID
import vlog_msg

class SetPlayerNameCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zset_player_name',
        description='Force a player to a new name'
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zset_player_name(
        self,
        ctx,
        player: discord.Option(discord.Member, 'Player', required=True),
        name: discord.Option(str, 'New name', required=True)
    ):
        await ctx.defer()
        y = await check_if_uid_exists(player.id)
        if y:
            pass
        else:
            await ctx.respond('Player does not exist.\nIf you want to change a non-placed player\'s name, use the nickname feature in Discord.')
            return
        x = await check_if_banned_characters(name)
        if x:
            await send_to_verification_log(self.client, ctx, name, vlog_msg.error1)
            await ctx.respond('You cannot use this name')
            return
        else:
            pass
        input_name = name
        name = await jp_kr_romanize(name)
        name = name.replace(" ", "-")
        if len(name) > 16:
            await ctx.respond(f'Your request: {input_name} -> {name} | Name is too long. 16 characters max')
            return
        is_name_taken = True
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (name,))
                if temp[0][0] is None:
                    is_name_taken = False
                else:
                    is_name_taken = True
        except Exception:
            is_name_taken = False
        if is_name_taken:
            await ctx.respond('Name is taken. Please try again.')
            return
        else:
            try:
                with DBA.DBAccess() as db:
                    db.execute('UPDATE player SET player_name = %s WHERE player_id = %s;', (name, player.id))
            except Exception as e:
                await send_raw_to_debug_channel(self.client, 'Could not force name change...', e)
                await ctx.respond('`Error 77:` Could not force player name change.')
                return
            member = await get_lounge_guild(self.client).fetch_member(player.id)
            try:
                await member.edit(nick=str(name))
            except Exception as e:
                await send_raw_to_debug_channel(self.client, 'Could not force name change 2...', e)
                await ctx.respond('`Error 78:` Could not force player name change.')
                return
            await ctx.respond(f'Name changed for user: <@{player.id}>')
            return

def setup(client):
    client.add_cog(SetPlayerNameCog(client))
