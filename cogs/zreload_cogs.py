from discord.ext import commands
from discord import Permissions
from constants import (
    ADMIN_ROLE_ID,
    UPDATER_ROLE_ID,
    LOUNGE,
)
import configparser


class ReloadCogsCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.LOOP_EXTENSIONS = config_file["COMMANDS"].get("LOOP_EXTENSIONS")
        self.COMMAND_EXTENSIONS = config_file["COMMANDS"].get("COMMAND_EXTENSIONS")
        self.ADMIN_COMMAND_EXTENSIONS = config_file["COMMANDS"].get(
            "ADMIN_COMMAND_EXTENSIONS"
        )
        # Load cogs

    @commands.slash_command(
        name="zreload_cogs",
        description="[DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING]",
        guild_ids=LOUNGE,
        default_member_permissions=(Permissions(moderate_members=True)),
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zreload_cogs(self, ctx):
        for extension in self.LOOP_EXTENSIONS.split(","):
            self.client.load_extension(f"cogs.{extension.strip()}")

        for extension in self.COMMAND_EXTENSIONS.split(","):
            self.client.load_extension(f"cogs.{extension.strip()}")

        for extension in self.ADMIN_COMMAND_EXTENSIONS.split(","):
            self.client.load_extension(f"cogs.{extension.strip()}")

        await ctx.respond("All cogs reloaded successfully :smile:")


def setup(client):
    client.add_cog(ReloadCogsCog(client))
