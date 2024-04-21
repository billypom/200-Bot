from discord.ext import commands, tasks
from discord import Embed, Color
import datetime
import DBA
from constants import DEBUG_CHANNEL_ID, PING_DEVELOPER
import logging


class strike_check(commands.Cog):
    """Cog runs every hour and checks if strikes are past their expiration time.
    Inactivates strikes that meet the criteria"""

    def __init__(self, client):
        self.check.start()
        self.client = client
        self.title = "Hourly Strike Check"

    async def send_embed(self, anything, error):
        """Sends a confirmation embed to the debug channel"""
        channel = self.client.get_channel(DEBUG_CHANNEL_ID)
        embed = Embed(title=self.title, description="✅", color=Color.teal())
        embed.add_field(name="Description: ", value=anything, inline=False)
        embed.add_field(name="Strike IDs: ", value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    async def send_error_embed(self, anything, error):
        """Sends an error embed to the debug channel"""
        channel = self.client.get_channel(DEBUG_CHANNEL_ID)
        embed = Embed(title=self.title, description="✅", color=Color.red())
        embed.add_field(name="Description: ", value=anything, inline=False)
        embed.add_field(name="Details: ", value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        """Unloads cog"""
        self.check.cancel()

    @tasks.loop(hours=1)
    async def check(self):
        """Every hour, checks for strikes and inactivates records that are past the expiration date"""
        current_time = datetime.datetime.now()
        # Get all active strikes to remove
        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT strike_id FROM strike WHERE expiration_date < %s AND is_active = %s;",
                    (current_time, 1),
                )
        except Exception as e:
            logging.info(f"strike_check | ERROR - unable to retrieve strike | {e}")
            await self.send_error_embed(f"strike_check error 1 {PING_DEVELOPER}", e)
            return
        # Set strikes inactive
        if temp:
            logging.info(f"strike_check | Strikes expiring: {str(temp)}")
            await self.send_embed("Strikes expiring by strike_id", str(temp))
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE strike SET is_active = %s WHERE expiration_date < %s;",
                        (0, current_time),
                    )
            except Exception as e:
                logging.info(
                    f"strike_check | ERROR - unable to set strikes to inactive | {e}"
                )
                await self.send_error_embed(f"strike_check error 2 {PING_DEVELOPER}", e)
                return

    @check.before_loop
    async def before_check(self):
        """Runs before the cog"""
        print("strike waiting...")
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(strike_check(client))
