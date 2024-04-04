import discord
from discord.ui import View


# Discord UI button - Confirmation button
class Confirm(View):
    def __init__(self, uid):
        super().__init__()
        self.value = None
        self.uid = uid

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        # Only accept input from user who initiated the interaction
        if self.uid != interaction.user.id:
            return
        await interaction.response.send_message("Confirming...", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Only accept input from user who initiated the interaction
        if self.uid != interaction.user.id:
            return
        await interaction.response.send_message("Denying...", ephemeral=True)
        self.value = False
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
