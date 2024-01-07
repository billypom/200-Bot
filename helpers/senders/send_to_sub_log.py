import discord
from config import SUB_CHANNEL_ID
from helpers.getters import get_unix_time_now

async def send_to_sub_log(client, ctx, message):
    unix_now = await get_unix_time_now()
    channel = client.get_channel(SUB_CHANNEL_ID)
    embed = discord.Embed(title='Sub', description=f'<t:{str(int(unix_now))}:F>', color = discord.Color.blurple())
    embed.add_field(name='Issuer: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Message: ', value=str(message), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)