async def delete_discord_channel(client, channel_id):
    channel = client.get_channel(channel_id)
    if channel:
        try:
            await channel.delete()
            print(f'Channel {channel_id} deleted')
            return True
        except Exception as e:
            print(f'Failed to deleted channel {channel_id}: {e}')
            return False
    else:
        print(f'Channel {channel_id} not found')
        # ok to return true here, dont care if didnt find channel
        return True