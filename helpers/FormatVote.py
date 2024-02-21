import discord
import random
import asyncio
import logging
from discord.ui import View

class FormatVote(View):
    """Discord View that starts a 60 second mogi format vote
    ## input:
    client = discord bot/client
    uid_list = list of players in room
    clean_pingable_player_list = string of all players in room like: <@discord_id> <@discord_id> etc
    channel_id = the channel to start the vote in
    average_mmr = average mmr of the room
    min_mmr = smallest mmr of the room
    max_mmr = largest mmr of the room
    channel_name = name of the room channel
    """
    def __init__(self, client, uid_list: list, clean_pingable_player_list: str, channel_id: int, average_mmr: int, min_mmr: int, max_mmr: int, channel_name: str):
        super().__init__()
        # self.votes is a list of players who voted for a format, NOT an integer
        self.votes = {
            1: [],
            2: [],
            3: [],
            4: []
        }
        self.uid_list = uid_list
        self.client = client
        self.completed = asyncio.Event()
        self.voting_time_seconds = 60
        self.channel_id = channel_id
        self.message_id = None
        self.clean_pingable_player_list = clean_pingable_player_list
        self.average_mmr = average_mmr
        self.min_mmr = min_mmr
        self.max_mmr = max_mmr
        self.channel_name = channel_name
        
    async def send_vote_message(self):
        """Sends a message to the room, pings all players, displays buttons"""
        channel = self.client.get_channel(self.channel_id)
        message = await channel.send(f'{self.clean_pingable_player_list}\n# Format Vote:', view=self)
        self.message_id = message.id
        
    async def refresh_vote_buttons(self):
        """Updates the button label text"""
        vote_options = [1, 2, 3, 4]  # Corresponding to your self.votes keys
        for button, format_number in zip(self.children, vote_options):
            # Update each button's label with the current vote count
            new_label = f"{format_number}v{format_number} - ({len(self.votes[format_number])})"
            button.label = new_label
        
    async def refresh_message(self):
        """Refreshes the vote message"""
        channel = self.client.get_channel(self.channel_id)
        if channel and self.message_id:
            try:
                message = await channel.fetch_message(self.message_id)
                await self.refresh_vote_buttons()
                await message.edit(view=self)
            except Exception as e:
                logging.warning(f'FormatVote refresh_message error: {e}')
        else:
            logging.info('No channel, no message, no swag')
    
    @discord.ui.button(label="FFA - (0)", style=discord.ButtonStyle.blurple)
    async def ffa(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.vote(1, interaction)
        button.label = f"FFA - ({len(self.votes[1])})"
        await self.refresh_message()
        await interaction.response.edit_message()
        
    @discord.ui.button(label="2v2 - (0)", style=discord.ButtonStyle.blurple)
    async def two(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.vote(2, interaction)
        button.label = f"2v2 - ({len(self.votes[2])})"
        await self.refresh_message()
        await interaction.response.edit_message()
        
    @discord.ui.button(label="3v3 - (0)", style=discord.ButtonStyle.blurple)
    async def three(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.vote(3, interaction)
        button.label = f"3v3 - ({len(self.votes[3])})"
        await self.refresh_message()
        await interaction.response.edit_message()
    
    @discord.ui.button(label="4v4 - (0)", style=discord.ButtonStyle.blurple)
    async def four(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.vote(4, interaction)
        button.label = f"4v4 - ({len(self.votes[4])})"
        await self.refresh_message()
        await interaction.response.edit_message()
    
    async def vote(self, format_number, interaction):
        """Player clicks a button to vote for a format"""
        if interaction.user.id not in self.uid_list:
            return
        for i in range(1,5):
            if i == format_number:
                # add new vote
                if interaction.user.id in self.votes[i]:
                    return
                self.votes[i].append(interaction.user.id)
            else:
                # remove other votes
                if interaction.user.id in self.votes[i]:
                    self.votes[i].remove(interaction.user.id)
        for vote_count in self.votes.values():
            if len(vote_count) >= 6:
                self.completed.set()
                await self.refresh_message()
                break
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Checks if player is eligible to vote"""
        return interaction.user.id in self.uid_list

    async def wait(self):
        await self.completed.wait()
    
    async def run(self):
        """Starts the format vote. Sends the message with buttons and stuff"""
        await self.send_vote_message()
        await asyncio.sleep(self.voting_time_seconds)
        self.completed.set()
    
    async def on_timeout(self):
        self.completed.set()
        
    async def on_stop(self):
        self.completed.set()
        
    async def get_result(self):
        """Returns the chosen format, if tied, chooses a random format from the ties"""
        await self.wait()
        # thank u chatgpt
        votes_count = {format_number: len(votes) for format_number, votes in self.votes.items()}
        max_votes = max(votes_count.values())
        tied_formats = [format_number for format_number, votes in votes_count.items() if votes == max_votes]
        return random.choice(tied_formats)
    
