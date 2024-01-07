import discord
from helpers.getters import get_lounge_guild
from config import SUGGESTION_LOG_CHANNEL_ID

async def send_to_suggestion_log_channel(client, ctx, suggestion_id, message, decision, author_id, admin_id, reason):
    channel = client.get_channel(SUGGESTION_LOG_CHANNEL_ID)
    member = get_lounge_guild(client).get_member(author_id)
    if decision:
        embed = discord.Embed(title=f'Suggestion #{suggestion_id} Approved', description='', color=discord.Color.green())
    else:
        embed = discord.Embed(title=f'Suggestion #{suggestion_id} Denied', description='', color=discord.Color.red())
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name='----------', value=message, inline=False)
    embed.add_field(name=f'Reason from {ctx.author.display_name}', value=reason)
    x = await channel.send(content=None, embed=embed)
    return x