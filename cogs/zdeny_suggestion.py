import discord
from discord.ext import commands
import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.handlers import handle_suggestion_decision
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE


class DenySuggestionCog(commands.Cog):
    """/zdeny_suggestion - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zdeny_suggestion",
        description="Deny a suggestion by ID",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def deny(
        self,
        ctx,
        suggestion_id: discord.Option(int, "Suggestion ID", required=True),
        reason: discord.Option(
            str, "Type your reason (1000 characters max)", required=True
        ),
    ):
        """
        # STAFF ONLY
        Denies a suggestion

        Args:
        - `reason` (str): Reason/justification/description of denial
        """
        await ctx.defer(ephemeral=True)
        try:
            with DBA.DBAccess() as db:
                crap = db.query(
                    "SELECT id, author_id, content, message_id FROM suggestion WHERE id = %s;",
                    (suggestion_id,),
                )
        except Exception as e:
            await send_raw_to_debug_channel(self.client, "/deny_suggestion error 1", e)
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "UPDATE suggestion SET reason = %s, was_accepted = %s, admin_id = %s WHERE id = %s",
                    (reason, 0, ctx.author.id, suggestion_id),
                )
        except Exception as e:
            await send_raw_to_debug_channel(self.client, "/deny_suggestion error 2", e)

        suggestion = crap[0][2]
        author_id = crap[0][1]
        message_id = crap[0][3]
        admin_id = ctx.author.id

        response = await handle_suggestion_decision(
            self.client,
            suggestion_id,
            suggestion,
            author_id,
            message_id,
            admin_id,
            0,
            reason,
        )
        if response:
            await ctx.respond(f"Suggestion #{suggestion_id} denied")
        else:
            await ctx.respond("Error...")


def setup(client):
    client.add_cog(DenySuggestionCog(client))
