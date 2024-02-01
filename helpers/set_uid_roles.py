import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from config import CHAT_RESTRICTED_ROLE_ID
from config import PLACEMENT_ROLE_ID

# Input: int discord user id
# Output Pass: Tuple( int role_id, str role_name )
# Output Fail: False
async def set_uid_roles(client, uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_name, mmr, is_chat_restricted FROM player WHERE player_id = %s;', (uid,))
        player_name = temp[0][0]
        mmr = temp[0][1]
        is_chat_restricted = temp[0][2]
        
        # Get discord.Guild and discord.Member objects
        guild = get_lounge_guild(client)
        member = await guild.fetch_member(uid)
        
        if is_chat_restricted: # Add chat restricted role
            restricted_role = guild.get_role(CHAT_RESTRICTED_ROLE_ID)
            await member.add_roles(restricted_role)
        
        # Outcome #1
        
        if mmr is None: # Add placement role & return
            role = guild.get_role(PLACEMENT_ROLE_ID)
            await member.add_roles(role)
            return (role.id, role)
        
        # Outcome #2
        
        with DBA.DBAccess() as db: # Get ranks info
            ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
            
        for rank in ranks: # Remove any ranks from player
            remove_rank = guild.get_role(rank[0])
            await member.remove_roles(remove_rank)
        
        for i in range(len(ranks)): # Find their rank, based on MMR
            if mmr >= int(ranks[i][1]) and mmr < int(ranks[i][2]):
                # Found your rank
                role = guild.get_role(ranks[i][0])
                await member.add_roles(role)
                with DBA.DBAccess() as db:
                    db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (ranks[i][0], member.id))
                    
        try: # Edit their discord nickname
            await member.edit(nick=str(player_name))
        except Exception as e:
            await send_raw_to_debug_channel(client, f'<@{uid}>', f'CANNOT EDIT NICKNAME OF STAFF MEMBER. I AM BUT A SMOLL ROBOT... {e}')
            pass 
        return (role.id, role)
    except IndexError:
        return False
    except Exception as e:
        await send_raw_to_debug_channel(client, f'<@{uid}>', f'set_uid_roles exception: {e}')
        return False