import discord
from config import IP_MATCH_CHANNEL_ID

async def send_to_ip_match_log(client, ctx, message, verify_color, user_matches_list):
    channel = client.get_channel(IP_MATCH_CHANNEL_ID)
    embed = discord.Embed(title="Verification", description=f'IP Matches for <@{ctx.author.id}>', color=verify_color)
    try:
        embed.add_field(name="Issuer: ", value=ctx.author, inline=False)
        embed.add_field(name='Link sent: ', value=message, inline=False)
        for user in user_matches_list:
            ip_match_forum_link = f'https://www.mariokartcentral.com/forums/index.php?members/{user}'
            embed.add_field(name=f'{user}', value=ip_match_forum_link, inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
    except Exception as e:
        await channel.send(f'TOO MANY MATCHES: {e} {user_matches_list}')