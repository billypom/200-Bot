from discord import Permissions
from discord.ext import commands
from constants import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID, BOT_ID


class DeleteBotMessagesCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zdelete_bot_messages",
        description="Delete all bot messages in the current channel from the past 14 days",
        default_member_permissions=(Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zdelete_bot_msgs(self, ctx):
        await ctx.defer()
        channel = ctx.channel
        # Fetch a certain number of messages from the channel, you can adjust the limit
        messages = await channel.history(limit=100).flatten()
        # Filter messages sent by the bot
        bot_messages = [message for message in messages if message.author.id == BOT_ID]
        # Delete bot messages
        await channel.delete_messages(bot_messages)
        # Inform the command invoker that messages have been deleted
        await ctx.respond(content="Deleted bot messages", hidden=True)


def setup(client):
    client.add_cog(DeleteBotMessagesCog(client))
