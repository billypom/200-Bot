import logging


async def delete_discord_channel(client, channel_id):
    channel = client.get_channel(channel_id)
    if channel:
        try:
            await channel.delete()
            return True
        except Exception:
            return False
    else:
        logging.error(f"delete_discord_channel.py | Channel {channel_id} not found")
        # ok to return true here, dont care if didnt find channel
        return True
