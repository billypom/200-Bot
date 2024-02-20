import discord
from discord.ext import commands
import DBA
from helpers.senders import send_raw_to_debug_channel
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE


class PlayerPunishmentsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zget_player_punishments",
        description="See all punishments for a player",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zget_player_punishments(
        self,
        ctx,
        name: discord.Option(str, "Name", required=False),
        discord_id: discord.Option(str, "Discord ID", required=False),
    ):
        await ctx.defer()
        if discord_id:
            with DBA.DBAccess() as db:
                name = db.query(
                    "SELECT player_name FROM player WHERE player_id = %s;",
                    (discord_id,),
                )[0][0]
        elif name:
            with DBA.DBAccess() as db:
                discord_id = db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;", (name,)
                )[0][0]
        else:
            await ctx.respond("You must provide a `name` or `discord_id`")
            return
        try:
            channel = self.client.get_channel(ctx.channel.id)

            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT pl.player_name, p.punishment_type, pp.reason, pp.id, pp.unban_date, UNIX_TIMESTAMP(pp.create_date), pp.ban_length FROM punishment p JOIN player_punishment pp ON p.id = pp.punishment_id JOIN player pl ON pp.admin_id = pl.player_id WHERE pp.player_id = %s;",
                    (discord_id,),
                )
                # dynamic list of punishments
                punishment_array = []
                emoji = ""
                for punishment in temp:
                    if punishment[1] == "Restriction":
                        emoji = "🚫"
                    if punishment[1] == "Loungeless":
                        emoji = "🔰"
                    if punishment[1] == "Warning":
                        emoji = "⚠️"
                    punishment_array.append(
                        f"""**{punishment[3]}.** {emoji} {punishment[1]}\n`Reason:` {punishment[2]}\n`Ban length:` {punishment[6]}\n`Unban date:` <t:{str(punishment[4])}:F>\n`Issued on:` <t:{str(punishment[5])}:F>\n`Issued by:` {punishment[0]}"""
                    )

            await ctx.respond(f"# {name}'s punishments")

            for message in punishment_array:
                await channel.send(message)

        except Exception as e:
            await ctx.respond("Invalid name or discord ID")
            await send_raw_to_debug_channel(
                self.client, "Player punishment retrieval error 1", e
            )
            return


def setup(client):
    client.add_cog(PlayerPunishmentsCog(client))
