# import logging
import DBA
from helpers.getters import get_lounge_guild

async def create_queue_channels_and_categories(client, number_of_players, groups_of_12):
    """Creates channels for lounge queue based on # of players"""
    guild = get_lounge_guild(client)
    if guild is None:
        print('create_queue_channels_and_categories error: Guild not found')
        return False
    
    print(f'length of groups: {len(groups_of_12)}')
    print(f'groups: {groups_of_12}')
    return
    
    # handle groups_of_12
    # assign permissions to channel for each user in group
    
    
    # Permissions in rooms will be added for each player on the list + mods + bots   
    # Calculate the number of channels and categories needed
    channels_needed = number_of_players // 12 + (1 if number_of_players % 12 != 0 else 0)
    categories_needed = channels_needed // 25 + (1 if channels_needed % 25 != 0 else 0)
    
    print(f"Creating {channels_needed} channels under {categories_needed} categories.")

    for category_index in range(categories_needed):
        channels_list = []
        # Create a new category
        category_name = f"Rooms {category_index + 1}"
        category = await guild.create_category(category_name)
        category_id = int(category.id)
        print(f"Created category: {category_name}")

        # Calculate the number of channels for this category
        channels_for_this_category = min(channels_needed, 25)
        channels_needed -= channels_for_this_category

        for channel_index in range(channels_for_this_category):
            # Create a new channel in this category
            channel_name = f"Channel {category_index * 25 + channel_index + 1}"
            channel = await guild.create_text_channel(channel_name, category=category)
            channels_list.append(channel.id)
            print(f"Created channel: {channel_name}")
        
        # Insert this category
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO lounge_queue_category (category_id) VALUES (%s)', (category_id,))
        except Exception as e:
            print(f'Exception inserting specific category to lounge_queue_category table: {e}')
            return False
        
        # Insert channels for this category
        channels_tuples = [(channel, category_id) for channel in channels_list]
        try:
            with DBA.DBAccess() as db:
                db.executemany('INSERT INTO lounge_queue_channel (channel_id, category_id) VALUES (%s, %s)', channels_tuples)
        except Exception as e:
            print(f'Exception inserting channels into specific category {category_id}: {e}')
            return False
            
    
    print("Creation complete.")
    return True