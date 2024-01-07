import discord
from config import DEBUG_CHANNEL_ID

async def send_to_debug_channel(client, ctx, error):
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    embed = discord.Embed(title='Debug', description='>.<', color = discord.Color.blurple())
    embed.add_field(name='Issuer: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)