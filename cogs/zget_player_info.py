import discord
from discord.ext import commands
import DBA
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE


class PlayerInfoCog(commands.Cog):
    """/zget_player_info - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zget_player_info",
        description="Get player DB info",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zget_player_info(
        self,
        ctx,
        name: discord.Option(str, "Name", required=False),  # type: ignore
        discord_id: discord.Option(str, "Discord ID", required=False),  # type: ignore
        mkc_id: discord.Option(str, "MKC Forum ID", required=False),  # type: ignore
    ):
        """
        # STAFF ONLY
        Gets db info about a particular player

        Args:
        - `name` (str): Player name
        - `discord_id` (str): Discord user ID
        - `mkc_id` (str): MKC forum ID
        """
        await ctx.defer()

        if discord_id:
            pass
        elif name:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;", (name,)
                )
                discord_id = temp[0][0]
        elif mkc_id:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT player_id FROM player WHERE mkc_id = %s;", (mkc_id,)
                )
                discord_id = temp[0][0]
        else:
            await ctx.respond("You must provide a `name` or `discord_id` or `mkc_id`")
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    """SELECT player_id, player_name, mkc_id, mmr, is_chat_restricted, times_strike_limit_reached 
                FROM player 
                WHERE player_id = %s;""",
                    (discord_id,),
                )
                strike_count = db.query(
                    "SELECT count(*) FROM strike WHERE player_id = %s;", (discord_id,)
                )[0][0]
                number_of_punishments = db.query(
                    "SELECT count(*) from player_punishment WHERE player_id = %s;",
                    (discord_id,),
                )[0][0]
            await ctx.respond(f"""`discord id`: {temp[0][0]}
`name`: {temp[0][1]}
`mkc_forum_id`: {temp[0][2]}
`mmr`: {temp[0][3]}
`chat restricted`: {'y' if temp[0][4] == 1 else 'n'}
`strike limit reached`: {temp[0][5]} times
`total # of strikes`: {strike_count}
`total # of punishments`: {number_of_punishments}
""")
            return
        except Exception:
            await ctx.respond("Invalid name or discord ID")
            return


def setup(client):
    client.add_cog(PlayerInfoCog(client))
