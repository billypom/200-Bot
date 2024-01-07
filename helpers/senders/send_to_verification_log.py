from config import VERIFICATION_CHANNEL_ID
# Somebody did a bad
# ctx | message | discord.Color.red() | my custom message
async def send_to_verification_log(client, ctx, message, verify_description):
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)
    await channel.send(f'{verify_description}\n{ctx.author.id} | {ctx.author.mention}\n{message}')