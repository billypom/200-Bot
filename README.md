# 🏁 MK8DX 200cc Lounge Bot
This bot is the primary driver for all things related to the MK8DX 200cc Lounge leaderboard.
- Sign up on [mariokartcentral.com](https://www.mariokartcentral.com/)
- `/verify` your MKC identity 
- Gather for matches in the [Discord server](discord.gg/uR3rRzsjhk) using [MogiBot](https://255mp.github.io/)
- Submit match results
- View player stats on [200-lounge.com](https://200-lounge.com), or use the commands below.


## 🤖 Commands
### **/VERIFY** + `[mkc link]`
- Verify your MKC identity (registry or forum link) with this command to participate in mogis.
### **/TABLE** + `[format]` & `[scores]`
- Submit a table.
- Provide a format (1, 2, 3, 4, 6) and a list of 12 players & 12 scores (brandon 180 popuko 12 jpgiviner 42 etc...).
In order is to ensure that all players on a team are grouped together, preserve the team order from @MogiBot. The Lorenzi table and MMR calculations will be out of sync if you do not follow these guidelines.
### **/MMR**
- Displays your MMR
### **/STATS** + (optional) `[#tier-channel]` or `[@player]` or `[last number of mogis]`
- Displays player statistics.
#### /stats example usage
- /stats = my stats
- /stats `#tier-a` = my stats in tier-a
- /stats `last:5` = stats for the last 5 mogis i played
- /stats `@Nino#7507` = Nino's stats
- /stats `#tier-a` `@Nino#7507` = Nino's stats in tier-a
- /stats `#tier-a` `@Nino#7507` `last:5` = Nino's stats for only the last 5 tier-a mogis he has played
### **/SUGGEST** + `[message]`
Submit a suggestion to improve the Lounge.
### **/NAME** + `[new name]`
Submit a name-change request to staff.
### **/STRIKES**
Displays your strikes & their expiration dates

# 🖲️ Staff Utilities
Useful commands, available only to staff members, to manage the leaderboard and Discord community.
## __🌆 MOGI COMMANDS__
### **/ZREVERT** + `mogi_id` 
- Deletes a specific mogi by ID. 
- **DO NOT** `/ZREVERT` a mogi that has `/ZREDUCE_LOSS` reduced loss.
### **/ZREDUCE_LOSS** +  `player` & `mogi_id` & `reduction`
- Reduce the loss of 1 player in 1 mogi by a reduction value (must be a fraction, 2/3, 1/2, etc). 
- **DO NOT** `/ZREVERT` a mogi that has `/ZREDUCE_LOSS` reduced loss.
### **/ZSWAPSCORE** +  `player1` & `player2` & `mogi_id` 
- Swaps the score of two players in a specific mogi. 
- Both players must be on the "same team" (the bot detects if they are on the same team if both players have the same placement). Be careful not to swap the scores of players from different teams that are tied.
### **/ZSTRIKE** +  `player_name` & `mmr_penalty` & `reason` 
- Give a player a strike and an mmr penalty. Please provide a brief reason (32 characters)
### **/ZUNSTRIKE** +  `strike_id`
- Undo a strike
### **/ZMMR_PENALTY** + `player_name` & `mmr penalty` 
- Give a player an MMR penalty.

## __🧑‍🦲 PLAYER COMMANDS__
### **/ZRESTRICT** + `player_name` & `reason` & `ban length`
- Give the restricted role to a player. 
- Having this role means that the 200-Lounge bot will immediately delete every message sent.
- The reason & ban length will be DM'd to the offending player, if their Discord settings allow.
### **/ZLOUNGELESS** + `player_name` & `reason` & `ban length`
- Give a player the loungeless role
- The reason & ban length will be DM'd to the offending player, if their Discord settings allow.
### **/ZWARN** + `player_name` & `reason`
- If you warn a player about their behavior, please log it using this command. Doing this allows the staff team to view the data at a later time and equitably take into account all warnings and restrictions when issuing a punishment.
- This does not send a message to the player.
### **/ZGET_PLAYER_PUNISHMENTS** + `player_name` or `discord_id`
- View warnings, restrictions, and loungeless history for a specific player
### **/ZGET_PLAYER_INFO** +  `player_name` or `discord_id`
- Get a specific players' database info
### **/ZADD_MMR** + `player_name` & `mmr`
- Give a player mmr :stonks:
### **/ZSET_PLAYER_NAME** +  `@player` & `name`
- Change a player's name.
### **/ZFIX_PLAYER** +  `player_name`
- Use this to fix someone's roles or nickname
### **/ZSTRIKES** + `player_name`
- View a player's strikes

## __👪 COMMUNITY COMMANDS__
### **/ZDENY_SUGGESTION** + `suggestion_id` & `reason`
- Deny a suggestion
### **/ZAPPROVE_SUGGESTION** + `suggestion_id` & `reason`
- Approve a suggestion

## __⚙️ CONFIGURATION COMMANDS__
### **/ZRELOAD_COGS**
- Reloads the persistent looping functions (~~inactivity checker, mogilist/lu~~, strike checker, ~~mogi media checker~~, unban checker).
- If someone is complaining that the bot didn't unban them at exactly 6:43:05.020 PM you can use this to force an unban check. The bot checks for unbans once every hour. The timer starts when the cogs are loaded.
### **/ZMANUALLY_VERIFY_PLAYER** + `discord_id` & `mkc_id` & `country_code`
- Manually verify a player, but you MUST check for the following:
- Use the numbers in their FORUM link as the mkc_id
- Make sure to enter the proper ISO 3166-1 Alpha-2 Country Code that matches the flag on their registry page. https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
### **/ZCHANGE_DISCORD_ACCOUNT** + `original_discord_id` & `new_discord_id`
- Change the discord account tied to the lounge account
- If the player is sending their mkc link with /verify and getting an error (likely Error 10)
- This means they are trying to verify with someone elses MKC account, or using a different Discord Account.
- Have the user confirm their name in the current leaderboard.
- Use `/zget_player_info` to retrieve the ID's for that player.
- Use `/zchange_discord_account`


# Credits
[Lorenzi Table Maker](https://github.com/hlorenzi/mk8d_ocr) used in the `/table` command

[150cc Lounge API](https://github.com/VikeMK/Lounge-API) used as a secondary verification method in the `/verify` command

[mariokartcentral.com](https://www.mariokartcentral.com/) used in the `/verify` command

Shout out to Lorenzi, Cynda, Vike, and Trom for providing info about their infrastructure.