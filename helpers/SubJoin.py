import discord
from discord.ui import View
import DBA
from helpers.getters import get_lounge_guild
from discord import PermissionOverwrite
from config import LOUNGE_QUEUE_SUB_CHANNEL_ID
import logging

# Discord UI button - Confirmation button
class SubJoin(View):
    def __init__(self, client, channel_id):
        super().__init__()
        self.value = None
        self.client = client
        self.channel_id = channel_id

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        logging.info(f'class SubJoin | button pressed by: {interaction.user.id}')
        player_id = interaction.user.id
        with DBA.DBAccess() as db:
            player_mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))[0][0]
        if not player_mmr:
            player_mmr = 1000
        
        with DBA.DBAccess() as db:
            room_data = db.query('SELECT min_mmr, max_mmr FROM lounge_queue_channel WHERE channel_id = %s;', (self.channel_id,))[0]
        room_min_mmr = room_data[0]
        room_max_mmr = room_data[1]
        if room_min_mmr <= player_mmr and player_mmr <= room_max_mmr:
            pass
        else:
            sub_channel = self.client.get_channel(LOUNGE_QUEUE_SUB_CHANNEL_ID)
            sub_channel.send(f'<@{player_id}>, you cannot join this room with {player_mmr} MMR', delete_after=60)
            return
        # remove player from queue if exists
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lounge_queue_player WHERE player_id = %s;', (player_id,))
        except Exception as e:
            # if this fails, they're not in the lineup, so i don't care
            pass

        # add interaction user to permissions for self.channel_id
        guild = get_lounge_guild(self.client)
        user = guild.get_member(player_id)
        channel = self.client.get_channel(self.channel_id)
        permissions = PermissionOverwrite(view_channel=True, send_messages=True)
        await channel.set_permissions(user, overwrite=permissions)
        
        # ping the interaction user - attention
        await channel.send(f'<@{player_id}> has joined the room as a sub!')
        await interaction.message.delete()
        self.stop()
        
### Example usage

## Create the confirmation
# table_view = Confirm(ctx.author.id)

## Get the channel
# channel = self.client.get_channel(ctx.channel.id)

## Send the confirmation
# await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)

## Await a response from the user
# await table_view.wait()

## Evaluate the response
# if table_view.value is None:
#     await ctx.respond('No response. Timed out')
# elif table_view.value: # yes
# else: # no
