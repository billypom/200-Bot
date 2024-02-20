import discord
from discord.ext import commands
import DBA
from helpers.senders import send_to_suggestion_voting_channel
from helpers.senders import send_raw_to_debug_channel
from helpers.checkers import check_if_banned_characters
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_uid_has_role
from config import SUPPORT_CHANNEL_ID, SUGGESTION_RESTRICTED_ROLE_ID, LOUNGE

class SuggestCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='suggest',
        description='Suggest an improvement for the Lounge (1000 characters max)',
        guild_ids=LOUNGE
    )
    async def suggest(
        self,
        ctx,
        message: discord.Option(str, 'Type your suggestion', required=True)
    ):
        await ctx.defer(ephemeral=True)
        is_suggestion_restricted = await check_if_uid_has_role(self.client, ctx.author.id, SUGGESTION_RESTRICTED_ROLE_ID)                
        if is_suggestion_restricted:
            await ctx.respond('You do not have permission to use this command.')
            return
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>')
            return
        else:
            pass
        x = await check_if_banned_characters(message)
        if x:
            await ctx.respond("Oops! There was an error with your suggestion. Try using less symbols - just use letters and numbers.")
            return
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO suggestion (content, author_id) VALUES (%s, %s);', (message, ctx.author.id))
                suggestion_id = db.query('SELECT id FROM suggestion WHERE author_id = %s AND content = %s', (ctx.author.id, message))[0][0]
            request_message = await send_to_suggestion_voting_channel(self.client, ctx, suggestion_id, message)
            request_message_id = request_message.id
            with DBA.DBAccess() as db:
                db.execute('UPDATE suggestion SET message_id = %s WHERE id = %s;', (request_message_id, suggestion_id))
            await request_message.add_reaction('⬆️')
            await request_message.add_reaction('⬇️')
            await ctx.respond('Your suggestion has been submitted.')
        except Exception as e:
            await send_raw_to_debug_channel(self.client, '/suggest error: ', e)
            await ctx.respond(f'`Error 81:` There was an issue with your suggestion. Please create a ticket in {SUPPORT_CHANNEL_ID} with your error number.')
            return

def setup(client):
    client.add_cog(SuggestCog(client))
