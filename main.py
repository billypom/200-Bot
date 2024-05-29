import sys
import os
import discord
from discord.ext import commands
from discord import Embed, Color
import logging
import DBA
import datetime
import configparser
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.getters import get_discord_role
from helpers import set_uid_roles
from constants import (
    CHAT_RESTRICTED_ROLE_ID,
    DEBUG_CHANNEL_ID,
    SUPPORT_CHANNEL_ID,
    NAME_CHANGE_CHANNEL_ID,
    TOKEN,
)
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import TextChannel

# Config file
config_file = configparser.ConfigParser()
config_file.read("config.ini")
# Logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename="200lounge.log",
    filemode="a",
    level=logging.INFO,
    format=log_format,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Easier imports (dynamic import)
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)


# Bot config
# Intents:  manage roles, manage channels, manage nicknames, read messages/viewchannels, manage events
#           send messages, manage messages, embed links, attach files, add reactions, use slash commands
intents = discord.Intents(
    guilds=True, messages=True, members=True, reactions=True, message_content=True
)
client = discord.Bot(intents=intents, activity=discord.Game(str("200cc Lounge")))

LOOP_EXTENSIONS = config_file["COMMANDS"].get("LOOP_EXTENSIONS")
COMMAND_EXTENSIONS = config_file["COMMANDS"].get("COMMAND_EXTENSIONS")
ADMIN_COMMAND_EXTENSIONS = config_file["COMMANDS"].get("ADMIN_COMMAND_EXTENSIONS")
# Load cogs
for extension in LOOP_EXTENSIONS.split(","):
    client.load_extension(f"cogs.{extension.strip()}")

for extension in COMMAND_EXTENSIONS.split(","):
    client.load_extension(f"cogs.{extension.strip()}")

for extension in ADMIN_COMMAND_EXTENSIONS.split(","):
    client.load_extension(f"cogs.{extension.strip()}")


@client.event
async def on_ready():
    channel = cast("TextChannel", client.get_channel(DEBUG_CHANNEL_ID))
    embed = Embed(title="Startup", description=":3", color=Color.og_blurple())
    embed.add_field(name="200-Lounge Bot Restarted", value=":D", inline=False)
    await channel.send(content=None, embed=embed)


@client.event
async def on_application_command_error(ctx, error) -> None:
    """Handles responses when errors are raised by slash commands"""
    if ctx.guild is None:
        await ctx.respond(
            "Sorry! My commands do not work in DMs. Please use 200cc Lounge :)"
        )
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error, delete_after=10)
        return
    elif isinstance(error, commands.MissingRole):
        await ctx.respond(
            "You do not have permission to use this command.", delete_after=20
        )
        return
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.respond(
            "You do not have permission to use this command.", delete_after=20
        )
        return
    else:
        channel = cast("TextChannel", client.get_channel(DEBUG_CHANNEL_ID))
        await channel.send(
            f"Unhandled exception in `on_application_command_error`\nName:{ctx.author}\nAuthor ID:{ctx.author.id}\nError:{str(error)}"
        )
        logging.warning(f"ERROR IN on_application_command_error by | {error}")
        await ctx.respond(
            f"Sorry! An unknown error occurred. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
        )
        raise error


@client.event
async def on_message(ctx):
    if ctx.author == client.user:  # ignore bot messages
        return
    if ctx.channel.id == 558096949337915413:  # ignore carl bot logging
        return
    guild = get_lounge_guild(client)
    try:
        if ctx.guild != guild:  # Only care if messages are in 200 Lounge
            return
    except Exception:
        return
    user = await guild.fetch_member(ctx.author.id)
    try:
        if (
            get_discord_role(client, CHAT_RESTRICTED_ROLE_ID) in user.roles
        ):  # restricted players
            await ctx.delete()
            return
    except Exception as e:
        logging.warning(
            f"on_message event error 1 - could not compare chat restricted role | {e}"
        )


@client.event
async def on_raw_reaction_add(payload):
    if int(payload.user_id) == int(client.user.id):
        # Return if bot reaction
        return
    if payload.channel_id == NAME_CHANGE_CHANNEL_ID:
        pass
    else:
        # Return if this isnt a name change approval
        return

    # Stuff relating to the current embed
    guild = client.get_guild(payload.guild_id)
    channel: "TextChannel" = cast("TextChannel", client.get_channel(payload.channel_id))
    message = await channel.fetch_message(payload.message_id)
    try:
        with DBA.DBAccess() as db:
            message_ids = db.query(
                "SELECT embed_message_id, player_id, requested_name FROM player_name_request WHERE was_accepted = %s ORDER BY create_date DESC;",
                (0,),
            )
    except Exception as e:
        await send_raw_to_debug_channel(client, "Name change exception 1", e)
        return

    # Look @ all embed message ids
    for i in range(0, len(message_ids)):
        if int(payload.message_id) == int(message_ids[i][0]):  # type: ignore
            try:
                # Accept
                if str(payload.emoji) == "✅":
                    # Edit DB player name
                    try:
                        with DBA.DBAccess() as db:
                            # Set record to accepted
                            db.execute(
                                "UPDATE player_name_request SET was_accepted = %s WHERE embed_message_id = %s;",
                                (1, int(payload.message_id)),
                            )
                            # Change the db username
                            db.execute(
                                "UPDATE player SET player_name = %s WHERE player_id = %s;",
                                (message_ids[i][2], message_ids[i][1]),  # type: ignore
                            )
                    except Exception as e:
                        await send_raw_to_debug_channel(
                            client, "Name change exception 2", e
                        )
                        pass
                    member = guild.get_member(message_ids[i][1])  # type: ignore
                    # Player not in guild
                    if member is None:
                        await send_raw_to_debug_channel(
                            client,
                            "Name change exception 5 - User is not in guild",
                            None,
                        )
                        return
                    # DM player
                    try:
                        await member.send(
                            f"Your name change [{message_ids[i][2]}] has been approved."  # type: ignore
                        )
                    except Exception as e:
                        await send_raw_to_debug_channel(
                            client, "Name change exception 3", e
                        )
                        pass
                    # Edit discord nickname
                    try:
                        await member.edit(nick=str(message_ids[i][2]))  # type: ignore
                    except Exception as e:
                        await send_raw_to_debug_channel(
                            client, "Name change exception 4", e
                        )
                        pass
                # Deny
                elif str(payload.emoji) == "❌":
                    with DBA.DBAccess() as db:
                        # Remove the db record
                        db.execute(
                            "DELETE FROM player_name_request WHERE embed_message_id = %s;",
                            (int(payload.message_id),),
                        )
                        # Delete the embed message
                    member = guild.get_member(message_ids[i][1])  # type: ignore
                    await member.send(  # type: ignore
                        f"Your name change [{message_ids[i][2]}] has been denied."  # type: ignore
                    )
                    await message.delete()
                # Any other reaction - Force an exception
                else:
                    x = int("hey")
                    x += x
            except Exception as e:
                await send_raw_to_debug_channel(client, "Name change exception", e)
                pass
        # Decision was made, delete embed message
        try:
            # await message.remove_reaction(payload.emoji, member)
            await message.delete()
        except Exception:
            pass
    return


@client.event
async def on_member_join(member):
    # Try to set roles on join
    try:
        x = await set_uid_roles(client, member.id)
        if not x:
            return
    except Exception as e:
        logging.error(f"on_member_join exception: {e}")
        return


if __name__ == "__main__":
    client.run(TOKEN)
