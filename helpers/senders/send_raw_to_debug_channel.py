from config import DEBUG_CHANNEL_ID
import discord
async def send_raw_to_debug_channel(client, anything, error):
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    embed = discord.Embed(title='Debug', description='>.<', color = discord.Color.yellow())
    embed.add_field(name='Details: ', value=anything, inline=False)
    embed.add_field(name='Traceback: ', value=str(error), inline=False)
    await channel.send(content=None, embed=embed)