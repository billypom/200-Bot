from config import VERIFICATION_CHANNEL_ID

async def send_raw_to_verification_log(client, message, verify_description):
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)
    await channel.send(f'{verify_description}\n{message}')