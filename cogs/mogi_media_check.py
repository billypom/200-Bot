import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import secretly
import requests

ml_channel_message_id = 1010644370954924052
ml_lu_channel_message_id = 1010644338499403937
Lounge = [461383953937596416]

class mogi_media_check(commands.Cog):
    def __init__(self, client):
        self.mogi_media.start()
        self.client = client

    async def send_raw_to_debug_channel(self, anything, error):
        channel = self.client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description='>.<', color = discord.Color.yellow())
        embed.add_field(name='anything: ', value=anything, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        self.mogi_media.cancel()
    
    async def get_live_streamers(self, temp):
        list_of_streams = []
        for i in range(0, len(temp)):
            streamer_name = temp[i][0]
            if streamer_name is None:
                continue
            else:
                streamer_name = str(streamer_name).strip().lower()
            body = {
                'client_id': secretly.twitch_client_id,
                'client_secret': secretly.twitch_client_secret,
                "grant_type": 'client_credentials'
            }
            r = requests.post('https://id.twitch.tv/oauth2/token', body)
            #data output
            keys = r.json()
            #print(keys)
            headers = {
                'Client-ID': secretly.twitch_client_id,
                'Authorization': 'Bearer ' + keys['access_token']
            }
            #print(headers)
            stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
            stream_data = stream.json()
            try:
                if len(stream_data['data']) == 1:
                    is_live = True
                    streamer_name = stream_data['data'][0]['user_name']
                    stream_title = stream_data['data'][0]['title']
                    stream_thumbnail_url = stream_data['data'][0]['thumbnail_url']
                    list_of_streams.append([streamer_name, stream_title, stream_thumbnail_url, is_live, temp[i][1], temp[i][2]])
                else:
                    is_live = False
                    stream_title = ""
                    stream_thumbnail_url = ""
                    list_of_streams.append([streamer_name, stream_title, stream_thumbnail_url, is_live, temp[i][1], temp[i][2]])
            except Exception as e:
                continue
            # name, title, image, is_live, db_mogimediamessageid, db_player_id
        return list_of_streams

    @tasks.loop(seconds=30)
    async def mogi_media(self):
        print('checking mogi media...')
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT p.twitch_link, p.mogi_media_message_id, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.can_drop = 0;', ())
        except Exception:
            return
        streams = await self.get_live_streamers(temp)
        print(streams)

        # print(f'future.result from thread executor: {streams}')
        for stream in streams:
            try:
                # If live
                if stream[3]:
                    # If no mogi media sent yet
                    if stream[4] is None:
                        member = await GUILD.fetch_member(stream[5])
                        embed = discord.Embed(title=stream[0], description=stream[1], color=discord.Color.purple())
                        embed.add_field(name='Link', value=f'https://twitch.tv/{stream[0]}', inline=False)
                        embed.set_image(url=stream[2])
                        embed.set_thumbnail(url=member.display_avatar)
                        mogi_media = self.client.get_channel(mogi_media_channel_id)
                        mogi_media_message = await mogi_media.send(embed=embed)
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE player SET mogi_media_message_id = %s WHERE player_id = %s;', (mogi_media_message.id, member.id))
                # If not live
                else:
                    if stream[4] > 0: 
                        member_future = await GUILD.fetch_member(stream[5])
                        member = member_future.result()               
                        channel = self.client.get_channel(mogi_media_channel_id)
                        message = await channel.fetch_message(stream[4])
                        await message.delete()
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE player SET mogi_media_message_id = NULL WHERE player_id = %s;', (member.id,))
            except Exception as e:
                continue

    @mogi_media.before_loop
    async def before_mogi_media(self):
        print('mogi media waiting...')
        await self.client.wait_until_ready()
        global GUILD
        GUILD = self.client.get_guild(Lounge[0])

def setup(client):
    client.add_cog(mogi_media_check(client))