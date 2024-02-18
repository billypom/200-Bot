import discord
import random
import asyncio
import logging
from discord.ui import View

class FormatVote(View):
    def __init__(self, client, uid_list, clean_pingable_player_list, channel_id):
        super().__init__()
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
        
    async def send_vote_message(self):
        channel = self.client.get_channel(self.channel_id)
        message = await channel.send(f'{self.clean_pingable_player_list}\n# Format Vote:', view=self)
        self.message_id = message.id
        
    async def refresh_vote_buttons(self):
        vote_options = [1, 2, 3, 4]  # Corresponding to your self.votes keys
        for button, format_number in zip(self.children, vote_options):
            # Update each button's label with the current vote count
            new_label = f"{format_number}v{format_number} - ({len(self.votes[format_number])})"
            button.label = new_label
        
    async def refresh_message(self):
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
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in self.uid_list

    async def wait(self):
        await self.completed.wait()
    
    async def run(self):
        await self.send_vote_message()
        await asyncio.sleep(self.voting_time_seconds)
        self.completed.set()
    
    async def on_timeout(self):
        self.completed.set()
        
    async def on_stop(self):
        self.completed.set()
        
    async def get_result(self):
        await self.wait()
        # thank u chatgpt
        votes_count = {format_number: len(votes) for format_number, votes in self.votes.items()}
        max_votes = max(votes_count.values())
        tied_formats = [format_number for format_number, votes in votes_count.items() if votes == max_votes]
        return random.choice(tied_formats)
    
