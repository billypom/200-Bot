import DBA
from helpers.getters import get_lounge_guild
from helpers import delete_discord_channel
from helpers import delete_discord_category

async def delete_queue_channels_and_categories(client):
    guild = get_lounge_guild(client)
    if guild is None:
        print('Guild is none')
        return False
    # Delete channels where is_table_submitted is 1
    select_channels_sql = "SELECT channel_id FROM lounge_queue_channel WHERE is_table_submitted = %s"
    delete_channel_sql = "DELETE FROM lounge_queue_channel WHERE channel_id = %s"
    with DBA.DBAccess() as db:
        eligible_channels = db.query(select_channels_sql, (0,))
        for (channel_id,) in eligible_channels:
            try:
                channel_was_deleted = await delete_discord_channel(client, channel_id)
                if channel_was_deleted:
                    db.execute(delete_channel_sql, (channel_id,))
                    print(f"Deleted channel {channel_id} from Discord and database.")
                else:
                    print(f'Failed to delete channel {channel_id}, returned before database execution')
            except Exception as e:
                print(f"Error deleting channel {channel_id}: {e}")
                return False
    # Delete categories that are now empty
    select_empty_categories_sql = """
    SELECT c.category_id
    FROM lounge_queue_category c
    LEFT JOIN lounge_queue_channel ch ON c.category_id = ch.category_id
    GROUP BY c.category_id
    HAVING COUNT(ch.channel_id) = %s
    """
    delete_category_sql = "DELETE FROM lounge_queue_category WHERE category_id = %s"
    with DBA.DBAccess() as db:
        empty_categories = db.query(select_empty_categories_sql, (0,))
        for (category_id,) in empty_categories:
            try:
                await delete_discord_category(client, category_id)
                db.execute(delete_category_sql, (category_id,))
                print(f"Deleted category {category_id} from Discord and database.")
            except Exception as e:
                print(f"Error deleting category {category_id}: {e}")
                return False
    return True
